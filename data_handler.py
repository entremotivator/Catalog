import pandas as pd
import os
import shutil
from datetime import datetime
import streamlit as st

class DataHandler:
    def __init__(self, data_path="./data/products.csv"):
        self.data_path = data_path
        self.backup_dir = "./data/backups"
        self.ensure_backup_dir()
    
    def ensure_backup_dir(self):
        """Ensure backup directory exists"""
        if not os.path.exists(self.backup_dir):
            os.makedirs(self.backup_dir)
    
    def load_products(self):
        """Load products from CSV file"""
        try:
            if not os.path.exists(self.data_path):
                raise FileNotFoundError(f"Data file not found: {self.data_path}")
            
            # Read CSV with proper encoding handling
            df = pd.read_csv(self.data_path, encoding='utf-8-sig')
            
            # Clean column names (remove BOM and extra spaces)
            df.columns = df.columns.str.strip()
            
            # Ensure required columns exist
            required_columns = ['Description', 'Name', 'URL Slug', 'Images', 'record_id']
            for col in required_columns:
                if col not in df.columns:
                    df[col] = ""
            
            # Convert record_id to string for consistency
            df['record_id'] = df['record_id'].astype(str)
            
            # Remove rows where record_id is empty or NaN
            df = df[df['record_id'].notna() & (df['record_id'] != '') & (df['record_id'] != 'nan')]
            
            return df
            
        except Exception as e:
            st.error(f"Error loading products: {str(e)}")
            return pd.DataFrame()
    
    def save_products(self, df):
        """Save products to CSV file with backup"""
        try:
            # Create backup before saving
            self.create_backup()
            
            # Save the updated dataframe
            df.to_csv(self.data_path, index=False, encoding='utf-8-sig')
            
            return True
            
        except Exception as e:
            st.error(f"Error saving products: {str(e)}")
            return False
    
    def create_backup(self):
        """Create a backup of the current data file"""
        try:
            if os.path.exists(self.data_path):
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                backup_filename = f"products_backup_{timestamp}.csv"
                backup_path = os.path.join(self.backup_dir, backup_filename)
                
                shutil.copy2(self.data_path, backup_path)
                
                # Keep only the last 10 backups
                self.cleanup_old_backups()
                
                return backup_path
        except Exception as e:
            st.warning(f"Could not create backup: {str(e)}")
            return None
    
    def cleanup_old_backups(self, keep_count=10):
        """Remove old backup files, keeping only the most recent ones"""
        try:
            backup_files = []
            for filename in os.listdir(self.backup_dir):
                if filename.startswith("products_backup_") and filename.endswith(".csv"):
                    filepath = os.path.join(self.backup_dir, filename)
                    backup_files.append((filepath, os.path.getctime(filepath)))
            
            # Sort by creation time (newest first)
            backup_files.sort(key=lambda x: x[1], reverse=True)
            
            # Remove old backups
            for filepath, _ in backup_files[keep_count:]:
                os.remove(filepath)
                
        except Exception as e:
            st.warning(f"Could not cleanup old backups: {str(e)}")
    
    def update_product_slug(self, record_id, new_slug):
        """Update a specific product's URL slug"""
        try:
            df = self.load_products()
            
            # Find the product by record_id
            mask = df['record_id'] == str(record_id)
            
            if not mask.any():
                raise ValueError(f"Product with ID {record_id} not found")
            
            # Update the slug
            df.loc[mask, 'URL Slug'] = new_slug
            
            # Save the updated dataframe
            success = self.save_products(df)
            
            if success:
                # Clear the cache to force reload
                st.cache_data.clear()
                return True
            else:
                return False
                
        except Exception as e:
            st.error(f"Error updating product slug: {str(e)}")
            return False
    
    def get_product_by_id(self, record_id):
        """Get a specific product by its record_id"""
        try:
            df = self.load_products()
            mask = df['record_id'] == str(record_id)
            
            if mask.any():
                return df[mask].iloc[0]
            else:
                return None
                
        except Exception as e:
            st.error(f"Error getting product: {str(e)}")
            return None
    
    def get_products_summary(self):
        """Get summary statistics about the products"""
        try:
            df = self.load_products()
            
            summary = {
                'total_products': len(df),
                'products_with_names': len(df[df['Name'].notna() & (df['Name'] != "")]),
                'products_with_descriptions': len(df[df['Description'].notna() & (df['Description'] != "")]),
                'products_with_images': len(df[df['Images'].notna() & (df['Images'] != "")]),
                'products_with_slugs': len(df[df['URL Slug'].notna() & (df['URL Slug'] != "")]),
            }
            
            return summary
            
        except Exception as e:
            st.error(f"Error getting products summary: {str(e)}")
            return {}
    
    def search_products(self, search_term, search_fields=['Name', 'Description']):
        """Search products by term in specified fields"""
        try:
            df = self.load_products()
            
            if not search_term:
                return df
            
            # Create a mask for searching across multiple fields
            mask = pd.Series([False] * len(df))
            
            for field in search_fields:
                if field in df.columns:
                    field_mask = df[field].str.contains(
                        search_term, 
                        case=False, 
                        na=False, 
                        regex=False
                    )
                    mask = mask | field_mask
            
            return df[mask]
            
        except Exception as e:
            st.error(f"Error searching products: {str(e)}")
            return pd.DataFrame()
    
    def validate_slug(self, slug):
        """Validate URL slug format"""
        if not slug:
            return False, "Slug cannot be empty"
        
        # Check for valid URL slug format
        import re
        if not re.match(r'^[a-z0-9-]+$', slug):
            return False, "Slug can only contain lowercase letters, numbers, and hyphens"
        
        if slug.startswith('-') or slug.endswith('-'):
            return False, "Slug cannot start or end with a hyphen"
        
        if '--' in slug:
            return False, "Slug cannot contain consecutive hyphens"
        
        return True, "Valid slug"
    
    def check_slug_uniqueness(self, slug, exclude_record_id=None):
        """Check if a slug is unique across all products"""
        try:
            df = self.load_products()
            
            # Filter out the current product if updating
            if exclude_record_id:
                df = df[df['record_id'] != str(exclude_record_id)]
            
            # Check if slug already exists
            existing_slugs = df['URL Slug'].dropna().str.lower()
            
            return slug.lower() not in existing_slugs.values
            
        except Exception as e:
            st.error(f"Error checking slug uniqueness: {str(e)}")
            return False
