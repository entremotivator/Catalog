import pandas as pd
from reportlab.lib.pagesizes import letter, A4
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Image, Table, TableStyle, PageBreak
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_JUSTIFY
import os
import re
from datetime import datetime
import requests
from io import BytesIO
import streamlit as st

class PDFGenerator:
    def __init__(self, output_dir="./output"):
        self.output_dir = output_dir
        self.ensure_output_dir()
        self.styles = getSampleStyleSheet()
        self.setup_custom_styles()
    
    def ensure_output_dir(self):
        """Ensure output directory exists"""
        if not os.path.exists(self.output_dir):
            os.makedirs(self.output_dir)
    
    def setup_custom_styles(self):
        """Setup custom paragraph styles"""
        # Title style
        self.title_style = ParagraphStyle(
            'CustomTitle',
            parent=self.styles['Heading1'],
            fontSize=24,
            spaceAfter=30,
            alignment=TA_CENTER,
            textColor=colors.HexColor('#2c3e50')
        )
        
        # Subtitle style
        self.subtitle_style = ParagraphStyle(
            'CustomSubtitle',
            parent=self.styles['Heading2'],
            fontSize=18,
            spaceAfter=20,
            alignment=TA_CENTER,
            textColor=colors.HexColor('#34495e')
        )
        
        # Product name style
        self.product_name_style = ParagraphStyle(
            'ProductName',
            parent=self.styles['Heading3'],
            fontSize=16,
            spaceAfter=10,
            textColor=colors.HexColor('#2980b9'),
            leftIndent=0
        )
        
        # Product description style
        self.description_style = ParagraphStyle(
            'ProductDescription',
            parent=self.styles['Normal'],
            fontSize=10,
            spaceAfter=15,
            alignment=TA_JUSTIFY,
            leftIndent=20,
            rightIndent=20
        )
        
        # Info style
        self.info_style = ParagraphStyle(
            'InfoStyle',
            parent=self.styles['Normal'],
            fontSize=9,
            textColor=colors.HexColor('#7f8c8d'),
            leftIndent=20
        )
    
    def clean_html(self, text):
        """Remove HTML tags from text"""
        if pd.isna(text) or text == "":
            return ""
        # Remove HTML tags
        clean = re.compile('<.*?>')
        cleaned_text = re.sub(clean, '', str(text))
        # Replace common HTML entities
        cleaned_text = cleaned_text.replace('&nbsp;', ' ')
        cleaned_text = cleaned_text.replace('&amp;', '&')
        cleaned_text = cleaned_text.replace('&lt;', '<')
        cleaned_text = cleaned_text.replace('&gt;', '>')
        return cleaned_text.strip()
    
    def download_image(self, url, max_size=(200, 200)):
        """Download and resize image from URL"""
        try:
            response = requests.get(url, timeout=10)
            response.raise_for_status()
            
            # Save to temporary file
            temp_path = os.path.join(self.output_dir, f"temp_image_{hash(url)}.jpg")
            
            with open(temp_path, 'wb') as f:
                f.write(response.content)
            
            return temp_path
            
        except Exception as e:
            print(f"Error downloading image {url}: {str(e)}")
            return None
    
    def add_product_to_story(self, story, product, product_number):
        """Add a single product to the PDF story"""
        # Product header with number
        story.append(Paragraph(
            f"Product #{product_number}: {product['Name'] if pd.notna(product['Name']) else 'Unnamed Product'}", 
            self.product_name_style
        ))
        
        # Product ID
        story.append(Paragraph(
            f"<b>Product ID:</b> {product['record_id']}", 
            self.info_style
        ))
        
        # URL Slug
        if pd.notna(product['URL Slug']) and product['URL Slug']:
            story.append(Paragraph(
                f"<b>URL Slug:</b> {product['URL Slug']}", 
                self.info_style
            ))
        
        story.append(Spacer(1, 10))
        
        # Description
        description = self.clean_html(product['Description'])
        if description:
            # Limit description length for PDF
            if len(description) > 500:
                description = description[:500] + "..."
            
            story.append(Paragraph(
                f"<b>Description:</b>", 
                self.info_style
            ))
            story.append(Paragraph(description, self.description_style))
        
        # Images
        if pd.notna(product['Images']) and product['Images']:
            image_urls = [url.strip() for url in str(product['Images']).split(',') if url.strip()]
            
            if image_urls:
                story.append(Paragraph("<b>Product Images:</b>", self.info_style))
                story.append(Spacer(1, 5))
                
                # Create a table for images (max 2 per row)
                image_data = []
                current_row = []
                
                for i, url in enumerate(image_urls[:4]):  # Limit to 4 images per product
                    try:
                        # For PDF, we'll just include the URL as text due to complexity of downloading
                        current_row.append(f"Image {i+1}: {url[:50]}{'...' if len(url) > 50 else ''}")
                        
                        if len(current_row) == 2 or i == len(image_urls) - 1:
                            image_data.append(current_row)
                            current_row = []
                    except:
                        continue
                
                if image_data:
                    image_table = Table(image_data, colWidths=[3*inch, 3*inch])
                    image_table.setStyle(TableStyle([
                        ('FONTSIZE', (0, 0), (-1, -1), 8),
                        ('TEXTCOLOR', (0, 0), (-1, -1), colors.HexColor('#7f8c8d')),
                        ('LEFTPADDING', (0, 0), (-1, -1), 20),
                        ('RIGHTPADDING', (0, 0), (-1, -1), 20),
                        ('TOPPADDING', (0, 0), (-1, -1), 5),
                        ('BOTTOMPADDING', (0, 0), (-1, -1), 5),
                    ]))
                    story.append(image_table)
        
        # Add separator
        story.append(Spacer(1, 20))
        story.append(Paragraph("_" * 80, self.info_style))
        story.append(Spacer(1, 20))
    
    def generate_catalog(self, df):
        """Generate PDF catalog from products dataframe"""
        try:
            # Create filename with timestamp
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"product_catalog_{timestamp}.pdf"
            filepath = os.path.join(self.output_dir, filename)
            
            # Create PDF document
            doc = SimpleDocTemplate(
                filepath,
                pagesize=A4,
                rightMargin=72,
                leftMargin=72,
                topMargin=72,
                bottomMargin=18
            )
            
            # Build the story
            story = []
            
            # Title page
            story.append(Paragraph("Product Catalog", self.title_style))
            story.append(Spacer(1, 20))
            
            story.append(Paragraph(
                f"Generated on {datetime.now().strftime('%B %d, %Y at %I:%M %p')}", 
                self.subtitle_style
            ))
            story.append(Spacer(1, 30))
            
            # Summary statistics
            total_products = len(df)
            products_with_images = len(df[df['Images'].notna() & (df['Images'] != "")])
            products_with_slugs = len(df[df['URL Slug'].notna() & (df['URL Slug'] != "")])
            
            summary_data = [
                ['Total Products', str(total_products)],
                ['Products with Images', str(products_with_images)],
                ['Products with URL Slugs', str(products_with_slugs)],
                ['Completion Rate', f"{(products_with_slugs/total_products*100):.1f}%" if total_products > 0 else "0%"]
            ]
            
            summary_table = Table(summary_data, colWidths=[2.5*inch, 1.5*inch])
            summary_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#3498db')),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 12),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
                ('GRID', (0, 0), (-1, -1), 1, colors.black)
            ]))
            
            story.append(summary_table)
            story.append(PageBreak())
            
            # Add products
            for idx, (_, product) in enumerate(df.iterrows(), 1):
                self.add_product_to_story(story, product, idx)
                
                # Add page break every 3 products
                if idx % 3 == 0 and idx < len(df):
                    story.append(PageBreak())
            
            # Build PDF
            doc.build(story)
            
            return filepath
            
        except Exception as e:
            raise Exception(f"Error generating PDF catalog: {str(e)}")
    
    def generate_affiliate_report(self, df, base_url="https://example.com"):
        """Generate affiliate links report"""
        try:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"affiliate_links_report_{timestamp}.pdf"
            filepath = os.path.join(self.output_dir, filename)
            
            doc = SimpleDocTemplate(
                filepath,
                pagesize=A4,
                rightMargin=72,
                leftMargin=72,
                topMargin=72,
                bottomMargin=18
            )
            
            story = []
            
            # Title
            story.append(Paragraph("Affiliate Links Report", self.title_style))
            story.append(Spacer(1, 20))
            
            story.append(Paragraph(
                f"Generated on {datetime.now().strftime('%B %d, %Y at %I:%M %p')}", 
                self.subtitle_style
            ))
            story.append(Spacer(1, 30))
            
            # Create affiliate links table
            table_data = [['Product Name', 'Product ID', 'URL Slug', 'Affiliate Link']]
            
            for _, product in df.iterrows():
                product_name = product['Name'] if pd.notna(product['Name']) else 'Unnamed Product'
                product_id = str(product['record_id'])
                url_slug = product['URL Slug'] if pd.notna(product['URL Slug']) else 'no-slug'
                affiliate_link = f"{base_url}/{url_slug}"
                
                # Truncate long names for table
                if len(product_name) > 30:
                    product_name = product_name[:27] + "..."
                
                table_data.append([
                    product_name,
                    product_id,
                    url_slug,
                    affiliate_link
                ])
            
            # Create table
            affiliate_table = Table(table_data, colWidths=[2*inch, 1*inch, 1.5*inch, 2.5*inch])
            affiliate_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#2c3e50')),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 10),
                ('FONTSIZE', (0, 1), (-1, -1), 8),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                ('GRID', (0, 0), (-1, -1), 1, colors.black),
                ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#f8f9fa')])
            ]))
            
            story.append(affiliate_table)
            
            # Build PDF
            doc.build(story)
            
            return filepath
            
        except Exception as e:
            raise Exception(f"Error generating affiliate report: {str(e)}")
    
    def cleanup_temp_files(self):
        """Clean up temporary image files"""
        try:
            for filename in os.listdir(self.output_dir):
                if filename.startswith("temp_image_"):
                    os.remove(os.path.join(self.output_dir, filename))
        except Exception as e:
            print(f"Error cleaning up temp files: {str(e)}")
