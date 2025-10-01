import streamlit as st
import pandas as pd
import re
from urllib.parse import urlparse
from data_handler import DataHandler
from pdf_generator import PDFGenerator
from affiliate_manager import AffiliateManager
import os

# Page configuration
st.set_page_config(
    page_title="Product Catalog - Affiliate Management",
    page_icon="🛍️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better styling
st.markdown("""
<style>
    .main-header {
        background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
        padding: 1rem;
        border-radius: 10px;
        color: white;
        text-align: center;
        margin-bottom: 2rem;
    }
    
    .product-card {
        background: white;
        padding: 1.5rem;
        border-radius: 10px;
        box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        margin-bottom: 1rem;
        border-left: 4px solid #667eea;
    }
    
    .affiliate-panel {
        background: #f8f9fa;
        padding: 1.5rem;
        border-radius: 10px;
        border: 2px solid #e9ecef;
        margin-top: 1rem;
    }
    
    .sidebar-product {
        padding: 0.5rem;
        margin: 0.25rem 0;
        border-radius: 5px;
        cursor: pointer;
        transition: background-color 0.3s;
    }
    
    .sidebar-product:hover {
        background-color: #f0f2f6;
    }
    
    .selected-product {
        background-color: #667eea !important;
        color: white !important;
    }
    
    .image-gallery {
        display: flex;
        flex-wrap: wrap;
        gap: 10px;
        margin: 1rem 0;
    }
    
    .product-image {
        max-width: 200px;
        max-height: 200px;
        border-radius: 8px;
        box-shadow: 0 2px 8px rgba(0,0,0,0.1);
    }
    
    .stats-container {
        display: flex;
        justify-content: space-around;
        margin: 1rem 0;
    }
    
    .stat-box {
        text-align: center;
        padding: 1rem;
        background: #f8f9fa;
        border-radius: 8px;
        min-width: 120px;
    }
</style>
""", unsafe_allow_html=True)

# Initialize session state
if 'selected_product_id' not in st.session_state:
    st.session_state.selected_product_id = None
if 'data_handler' not in st.session_state:
    st.session_state.data_handler = DataHandler()
if 'pdf_generator' not in st.session_state:
    st.session_state.pdf_generator = PDFGenerator()
if 'affiliate_manager' not in st.session_state:
    st.session_state.affiliate_manager = AffiliateManager()

# Load data
@st.cache_data
def load_data():
    return st.session_state.data_handler.load_products()

def clean_html(text):
    """Remove HTML tags from text"""
    if pd.isna(text) or text == "":
        return ""
    # Remove HTML tags
    clean = re.compile('<.*?>')
    return re.sub(clean, '', str(text))

def display_images(image_urls):
    """Display product images in a gallery format"""
    if pd.isna(image_urls) or image_urls == "":
        return
    
    # Split multiple URLs
    urls = [url.strip() for url in str(image_urls).split(',') if url.strip()]
    
    if urls:
        st.markdown('<div class="image-gallery">', unsafe_allow_html=True)
        cols = st.columns(min(len(urls), 4))  # Max 4 images per row
        
        for i, url in enumerate(urls[:8]):  # Limit to 8 images
            with cols[i % 4]:
                try:
                    st.image(url, caption=f"Image {i+1}", use_column_width=True)
                except:
                    st.write(f"🖼️ [Image {i+1}]({url})")
        
        st.markdown('</div>', unsafe_allow_html=True)

def main():
    # Header
    st.markdown("""
    <div class="main-header">
        <h1>🛍️ Product Catalog & Affiliate Management</h1>
        <p>Manage your product catalog and affiliate links with SliceWP integration</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Load products data
    try:
        df = load_data()
        
        if df.empty:
            st.error("No products found in the database.")
            return
            
    except Exception as e:
        st.error(f"Error loading data: {str(e)}")
        return
    
    # Sidebar - Product Navigation
    with st.sidebar:
        st.header("📋 Product Catalog")
        
        # Search functionality
        search_term = st.text_input("🔍 Search Products", placeholder="Enter product name...")
        
        # Filter products based on search
        if search_term:
            filtered_df = df[df['Name'].str.contains(search_term, case=False, na=False)]
        else:
            filtered_df = df
        
        # Display statistics
        st.markdown("### 📊 Statistics")
        col1, col2 = st.columns(2)
        with col1:
            st.metric("Total Products", len(df))
        with col2:
            st.metric("Filtered", len(filtered_df))
        
        # Product list
        st.markdown("### 📦 Products")
        
        # Create a container for the product list
        product_container = st.container()
        
        with product_container:
            for idx, row in filtered_df.iterrows():
                product_name = row['Name'] if pd.notna(row['Name']) else f"Product {row['record_id']}"
                
                # Create clickable product item
                if st.button(
                    f"📦 {product_name[:30]}{'...' if len(str(product_name)) > 30 else ''}",
                    key=f"product_{row['record_id']}",
                    help=product_name,
                    use_container_width=True
                ):
                    st.session_state.selected_product_id = row['record_id']
                    st.rerun()
    
    # Main content area
    if st.session_state.selected_product_id:
        # Get selected product
        selected_product = df[df['record_id'] == st.session_state.selected_product_id].iloc[0]
        
        # Product details section
        st.markdown("## 📦 Product Details")
        
        # Product info in a card
        with st.container():
            st.markdown('<div class="product-card">', unsafe_allow_html=True)
            
            col1, col2 = st.columns([2, 1])
            
            with col1:
                st.markdown(f"### {selected_product['Name'] if pd.notna(selected_product['Name']) else 'Unnamed Product'}")
                
                # Description
                description = clean_html(selected_product['Description'])
                if description:
                    st.markdown("**Description:**")
                    st.write(description[:500] + "..." if len(description) > 500 else description)
                
                # Current URL Slug
                st.markdown("**Current URL Slug:**")
                current_slug = selected_product['URL Slug'] if pd.notna(selected_product['URL Slug']) else ""
                st.code(current_slug if current_slug else "No slug set")
            
            with col2:
                st.markdown("**Product ID:**")
                st.code(selected_product['record_id'])
                
                # Quick actions
                st.markdown("**Quick Actions:**")
                if st.button("📋 Copy Product ID", key="copy_id"):
                    st.success("Product ID copied!")
                
                if st.button("🔗 Copy Current Slug", key="copy_slug"):
                    st.success("Slug copied!")
            
            st.markdown('</div>', unsafe_allow_html=True)
        
        # Images section
        if pd.notna(selected_product['Images']) and selected_product['Images']:
            st.markdown("### 🖼️ Product Images")
            display_images(selected_product['Images'])
        
        # Affiliate management section
        st.markdown("### 🔗 Affiliate Management")
        
        with st.container():
            st.markdown('<div class="affiliate-panel">', unsafe_allow_html=True)
            
            # Current slug display and editing
            col1, col2 = st.columns([2, 1])
            
            with col1:
                st.markdown("**Edit URL Slug:**")
                current_slug = selected_product['URL Slug'] if pd.notna(selected_product['URL Slug']) else ""
                
                # Slug input field
                new_slug = st.text_input(
                    "URL Slug",
                    value=current_slug,
                    key=f"slug_input_{selected_product['record_id']}",
                    help="Enter a URL-friendly slug (lowercase, hyphens only)"
                )
                
                # Auto-suggest button
                if st.button("🔄 Auto-Generate Slug", key="auto_suggest"):
                    suggested_slug = st.session_state.affiliate_manager.suggest_slug(selected_product['Name'])
                    if suggested_slug:
                        st.session_state[f"slug_input_{selected_product['record_id']}"] = suggested_slug
                        st.rerun()
                
                # Validate slug
                if new_slug:
                    is_valid, validation_message = st.session_state.affiliate_manager.validate_slug(new_slug)
                    
                    if is_valid:
                        # Check uniqueness
                        is_unique = st.session_state.affiliate_manager.check_slug_availability(
                            new_slug, selected_product['record_id']
                        )
                        
                        if is_unique:
                            st.success(f"✅ Valid slug: {validation_message}")
                        else:
                            st.warning("⚠️ This slug is already in use by another product")
                    else:
                        st.error(f"❌ {validation_message}")
            
            with col2:
                st.markdown("**Preview URLs:**")
                
                if new_slug and new_slug != "":
                    # Direct URL
                    direct_url = st.session_state.affiliate_manager.generate_affiliate_url(new_slug)
                    st.markdown("**Direct URL:**")
                    st.code(direct_url, language="text")
                    
                    # Affiliate URL example
                    affiliate_url = st.session_state.affiliate_manager.generate_affiliate_url(new_slug, "AFFILIATE_ID")
                    st.markdown("**Affiliate URL:**")
                    st.code(affiliate_url, language="text")
                else:
                    st.info("Enter a slug to see URL preview")
            
            # Action buttons
            st.markdown("---")
            col1, col2, col3 = st.columns(3)
            
            with col1:
                if st.button("💾 Save Slug", key="save_slug", use_container_width=True):
                    if new_slug:
                        is_valid, validation_message = st.session_state.affiliate_manager.validate_slug(new_slug)
                        
                        if is_valid:
                            is_unique = st.session_state.affiliate_manager.check_slug_availability(
                                new_slug, selected_product['record_id']
                            )
                            
                            if is_unique:
                                success = st.session_state.data_handler.update_product_slug(
                                    selected_product['record_id'], new_slug
                                )
                                
                                if success:
                                    st.success("✅ Slug updated successfully!")
                                    st.rerun()
                                else:
                                    st.error("❌ Failed to update slug")
                            else:
                                st.error("❌ Slug already exists")
                        else:
                            st.error(f"❌ {validation_message}")
                    else:
                        st.error("❌ Please enter a slug")
            
            with col2:
                if st.button("🔗 Copy Affiliate URL", key="copy_affiliate", use_container_width=True):
                    if new_slug:
                        affiliate_url = st.session_state.affiliate_manager.generate_affiliate_url(new_slug, "YOUR_AFFILIATE_ID")
                        st.info(f"Affiliate URL template copied: {affiliate_url}")
                    else:
                        st.warning("Please enter a slug first")
            
            with col3:
                if st.button("📋 Integration Code", key="integration_code", use_container_width=True):
                    if new_slug:
                        st.session_state.show_integration_modal = True
                        st.rerun()
                    else:
                        st.warning("Please enter a slug first")
            
            st.markdown('</div>', unsafe_allow_html=True)
        
        # Integration code modal
        if hasattr(st.session_state, 'show_integration_modal') and st.session_state.show_integration_modal:
            st.markdown("### 🔧 SliceWP Integration Code")
            
            integration_code = st.session_state.affiliate_manager.get_slicewp_integration_code(new_slug, "YOUR_AFFILIATE_ID")
            
            if integration_code:
                tab1, tab2, tab3, tab4 = st.tabs(["HTML", "WordPress", "JavaScript", "PHP"])
                
                with tab1:
                    st.code(integration_code['html_link'], language="html")
                
                with tab2:
                    st.code(integration_code['wordpress_shortcode'], language="text")
                
                with tab3:
                    st.code(integration_code['javascript'], language="javascript")
                
                with tab4:
                    st.code(integration_code['php'], language="php")
            
            if st.button("❌ Close", key="close_modal"):
                st.session_state.show_integration_modal = False
                st.rerun()
        
    else:
        # Welcome screen
        st.markdown("## 👋 Welcome to Product Catalog Manager")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.markdown("""
            <div class="stat-box">
                <h3>📦</h3>
                <h4>Browse Products</h4>
                <p>Select a product from the sidebar to view details</p>
            </div>
            """, unsafe_allow_html=True)
        
        with col2:
            st.markdown("""
            <div class="stat-box">
                <h3>🔗</h3>
                <h4>Manage Affiliates</h4>
                <p>Edit URL slugs for SliceWP integration</p>
            </div>
            """, unsafe_allow_html=True)
        
        with col3:
            st.markdown("""
            <div class="stat-box">
                <h3>📄</h3>
                <h4>Export Catalog</h4>
                <p>Generate PDF catalogs for distribution</p>
            </div>
            """, unsafe_allow_html=True)
        
        # Display some general statistics
        st.markdown("### 📊 Catalog Overview")
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("Total Products", len(df))
        
        with col2:
            products_with_images = len(df[df['Images'].notna() & (df['Images'] != "")])
            st.metric("Products with Images", products_with_images)
        
        with col3:
            products_with_slugs = len(df[df['URL Slug'].notna() & (df['URL Slug'] != "")])
            st.metric("Products with Slugs", products_with_slugs)
        
        with col4:
            products_with_descriptions = len(df[df['Description'].notna() & (df['Description'] != "")])
            st.metric("Products with Descriptions", products_with_descriptions)
    
    # Footer with export options and bulk management
    st.markdown("---")
    st.markdown("## 🛠️ Bulk Management & Export Tools")
    
    # Bulk management section
    with st.expander("📊 Slug Analysis & Bulk Operations", expanded=False):
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("### 📈 Slug Analysis")
            if st.button("🔍 Analyze Slugs", use_container_width=True):
                with st.spinner("Analyzing slugs..."):
                    analysis = st.session_state.affiliate_manager.analyze_slug_performance(df)
                    
                    # Display analysis results
                    st.markdown("**Analysis Results:**")
                    
                    metrics_col1, metrics_col2, metrics_col3 = st.columns(3)
                    with metrics_col1:
                        st.metric("Completion Rate", f"{analysis['completion_rate']:.1f}%")
                    with metrics_col2:
                        st.metric("Missing Slugs", analysis['products_without_slugs'])
                    with metrics_col3:
                        st.metric("Invalid Slugs", analysis['invalid_slugs'])
                    
                    if analysis['duplicate_slugs'] > 0:
                        st.warning(f"⚠️ Found {analysis['duplicate_slugs']} duplicate slugs")
                    
                    # Show suggestions
                    if analysis['suggestions']:
                        st.markdown("**Suggested Improvements:**")
                        suggestions_df = pd.DataFrame(analysis['suggestions'])
                        st.dataframe(suggestions_df, use_container_width=True)
        
        with col2:
            st.markdown("### 🔄 Bulk Auto-Generate")
            if st.button("🚀 Auto-Generate Missing Slugs", use_container_width=True):
                with st.spinner("Generating slugs for products without them..."):
                    updates = []
                    
                    for _, product in df.iterrows():
                        current_slug = product.get('URL Slug', '')
                        if pd.isna(current_slug) or current_slug == '':
                            suggested_slug = st.session_state.affiliate_manager.suggest_slug(product.get('Name', ''))
                            if suggested_slug:
                                updates.append({
                                    'record_id': product['record_id'],
                                    'new_slug': suggested_slug
                                })
                    
                    if updates:
                        results = st.session_state.affiliate_manager.bulk_update_slugs(updates)
                        
                        success_count = sum(1 for r in results if r['success'])
                        total_count = len(results)
                        
                        if success_count > 0:
                            st.success(f"✅ Successfully generated {success_count}/{total_count} slugs!")
                            st.rerun()
                        else:
                            st.error("❌ Failed to generate any slugs")
                        
                        # Show detailed results
                        if total_count > success_count:
                            st.markdown("**Failed Updates:**")
                            failed_results = [r for r in results if not r['success']]
                            failed_df = pd.DataFrame(failed_results)
                            st.dataframe(failed_df, use_container_width=True)
                    else:
                        st.info("ℹ️ All products already have slugs!")
    
    # Export options
    st.markdown("### 📤 Export Options")
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        if st.button("📄 PDF Catalog", use_container_width=True):
            with st.spinner("Generating PDF catalog..."):
                try:
                    pdf_path = st.session_state.pdf_generator.generate_catalog(df)
                    st.success("PDF catalog generated!")
                    
                    with open(pdf_path, "rb") as pdf_file:
                        st.download_button(
                            label="⬇️ Download PDF",
                            data=pdf_file.read(),
                            file_name="product_catalog.pdf",
                            mime="application/pdf",
                            use_container_width=True
                        )
                except Exception as e:
                    st.error(f"Error: {str(e)}")
    
    with col2:
        if st.button("📊 Affiliate Report", use_container_width=True):
            with st.spinner("Generating affiliate report..."):
                try:
                    pdf_path = st.session_state.pdf_generator.generate_affiliate_report(df)
                    st.success("Affiliate report generated!")
                    
                    with open(pdf_path, "rb") as pdf_file:
                        st.download_button(
                            label="⬇️ Download Report",
                            data=pdf_file.read(),
                            file_name="affiliate_links_report.pdf",
                            mime="application/pdf",
                            use_container_width=True
                        )
                except Exception as e:
                    st.error(f"Error: {str(e)}")
    
    with col3:
        affiliate_id = st.text_input("Affiliate ID", placeholder="Enter affiliate ID", key="export_affiliate_id")
        if st.button("📋 CSV Export", use_container_width=True):
            affiliate_df = st.session_state.affiliate_manager.generate_affiliate_links_csv(df, affiliate_id)
            if affiliate_df is not None:
                csv_data = affiliate_df.to_csv(index=False)
                st.download_button(
                    label="⬇️ Download CSV",
                    data=csv_data,
                    file_name=f"affiliate_links_{affiliate_id or 'direct'}.csv",
                    mime="text/csv",
                    use_container_width=True
                )
    
    with col4:
        if st.button("⚙️ SliceWP Config", use_container_width=True):
            config = st.session_state.affiliate_manager.export_slicewp_config(df)
            import json
            config_json = json.dumps(config, indent=2)
            st.download_button(
                label="⬇️ Download Config",
                data=config_json,
                file_name="slicewp_config.json",
                mime="application/json",
                use_container_width=True
            )

if __name__ == "__main__":
    main()
