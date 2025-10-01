import pandas as pd
import re
from urllib.parse import urljoin, urlparse
import streamlit as st
from data_handler import DataHandler

class AffiliateManager:
    def __init__(self, base_url="https://entremotivator.com"):
        self.base_url = base_url.rstrip('/')
        self.data_handler = DataHandler()
    
    def generate_affiliate_url(self, product_slug, affiliate_id=None):
        """Generate affiliate URL for SliceWP integration"""
        if not product_slug:
            return None
        
        # Clean the slug
        clean_slug = self.clean_slug(product_slug)
        
        if affiliate_id:
            # SliceWP format: /slicewp_affiliate/{affiliate_id}/{product_slug}
            return f"{self.base_url}/slicewp_affiliate/{affiliate_id}/{clean_slug}/"
        else:
            # Direct product URL
            return f"{self.base_url}/{clean_slug}/"
    
    def clean_slug(self, slug):
        """Clean and validate URL slug"""
        if not slug:
            return ""
        
        # Convert to lowercase and replace spaces with hyphens
        clean_slug = str(slug).lower().strip()
        clean_slug = re.sub(r'\s+', '-', clean_slug)
        
        # Remove special characters except hyphens and alphanumeric
        clean_slug = re.sub(r'[^a-z0-9-]', '', clean_slug)
        
        # Remove multiple consecutive hyphens
        clean_slug = re.sub(r'-+', '-', clean_slug)
        
        # Remove leading/trailing hyphens
        clean_slug = clean_slug.strip('-')
        
        return clean_slug
    
    def validate_slug(self, slug):
        """Validate URL slug format"""
        if not slug:
            return False, "Slug cannot be empty"
        
        # Check length
        if len(slug) < 3:
            return False, "Slug must be at least 3 characters long"
        
        if len(slug) > 100:
            return False, "Slug cannot be longer than 100 characters"
        
        # Check format
        if not re.match(r'^[a-z0-9-]+$', slug):
            return False, "Slug can only contain lowercase letters, numbers, and hyphens"
        
        if slug.startswith('-') or slug.endswith('-'):
            return False, "Slug cannot start or end with a hyphen"
        
        if '--' in slug:
            return False, "Slug cannot contain consecutive hyphens"
        
        # Check for reserved words
        reserved_words = [
            'admin', 'api', 'www', 'mail', 'ftp', 'localhost', 'root',
            'slicewp', 'affiliate', 'wp-admin', 'wp-content', 'wp-includes'
        ]
        
        if slug in reserved_words:
            return False, f"'{slug}' is a reserved word and cannot be used"
        
        return True, "Valid slug"
    
    def check_slug_availability(self, slug, exclude_record_id=None):
        """Check if slug is available (not used by other products)"""
        return self.data_handler.check_slug_uniqueness(slug, exclude_record_id)
    
    def suggest_slug(self, product_name):
        """Suggest a URL slug based on product name"""
        if not product_name or pd.isna(product_name):
            return ""
        
        # Start with the product name
        suggested_slug = self.clean_slug(product_name)
        
        # If the suggested slug is too short, return empty
        if len(suggested_slug) < 3:
            return ""
        
        # Check if it's available
        if self.check_slug_availability(suggested_slug):
            return suggested_slug
        
        # If not available, try adding numbers
        for i in range(2, 100):
            numbered_slug = f"{suggested_slug}-{i}"
            if self.check_slug_availability(numbered_slug):
                return numbered_slug
        
        # If all numbered versions are taken, add timestamp
        from datetime import datetime
        timestamp = datetime.now().strftime("%m%d")
        return f"{suggested_slug}-{timestamp}"
    
    def bulk_update_slugs(self, updates):
        """Update multiple product slugs at once"""
        """
        updates: list of dictionaries with 'record_id' and 'new_slug' keys
        """
        results = []
        
        for update in updates:
            record_id = update.get('record_id')
            new_slug = update.get('new_slug')
            
            if not record_id or not new_slug:
                results.append({
                    'record_id': record_id,
                    'success': False,
                    'error': 'Missing record_id or new_slug'
                })
                continue
            
            # Validate slug
            is_valid, message = self.validate_slug(new_slug)
            if not is_valid:
                results.append({
                    'record_id': record_id,
                    'success': False,
                    'error': f'Invalid slug: {message}'
                })
                continue
            
            # Check availability
            if not self.check_slug_availability(new_slug, record_id):
                results.append({
                    'record_id': record_id,
                    'success': False,
                    'error': 'Slug already exists'
                })
                continue
            
            # Update the slug
            success = self.data_handler.update_product_slug(record_id, new_slug)
            results.append({
                'record_id': record_id,
                'success': success,
                'error': None if success else 'Failed to update database'
            })
        
        return results
    
    def generate_affiliate_links_csv(self, df, affiliate_id=None):
        """Generate CSV file with affiliate links"""
        try:
            # Create a copy of the dataframe
            affiliate_df = df.copy()
            
            # Generate affiliate URLs
            affiliate_df['Affiliate_URL'] = affiliate_df['URL Slug'].apply(
                lambda slug: self.generate_affiliate_url(slug, affiliate_id)
            )
            
            # Add affiliate ID column
            affiliate_df['Affiliate_ID'] = affiliate_id if affiliate_id else 'Direct'
            
            # Select relevant columns
            export_columns = [
                'record_id', 'Name', 'URL Slug', 'Affiliate_ID', 'Affiliate_URL'
            ]
            
            # Filter to only include columns that exist
            available_columns = [col for col in export_columns if col in affiliate_df.columns]
            export_df = affiliate_df[available_columns]
            
            return export_df
            
        except Exception as e:
            st.error(f"Error generating affiliate links CSV: {str(e)}")
            return None
    
    def get_slicewp_integration_code(self, product_slug, affiliate_id=None):
        """Generate SliceWP integration code snippet"""
        affiliate_url = self.generate_affiliate_url(product_slug, affiliate_id)
        
        if not affiliate_url:
            return None
        
        # Generate different code snippets for various use cases
        integration_code = {
            'html_link': f'<a href="{affiliate_url}" target="_blank">View Product</a>',
            'wordpress_shortcode': f'[slicewp_affiliate_link id="{affiliate_id}" url="{product_slug}"]View Product[/slicewp_affiliate_link]',
            'direct_url': affiliate_url,
            'javascript': f'''
// JavaScript redirect
window.location.href = "{affiliate_url}";

// Or for a new window
window.open("{affiliate_url}", "_blank");
''',
            'php': f'''
<?php
// PHP redirect
header("Location: {affiliate_url}");
exit();
?>
'''
        }
        
        return integration_code
    
    def analyze_slug_performance(self, df):
        """Analyze slug completion and suggest improvements"""
        analysis = {
            'total_products': len(df),
            'products_with_slugs': 0,
            'products_without_slugs': 0,
            'duplicate_slugs': 0,
            'invalid_slugs': 0,
            'suggestions': []
        }
        
        slug_counts = {}
        
        for _, product in df.iterrows():
            slug = product.get('URL Slug', '')
            
            if pd.isna(slug) or slug == '':
                analysis['products_without_slugs'] += 1
                # Suggest slug for products without one
                suggested = self.suggest_slug(product.get('Name', ''))
                if suggested:
                    analysis['suggestions'].append({
                        'record_id': product['record_id'],
                        'product_name': product.get('Name', 'Unnamed'),
                        'suggested_slug': suggested,
                        'reason': 'Missing slug'
                    })
            else:
                analysis['products_with_slugs'] += 1
                
                # Check for duplicates
                if slug in slug_counts:
                    slug_counts[slug] += 1
                    if slug_counts[slug] == 2:  # First duplicate
                        analysis['duplicate_slugs'] += 2
                    else:
                        analysis['duplicate_slugs'] += 1
                else:
                    slug_counts[slug] = 1
                
                # Validate slug format
                is_valid, message = self.validate_slug(slug)
                if not is_valid:
                    analysis['invalid_slugs'] += 1
                    suggested = self.suggest_slug(product.get('Name', ''))
                    if suggested:
                        analysis['suggestions'].append({
                            'record_id': product['record_id'],
                            'product_name': product.get('Name', 'Unnamed'),
                            'current_slug': slug,
                            'suggested_slug': suggested,
                            'reason': f'Invalid slug: {message}'
                        })
        
        # Calculate completion rate
        analysis['completion_rate'] = (
            analysis['products_with_slugs'] / analysis['total_products'] * 100
            if analysis['total_products'] > 0 else 0
        )
        
        return analysis
    
    def export_slicewp_config(self, df, base_commission_rate=10):
        """Export configuration for SliceWP plugin"""
        config = {
            'plugin': 'SliceWP',
            'base_url': self.base_url,
            'commission_rate': base_commission_rate,
            'products': []
        }
        
        for _, product in df.iterrows():
            if pd.notna(product.get('URL Slug')) and product['URL Slug']:
                product_config = {
                    'id': product['record_id'],
                    'name': product.get('Name', 'Unnamed Product'),
                    'slug': product['URL Slug'],
                    'direct_url': f"{self.base_url}/{product['URL Slug']}/",
                    'affiliate_url_template': f"{self.base_url}/slicewp_affiliate/{{affiliate_id}}/{product['URL Slug']}/",
                    'commission_rate': base_commission_rate
                }
                config['products'].append(product_config)
        
        return config
