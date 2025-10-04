# Amazon Product HTML Scraper

A robust Python scraper that extracts product information from Amazon product HTML files and converts them into structured JSON format.

## Features

- 🔍 **Intelligent HTML Parsing**: Uses BeautifulSoup4 for accurate DOM parsing
- 🛡️ **Fallback Mechanisms**: Includes regex-based extraction when BeautifulSoup fails
- 🤖 **OpenAI Integration**: Optional API enhancement for data cleaning and structuring
- 📊 **Comprehensive Data Extraction**: Product title, rating, reviews, price, variants, specifications, and descriptions
- 🔐 **Secure API Key Management**: Uses `.env` files for secure API key storage
- ⚡ **Command Line Interface**: Easy to use with file paths and options

## Installation

1. **Clone or download the project files**

2. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Set up your API keys** (optional):
   - Copy the `.env` file and add your OpenAI API key:
   ```env
   OPENAI_API_KEY=your_openai_api_key_here
   ```

## Usage

### Basic Usage (HTML parsing only)
```bash
python amazon_scraper.py sample_amazon_listing.html -o output.json
```

### With OpenAI Enhancement
```bash
# Using .env file
python amazon_scraper.py sample_amazon_listing.html -o output.json

# Or provide API key directly
python amazon_scraper.py sample_amazon_listing.html -o output.json --openai-key your_api_key
```

### Command Line Options
- `input_file`: Path to the HTML file to process (required)
- `-o, --output`: Output JSON file path (default: output.json)
- `--openai-key`: OpenAI API key (overrides .env file)

## Output Format

The scraper extracts the following information:

```json
{
  "product_title": "Product name and description",
  "rating": 4.4,
  "total_reviews": 3649,
  "price": 13.99,
  "bought_in_past_month": "9K+",
  "color": "14K-Gold-Plated",
  "variants": {
    "14K-Gold-Plated": 13.99,
    "Rose Gold-Plated": 15.99,
    "White Gold-Plated": 14.99
  },
  "product_details": {
    "Material": "Brass",
    "Metal type": "Brass",
    "Back Finding": "Hinged Hoop",
    "Earring design": "Hoop",
    "Gem type": "No Gemstone"
  },
  "about_this_item": "Detailed product description and features..."
}
```

## Dependencies

### Required
- `beautifulsoup4` - HTML parsing
- `lxml` - XML/HTML parser
- `requests` - HTTP library

### Optional
- `openai` - AI-enhanced text processing
- `python-dotenv` - Environment variable management
- `html5lib` - Enhanced HTML parsing

## Environment Variables

Create a `.env` file in the project directory:

```env
# OpenAI API Key for enhanced text processing
OPENAI_API_KEY=your_openai_api_key_here
```

**Important**: Never commit your `.env` file to version control. It's already included in `.gitignore`.

## Architecture

1. **HTML Parsing Layer**: BeautifulSoup4 with CSS selectors for precise extraction
2. **Regex Fallback**: Pattern-based extraction for resilience
3. **Data Enhancement**: Smart fallback data and optional OpenAI processing
4. **Output Formatting**: Clean JSON structure matching expected format

## Error Handling

The scraper includes comprehensive error handling:
- Graceful degradation when optional packages aren't available
- Fallback extraction methods when primary parsing fails
- Detailed error messages for troubleshooting

## Security

- API keys are stored securely in `.env` files
- `.env` files are excluded from version control
- No sensitive data is logged or exposed

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## License

This project is for educational and research purposes.