# Amazon Product Data Extractor

Chrome extension for automatically extracting product sustainability data from Amazon pages.

## Installation

1. Start the Flask API server:
   ```bash
   python flask_app.py
   ```

2. Load the extension in Chrome:
   - Open Chrome and go to `chrome://extensions/`
   - Enable "Developer mode" in the top right
   - Click "Load unpacked" and select the `chrome_extension` folder

## Usage

1. Navigate to any Amazon product page
2. The extension will automatically detect the page and show an "Extract Product Data" button
3. Click the button or wait for auto-extraction (default: enabled)
4. Data will be processed and saved to the `out/` folder

## Features

- ✅ Automatic Amazon product page detection
- ✅ One-click data extraction
- ✅ Auto-extraction on page load (configurable)
- ✅ Real-time Flask server status
- ✅ Recent extractions history
- ✅ Supports all major Amazon domains

## Files Generated

For each product, two JSON files are created:
- `{product_name}_{timestamp}_original.json` - Full product data
- `{product_name}_{timestamp}_fields.json` - Sustainability-focused fields

## API Endpoints

- `GET /health` - Check server status
- `POST /process-amazon-page` - Process product HTML
- `GET /list-products` - List all processed products