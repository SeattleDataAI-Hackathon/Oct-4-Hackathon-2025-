# Amazon Product Data Extractor - Setup Guide

## 🚀 Installation

### Step 1: Start the Flask API Server
```bash
cd c:\BellevueHackathon
C:/BellevueHackathon/.venv/Scripts/python.exe flask_app.py
```
The server will start on `http://127.0.0.1:5000`

### Step 2: Install Chrome Extension
1. Open Chrome and navigate to `chrome://extensions/`
2. Enable **"Developer mode"** (toggle in top-right corner)
3. Click **"Load unpacked"**
4. Select the `c:\BellevueHackathon\chrome_extension` folder
5. The extension should appear with a 📊 icon

## 🎯 Usage

### Automatic Detection
1. Navigate to any Amazon product page (e.g., https://amazon.com/dp/B123456789)
2. The extension automatically detects the page
3. A **"📊 Extract Product Data"** button appears (top-right corner)
4. Data auto-extracts if enabled (default: ON)

### Manual Extraction
1. Click the extension icon (📊) in Chrome toolbar
2. Click **"Extract Current Page"** button
3. Status shows in popup: ✅ Success or ❌ Error

### View Results
- Files saved to `c:\BellevueHackathon\out\` folder
- Format: `{product_name}_{timestamp}_original.json` and `{product_name}_{timestamp}_fields.json`
- View recent extractions in extension popup

## ⚙️ Configuration

### Extension Popup Controls
- **Server Status**: Green = Online, Red = Offline  
- **Auto-extract Toggle**: Enable/disable automatic extraction
- **Recent Extractions**: Shows last 5 processed products
- **Extract Button**: Manual extraction for current page

### Supported Amazon Domains
- amazon.com (US)
- amazon.co.uk (UK)  
- amazon.de (Germany)
- amazon.fr (France)
- amazon.it (Italy)
- amazon.es (Spain)
- amazon.ca (Canada)
- amazon.co.jp (Japan)
- amazon.in (India)
- amazon.com.br (Brazil)
- amazon.com.mx (Mexico)
- amazon.com.au (Australia)

## 🔧 API Endpoints

The Flask server provides these endpoints:
- `GET /health` - Server status check
- `POST /process-amazon-page` - Process HTML data
- `GET /list-products` - List all processed products

## 📁 File Structure

```
chrome_extension/
├── manifest.json      # Extension configuration
├── content.js         # Amazon page detection & extraction
├── background.js      # Extension lifecycle management  
├── popup.html         # User interface
├── popup.js           # Popup functionality
├── icon*.png          # Extension icons
└── README.md          # Documentation
```

## 🐛 Troubleshooting

### Extension Not Working
1. Check Flask server is running (`python flask_app.py`)
2. Verify extension is loaded in `chrome://extensions/`
3. Check extension popup shows "Flask server online"
4. Try manual extraction from popup

### No Extract Button Appears
1. Ensure you're on an actual Amazon product page (not search results)
2. Look for URLs containing `/dp/` or `/gp/product/`
3. Refresh the page and wait a few seconds

### Data Not Saving
1. Check Flask server console for errors
2. Verify `out/` folder exists and is writable
3. Check OpenAI API key is properly configured in `.env`

## 🎉 Success Indicators

- ✅ Extension icon shows in Chrome toolbar
- ✅ "📊 Extract Product Data" button appears on Amazon product pages  
- ✅ Popup shows "Flask server online"
- ✅ Files appear in `out/` folder after extraction
- ✅ Recent extractions listed in popup

The system is now ready to automatically detect and extract sustainability data from Amazon product pages!