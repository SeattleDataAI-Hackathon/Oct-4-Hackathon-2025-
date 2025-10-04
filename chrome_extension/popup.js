/**
 * Popup script for Amazon Product Data Extractor
 */

class ExtractorPopup {
    constructor() {
        this.API_BASE_URL = 'http://127.0.0.1:5000';
        this.currentProductData = null;
        this.currentSustainabilityReport = null;

        this.init();
    }
    
    async init() {
        await this.checkServerStatus();
        // await this.loadRecentExtractions();
        this.setupEventListeners();
    }
    
    async checkServerStatus() {
        const statusDot = document.getElementById('status-dot');
        const statusText = document.getElementById('status-text');
        const extractBtn = document.getElementById('extract-btn');
        const sustainabilityBtn = document.getElementById('sustainability-btn');
        
        try {
            const response = await fetch(`${this.API_BASE_URL}/health`, {
                method: 'GET',
                timeout: 5000
            });
            
            if (response.ok) {
                statusDot.className = 'status-dot online';
                statusText.textContent = 'Flask server online';
                extractBtn.disabled = false;
                // sustainabilityBtn will be enabled when data is extracted
            } else {
                throw new Error('Server not responding');
            }
        } catch (error) {
            statusDot.className = 'status-dot offline';
            statusText.textContent = 'Flask server offline';
            extractBtn.disabled = true;
            sustainabilityBtn.disabled = true;
        }
    }
    
    async loadRecentExtractions() {
        const data = await chrome.storage.local.get(null);
        const extractions = Object.entries(data)
            .filter(([key, value]) => key.startsWith('extraction_'))
            .sort((a, b) => b[0].localeCompare(a[0])) // Sort by timestamp (newest first)
            .slice(0, 5); // Show only last 5
        
        const extractionsList = document.getElementById('extractions-list');
        
        if (extractions.length === 0) {
            extractionsList.innerHTML = `
                <div style="color: #666; font-size: 12px; text-align: center; padding: 20px;">
                    No extractions yet
                </div>
            `;
            return;
        }
        
        extractionsList.innerHTML = extractions.map(([key, extraction]) => {
            const date = new Date(extraction.timestamp);
            const timeStr = date.toLocaleDateString() + ' ' + date.toLocaleTimeString([], {hour: '2-digit', minute:'2-digit'});
            
            return `
                <div class="extraction-item">
                    <div class="extraction-name">${extraction.productName}</div>
                    <div class="extraction-time">${timeStr}</div>
                </div>
            `;
        }).join('');
    }
    
    setupEventListeners() {
        // Extract button
        document.getElementById('extract-btn').addEventListener('click', async (e) => {
            const btn = e.target;
            btn.disabled = true;
            btn.textContent = 'Extracting...';
            
            try {
                // Get current tab
                const [tab] = await chrome.tabs.query({ active: true, currentWindow: true });
                
                // Check if it's an Amazon page
                if (!tab.url.includes('amazon.')) {
                    throw new Error('Please navigate to an Amazon product page');
                }
                
                // Send message to content script
                const response = await chrome.tabs.sendMessage(tab.id, { action: 'startExtraction' });
                
                // Store the response data for sustainability report
                if (response && response.success) {
                    this.currentProductData = response.data_preview;
                    this.currentSustainabilityReport = response.sustainability_report;
                    
                    // Enable sustainability report button if report was generated
                    const sustainabilityBtn = document.getElementById('sustainability-btn');
                    if (this.currentSustainabilityReport && !this.currentSustainabilityReport.error) {
                        sustainabilityBtn.disabled = false;
                        sustainabilityBtn.textContent = '📋 View Sustainability Report ✅';
                    } else if (this.currentSustainabilityReport && this.currentSustainabilityReport.error) {
                        sustainabilityBtn.disabled = false;
                        sustainabilityBtn.textContent = '📋 View Report (Error)';
                    } else {
                        sustainabilityBtn.disabled = true;
                        sustainabilityBtn.textContent = '📋 No Report Generated';
                    }
                }
                
                btn.textContent = 'Extracted!';
                setTimeout(() => {
                    btn.textContent = 'Extract Current Page';
                    btn.disabled = false;
                }, 2000);
                
                // Refresh recent extractions after a delay
                // setTimeout(() => {
                //     this.loadRecentExtractions();
                // }, 1000);
                
            } catch (error) {
                console.error('Extraction error:', error);
                btn.textContent = 'Error';
                setTimeout(() => {
                    btn.textContent = 'Extract Current Page';
                    btn.disabled = false;
                }, 2000);
            }
        });
        
        // Sustainability report button
        document.getElementById('sustainability-btn').addEventListener('click', (e) => {
            console.log('Sustainability button clicked');
            console.log('Current report data:', this.currentSustainabilityReport);
            this.toggleSustainabilityReport();
        });
        
        // View data folder link
        document.getElementById('view-data-link').addEventListener('click', (e) => {
            e.preventDefault();
            chrome.tabs.create({
                url: 'http://127.0.0.1:5000/list-products'
            });
        });
        
        // Refresh status every 30 seconds
        setInterval(() => {
            this.checkServerStatus();
        }, 30000);
    }
    
    toggleSustainabilityReport() {
        const reportSection = document.getElementById('sustainability-report');
        const reportContent = document.getElementById('report-content');
        const btn = document.getElementById('sustainability-btn');
        
        if (reportSection.style.display === 'none') {
            // Show report and expand popup
            reportSection.style.display = 'block';
            document.body.classList.add('expanded');
            btn.textContent = '📋 Hide Sustainability Report';
            
            if (this.currentSustainabilityReport) {
                if (this.currentSustainabilityReport.error) {
                    reportContent.innerHTML = `
                        <div style="color: #dc3545; text-align: center; padding: 20px;">
                            <strong>⚠️ Report Generation Failed</strong><br>
                            ${this.currentSustainabilityReport.error}
                        </div>
                    `;
                } else {
                    // Format the report content for display (limit length for popup)
                    const content = this.currentSustainabilityReport.content || '';
                    // Display full content as HTML (no truncation)
                    
                    // Extract filename from file_path
                    const fileName = this.currentSustainabilityReport.file_path ? 
                        this.currentSustainabilityReport.file_path.split('/').pop() : '';
                    
                    reportContent.innerHTML = `
                        <div style="margin-bottom: 15px; padding: 10px; background: #e8f5e8; border-radius: 5px;">
                            <strong>🌱 ${this.currentSustainabilityReport.brand}</strong><br>
                            <small>Generated: ${new Date(this.currentSustainabilityReport.generated_at).toLocaleString()}</small>
                        </div>
                        <div style="text-align: left; font-size: 13px; line-height: 1.5;">
                            ${content}
                        </div>
                    `;
                }
            } else {
                reportContent.innerHTML = `
                    <div style="color: #666; text-align: center; padding: 20px;">
                        Extract product data first to generate a sustainability report
                    </div>
                `;
            }
        } else {
            // Hide report and collapse popup
            reportSection.style.display = 'none';
            document.body.classList.remove('expanded');
            const hasReport = this.currentSustainabilityReport && !this.currentSustainabilityReport.error;
            btn.textContent = hasReport ? '📋 View Sustainability Report ✅' : '📋 View Sustainability Report';
        }
    }
}

// Initialize popup when DOM is ready
document.addEventListener('DOMContentLoaded', () => {
    new ExtractorPopup();
});