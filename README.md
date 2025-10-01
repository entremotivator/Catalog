# Product Catalog & Affiliate Management System

A comprehensive Streamlit application for managing product catalogs with SliceWP affiliate integration capabilities.

## 🚀 Live Application

**Access the live application at:** https://8501-irdhm3uumi6ph5vnajfvo-1e6c6f24.manusvm.computer

## 📋 Features

### Core Functionality
- **Product Catalog Display**: Browse 107+ products with detailed information
- **Sidebar Navigation**: Easy product selection and search
- **Affiliate Management**: Edit and manage URL slugs for SliceWP integration
- **PDF Generation**: Export product catalogs and affiliate reports
- **Bulk Operations**: Auto-generate missing slugs and bulk management tools
- **Real-time Validation**: Slug format validation and uniqueness checking

### SliceWP Integration
- **Affiliate URL Generation**: Automatic affiliate link creation
- **Integration Code**: HTML, WordPress, JavaScript, and PHP code snippets
- **Configuration Export**: SliceWP plugin configuration files
- **CSV Export**: Affiliate links with custom affiliate IDs

### Data Management
- **CSV Backend**: Reliable data storage with automatic backups
- **Search & Filter**: Find products quickly by name or description
- **Statistics Dashboard**: Track completion rates and data quality
- **Data Validation**: Ensure data integrity and consistency

## 🛠️ Technical Stack

- **Frontend**: Streamlit with custom CSS styling
- **Data Processing**: Pandas for CSV management
- **PDF Generation**: ReportLab for document creation
- **Backend**: Python with modular architecture
- **Deployment**: Live on public URL with port exposure

## 📁 Project Structure

```
streamlit_catalog/
├── app.py                 # Main Streamlit application
├── data_handler.py        # CSV data management module
├── pdf_generator.py       # PDF generation functionality
├── affiliate_manager.py   # SliceWP affiliate management
├── requirements.txt       # Python dependencies
├── README.md             # This documentation
├── test_results.md       # Testing results and verification
└── data/
    ├── products.csv      # Product database (107 products)
    └── backups/          # Automatic data backups
```

## 🚀 Getting Started

### Prerequisites
- Python 3.11+
- Streamlit
- Pandas
- ReportLab
- Requests

### Installation
1. Clone or download the project files
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Run the application:
   ```bash
   streamlit run app.py
   ```

### Data Setup
- Place your product CSV file in the `data/` directory
- Ensure CSV has columns: Description, Name, URL Slug, Images, record_id
- The application will automatically create backups

## 📊 Usage Guide

### Product Management
1. **Browse Products**: Use the sidebar to navigate through all products
2. **Search**: Use the search box to find specific products
3. **View Details**: Click on any product to see full details and images

### Affiliate Management
1. **Edit Slugs**: Select a product and modify its URL slug
2. **Validate**: Real-time validation ensures proper slug format
3. **Preview URLs**: See direct and affiliate URL previews
4. **Save Changes**: Update slugs with automatic backup creation

### Bulk Operations
1. **Analyze Slugs**: Get completion rates and identify issues
2. **Auto-Generate**: Automatically create missing slugs
3. **Bulk Export**: Export affiliate links for multiple products

### Export Options
1. **PDF Catalog**: Generate comprehensive product catalog
2. **Affiliate Report**: Create affiliate links report
3. **CSV Export**: Export data with affiliate URLs
4. **SliceWP Config**: Generate plugin configuration files

## 🔧 SliceWP Integration

### Affiliate URL Format
- **Direct URL**: `https://entremotivator.com/{slug}/`
- **Affiliate URL**: `https://entremotivator.com/slicewp_affiliate/{affiliate_id}/{slug}/`

### Integration Methods
1. **HTML Links**: Direct HTML anchor tags
2. **WordPress Shortcodes**: SliceWP plugin shortcodes
3. **JavaScript**: Programmatic redirects
4. **PHP**: Server-side redirects

### Configuration
- Base URL: `https://entremotivator.com`
- Affiliate path: `/slicewp_affiliate/{affiliate_id}/`
- Slug validation: Lowercase, hyphens, alphanumeric only

## 📈 Statistics & Analytics

The application provides comprehensive analytics:
- **Total Products**: 107 products loaded
- **Products with Images**: 63 (58.9%)
- **Products with Slugs**: 100 (93.5%)
- **Products with Descriptions**: 84 (78.5%)

## 🔒 Data Security

- **Automatic Backups**: Every save creates a timestamped backup
- **Data Validation**: Input validation prevents data corruption
- **Error Handling**: Graceful error handling with user feedback
- **Backup Cleanup**: Maintains last 10 backups automatically

## 🎨 User Interface

- **Modern Design**: Clean, professional interface with gradient headers
- **Responsive Layout**: Works on desktop and mobile devices
- **Interactive Elements**: Hover states and smooth transitions
- **Color-coded Status**: Visual feedback for validation and actions

## 🚀 Deployment

The application is currently deployed and accessible at:
**https://8501-irdhm3uumi6ph5vnajfvo-1e6c6f24.manusvm.computer**

### Deployment Features
- **Public Access**: No authentication required
- **Real-time Updates**: Changes reflect immediately
- **Persistent Data**: CSV data persists between sessions
- **Scalable**: Can handle multiple concurrent users

## 📝 API Integration

The affiliate manager supports various integration methods:

### WordPress Integration
```php
[slicewp_affiliate_link id="AFFILIATE_ID" url="product-slug"]View Product[/slicewp_affiliate_link]
```

### JavaScript Integration
```javascript
window.location.href = "https://entremotivator.com/slicewp_affiliate/AFFILIATE_ID/product-slug/";
```

### HTML Integration
```html
<a href="https://entremotivator.com/slicewp_affiliate/AFFILIATE_ID/product-slug/" target="_blank">View Product</a>
```

## 🔄 Maintenance

### Regular Tasks
- Monitor backup directory size
- Review slug completion rates
- Update product information as needed
- Export reports for affiliate tracking

### Troubleshooting
- Check CSV file format if products don't load
- Verify slug uniqueness if validation fails
- Review backup files if data recovery is needed

## 📞 Support

For technical support or feature requests:
1. Check the test results in `test_results.md`
2. Review error messages in the application
3. Verify CSV file format and data integrity
4. Contact system administrator for deployment issues

## 🎯 Future Enhancements

Potential improvements for future versions:
- Database backend integration
- User authentication and roles
- Advanced analytics dashboard
- API endpoints for external integration
- Automated affiliate performance tracking
- Multi-language support
- Advanced search and filtering options

---

**Version**: 1.0.0  
**Last Updated**: October 1, 2025  
**Status**: Production Ready ✅
