/**
 * Content script for Amazon Product Data Extractor
 * Detects Amazon product pages and extracts HTML for processing
 */

class AmazonProductDetector {
    constructor() {
        this.API_BASE_URL = 'http://127.0.0.1:5000';
        this.isProcessing = false;
        this.lastProcessedUrl = null;
        
        this.init();
    }
    
    init() {
        console.log('Amazon Product Extractor: Content script loaded');
        
        // Check if this is a product page
        if (this.isAmazonProductPage()) {
            console.log('Amazon Product Extractor: Product page detected');
            // Button functionality disabled - extraction only available through popup
            
            // Automatic extraction disabled - users must click the button manually
        }
    }
    
    isAmazonProductPage() {
        // Check URL patterns that indicate a product page
        const url = window.location.href;
        const productPagePatterns = [
            /\/dp\/[A-Z0-9]{10}/,  // Standard product page
            /\/gp\/product\/[A-Z0-9]{10}/,  // Alternative product page
            /\/product\/[A-Z0-9]{10}/  // Another variant
        ];
        
        const isProductPage = productPagePatterns.some(pattern => pattern.test(url));
        
        // Additional check for product elements
        const hasProductElements = !!(
            document.querySelector('#productTitle') ||
            document.querySelector('[data-asin]') ||
            document.querySelector('#dp-container') ||
            document.querySelector('.s-product-container')
        );
        
        return isProductPage && hasProductElements;
    }
    
    async extractProductData() {
        if (this.isProcessing) {
            console.log('Amazon Product Extractor: Already processing');
            return null;
        }
        
        this.isProcessing = true;
        
        try {
            console.log('Amazon Product Extractor: Starting extraction...');
            
            // Get the HTML content
            const htmlContent = document.documentElement.outerHTML;
            const currentUrl = window.location.href;
            const timestamp = new Date().toISOString();
            
            // Send to Flask API with sustainability report generation enabled
            const response = await fetch(`${this.API_BASE_URL}/process-amazon-page`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    html: htmlContent,
                    url: currentUrl,
                    timestamp: timestamp,
                    generate_sustainability_report: true
                })
            });
            
            if (!response.ok) {
                throw new Error(`HTTP ${response.status}: ${response.statusText}`);
            }
            
            const result = await response.json();
            
            if (result.success) {
                console.log('Amazon Product Extractor: Success!', result);
                this.lastProcessedUrl = currentUrl;
                
                // Show notification
                let message = `Product data extracted: ${result.product_name}`;
                if (result.sustainability_report && !result.sustainability_report.error) {
                    message += ' + Sustainability Report';
                }
                this.showNotification('success', message);
                
                // Store extraction info
                chrome.storage.local.set({
                    [`extraction_${Date.now()}`]: {
                        url: currentUrl,
                        productName: result.product_name,
                        timestamp: timestamp,
                        files: result.files_created,
                        sustainabilityReport: result.sustainability_report
                    }
                });
                
                return result; // Return the result for popup use
                
            } else {
                throw new Error(result.error || 'Unknown error occurred');
            }
        } catch (error) {
            console.error('Amazon Product Extractor: Error:', error);
            this.showNotification('error', `Extraction failed: ${error.message}`);
            return { success: false, error: error.message };
        } finally {
            this.isProcessing = false;
        }
    }
    
    showNotification(type, message) {
        // Create notification element
        const notification = document.createElement('div');
        notification.style.cssText = `
            position: fixed;
            top: 80px;
            right: 20px;
            z-index: 10001;
            background: ${type === 'success' ? '#d4edda' : '#f8d7da'};
            color: ${type === 'success' ? '#155724' : '#721c24'};
            border: 1px solid ${type === 'success' ? '#c3e6cb' : '#f5c6cb'};
            padding: 10px 15px;
            border-radius: 5px;
            font-size: 14px;
            max-width: 1000px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.2);
            animation: slideIn 0.3s ease;
        `;
        
        notification.innerHTML = `
            <strong>${type === 'success' ? 'Success!' : 'Error!'}</strong><br>
            ${message}
        `;
        
        // Add animation styles
        const style = document.createElement('style');
        style.textContent = `
            @keyframes slideIn {
                from { transform: translateX(100%); opacity: 0; }
                to { transform: translateX(0); opacity: 1; }
            }
        `;
        document.head.appendChild(style);
        
        document.body.appendChild(notification);
        
        // Remove after 5 seconds
        setTimeout(() => {
            if (notification.parentNode) {
                notification.remove();
            }
        }, 5000);
    }
}

// Message listener for popup communication
chrome.runtime.onMessage.addListener((request, sender, sendResponse) => {
    if (request.action === 'startExtraction') {
        const detector = new AmazonProductDetector();
        detector.extractProductData().then(result => {
            sendResponse(result);
        }).catch(error => {
            sendResponse({ success: false, error: error.message });
        });
        return true; // Will respond asynchronously
    }
});

// Initialize the detector when the page loads
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', () => {
        new AmazonProductDetector();
    });
} else {
    new AmazonProductDetector();
}

// Handle navigation changes (for single-page app behavior)
let lastUrl = location.href;
new MutationObserver(() => {
    const url = location.href;
    if (url !== lastUrl) {
        lastUrl = url;
        setTimeout(() => {
            new AmazonProductDetector();
        }, 1000);
    }
}).observe(document, { subtree: true, childList: true });