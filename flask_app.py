#!/usr/bin/env python3
"""
Flask API server for processing Amazon product HTML data from Chrome extension.
Receives HTML content, processes it using the Amazon scraper, and stores results.
"""

import os
import json
from datetime import datetime
from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
from amazon_scraper import AmazonProductScraper
import tempfile

app = Flask(__name__)
CORS(app)  # Enable CORS for Chrome extension

def generate_sustainability_report_content(brand: str, product_data: dict) -> dict:
    """Generate sustainability report content using OpenAI."""
    try:
        import openai
        from dotenv import load_dotenv
        
        load_dotenv()
        openai_api_key = os.getenv('OPENAI_API_KEY')
        
        if not openai_api_key:
            raise Exception("OpenAI API key not found")
        
        client = openai.OpenAI(api_key=openai_api_key)
        
        # Read the template file
        try:
            with open('template.html', 'r', encoding='utf-8') as template_file:
                html_template = template_file.read()
        except Exception as e:
            raise Exception(f"Failed to read template.html: {str(e)}")
        
        # Create comprehensive prompt for sustainability research
        prompt = f"""
        You are a sustainability expert conducting a concise assessment of {brand}. 
        
        Product Information:
        {json.dumps(product_data, indent=2)}
        
        Create a CONCISE sustainability report for {brand} using the following HTML template structure:

        {html_template}
        
        CRITICAL REQUIREMENTS:
        1. Replace all placeholder content (like "X/10", "Brief explanation", etc.) with actual data
        2. Keep each section BRIEF (1-3 sentences max per point)
        3. ALL sources must be formatted as: <a href="actual_URL" target="_blank">Source Name</a>
        4. Use REAL URLs from your research (not placeholder URLs)
        5. Focus on the most important findings only
        6. Return ONLY the HTML content following the template structure (no markdown formatting)
        7. Ensure all HTML tags are properly closed
        8. Look for recent news, NGO reports, lawsuits, and independent studies
        9. Replace "SCORE HERE" with an actual numerical score (X/10)
        
        Research external sources from: ProPublica, Reuters, Business Insider, NGOs, ESG rating agencies, academic studies, regulatory filings.
        """
        
        response = client.chat.completions.create(
            model="gpt-4",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=4000,
            temperature=0.7
        )
        
        return {
            'report_text': response.choices[0].message.content,
            'brand': brand,
            'generated_at': datetime.now().isoformat(),
            'model_used': 'gpt-4'
        }
        
    except Exception as e:
        raise Exception(f"Failed to generate sustainability report: {str(e)}")

def save_sustainability_report_html(report_content: dict, file_path: str) -> None:
    """Save sustainability report as formatted HTML file."""
    html_document = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Sustainability Report - {report_content['brand']}</title>
    <style>
        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            line-height: 1.6;
            color: #333;
            max-width: 1200px;
            margin: 0 auto;
            padding: 20px;
            background-color: #f8f9fa;
        }}
        .header {{
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 30px;
            border-radius: 10px;
            margin-bottom: 30px;
        }}
        .report-content {{
            background: white;
            padding: 30px;
            border-radius: 10px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
            font-size: 16px;
        }}
        .metadata {{
            background: #e9ecef;
            padding: 15px;
            border-radius: 5px;
            margin-bottom: 20px;
            font-size: 14px;
            color: #6c757d;
        }}
        h1 {{ margin-top: 0; }}
        h2 {{ color: #495057; border-bottom: 2px solid #dee2e6; padding-bottom: 10px; }}
        h3 {{ color: #6c757d; }}
        table {{ margin: 20px 0; }}
        th, td {{ padding: 8px; text-align: left; }}
        th {{ background-color: #f8f9fa; }}
    </style>
</head>
<body>
    <div class="header">
        <h1>Sustainability Assessment Report</h1>
        <h2>{report_content['brand']}</h2>
        <p>Generated: {report_content['generated_at']}</p>
    </div>
    
    <div class="metadata">
        <strong>Report Details:</strong><br>
        Brand: {report_content['brand']}<br>
        Generated: {report_content['generated_at']}<br>
        Model: {report_content['model_used']}<br>
        Type: Comprehensive Sustainability Analysis with External Sources
    </div>
    
    <div class="report-content">
{report_content['report_text']}
    </div>
</body>
</html>"""
    
    try:
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(html_document)
    except Exception as e:
        raise Exception(f"Failed to save report HTML: {str(e)}")

# Initialize scraper with error handling
try:
    scraper = AmazonProductScraper()
    print("✅ Scraper initialized successfully")
except Exception as e:
    print(f"❌ Error initializing scraper: {e}")
    scraper = None

@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint."""
    return jsonify({'status': 'healthy', 'service': 'Amazon Product Scraper API'})

@app.route('/process-amazon-page', methods=['POST'])
def process_amazon_page():
    """
    Process Amazon product page HTML and extract product data.
    Now also generates sustainability report automatically.
    
    Expected POST data:
    {
        "html": "<html content>",
        "url": "amazon product URL",
        "timestamp": "ISO timestamp",
        "generate_sustainability_report": true/false (optional, defaults to true)
    }
    """
    try:
        if not scraper:
            return jsonify({'error': 'Scraper not initialized'}), 500
            
        # Validate request data
        if not request.is_json:
            return jsonify({'error': 'Request must be JSON'}), 400
        
        data = request.get_json()
        html_content = data.get('html')
        url = data.get('url', '')
        timestamp = data.get('timestamp', datetime.now().isoformat())
        generate_report = data.get('generate_sustainability_report', True)
        
        if not html_content:
            return jsonify({'error': 'HTML content is required'}), 400
        
        print(f"Received request to process Amazon page: {url[:100]}...")
        
        # Create temporary HTML file for processing
        with tempfile.NamedTemporaryFile(mode='w', suffix='.html', delete=False, encoding='utf-8') as temp_file:
            temp_file.write(html_content)
            temp_html_path = temp_file.name
        
        try:
            # Process with our scraper
            result_data = scraper.scrape_product(temp_html_path)
            
            # Generate filename using product name and ASIN (same as scraper)
            base_filename = scraper.generate_safe_filename(result_data['original_format'])
            
            # Ensure out directory exists
            os.makedirs('out', exist_ok=True)
            
            # Generate output filenames
            original_output = f"out/{base_filename}_original.json"
            fields_output = f"out/{base_filename}_fields.json"
            
            # Save both formats
            scraper.save_to_json(result_data['original_format'], original_output)
            scraper.save_to_json(result_data['fields_format'], fields_output)
            
            # Get original data for response
            original_data = result_data.get('original_format', {})
            fields_data = result_data.get('fields_format', {})
            
            # Initialize sustainability report data
            sustainability_report = None
            
            # Generate sustainability report if requested
            if generate_report:
                try:
                    brand = fields_data.get('brand')
                    asin = fields_data.get('asin', '')
                    
                    if brand:
                        print(f"Generating sustainability report for brand: {brand}, ASIN: {asin}")
                        
                        # Generate sustainability report using OpenAI
                        report_content = generate_sustainability_report_content(brand, fields_data)
                        
                        # Ensure reports directory exists
                        os.makedirs('reports', exist_ok=True)
                        
                        # Generate filename using brand and ASIN
                        safe_brand = scraper.generate_safe_filename({'product_title': brand})
                        report_filename = f"sustainability_report_{safe_brand}_{asin}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.html"
                        report_path = f"reports/{report_filename}"
                        
                        # Save report to HTML file
                        save_sustainability_report_html(report_content, report_path)
                        
                        # Prepare sustainability report data for Chrome extension
                        sustainability_report = {
                            'brand': brand,
                            'asin': asin,
                            'generated_at': report_content['generated_at'],
                            'model_used': report_content['model_used'],
                            'file_path': report_path,
                            'content': report_content['report_text'],
                            'success': True
                        }
                        
                        print(f"Sustainability report saved: {report_path}")
                    else:
                        print("No brand found for sustainability report generation")
                        sustainability_report = {
                            'error': 'No brand information found for sustainability report generation',
                            'success': False
                        }
                        
                except Exception as report_error:
                    print(f"Error generating sustainability report: {str(report_error)}")
                    sustainability_report = {
                        'error': f'Report generation failed: {str(report_error)}',
                        'success': False
                    }
            
            # Prepare response
            response_data = {
                'success': True,
                'message': 'Product data extracted successfully',
                'product_name': base_filename,
                'files_created': {
                    'original': original_output,
                    'fields': fields_output
                },
                'data_preview': {
                    'product_title': original_data.get('product_title', '')[:100] + '...' if len(original_data.get('product_title', '')) > 100 else original_data.get('product_title', ''),
                    'rating': original_data.get('rating'),
                    'price': original_data.get('price'),
                    'brand': fields_data.get('brand'),
                    'materials': fields_data.get('materials'),
                    'asin': fields_data.get('asin'),
                    'sustainability_feature_score': fields_data.get('sustainability_feature_score')
                },
                'processed_at': timestamp,
                'url': url,
                'sustainability_report': sustainability_report
            }
            
            print(f"Successfully processed: {base_filename}")
            print(f"Files saved: {original_output}, {fields_output}")
            
            return jsonify(response_data)
            
        finally:
            # Clean up temporary file
            try:
                os.unlink(temp_html_path)
            except:
                pass
                
    except Exception as e:
        print(f"Error processing Amazon page: {str(e)}")
        return jsonify({
            'success': False,
            'error': f'Processing failed: {str(e)}'
        }), 500

@app.route('/reports/<filename>')
def serve_report(filename):
    """Serve sustainability reports."""
    try:
        return send_from_directory('reports', filename)
    except Exception as e:
        return jsonify({'error': f'Report not found: {str(e)}'}), 404

@app.route('/list-products', methods=['GET'])
def list_products():
    """List all processed products in the out/ directory."""
    try:
        if not os.path.exists('out'):
            return jsonify({'products': []})
        
        files = os.listdir('out')
        products = {}
        
        for file in files:
            if file.endswith('_original.json'):
                base_name = file.replace('_original.json', '')
                if base_name not in products:
                    products[base_name] = {}
                products[base_name]['original'] = file
                
            elif file.endswith('_fields.json'):
                base_name = file.replace('_fields.json', '')
                if base_name not in products:
                    products[base_name] = {}
                products[base_name]['fields'] = file
        
        return jsonify({'products': products})
        
    except Exception as e:
        return jsonify({'error': f'Failed to list products: {str(e)}'}), 500

if __name__ == '__main__':
    print("Starting Amazon Product Scraper API...")
    print("Endpoints:")
    print("  GET  /health - Health check")
    print("  POST /process-amazon-page - Process Amazon HTML")
    print("  GET  /list-products - List processed products")
    print("")
    app.run(debug=True, host='127.0.0.1', port=5000)