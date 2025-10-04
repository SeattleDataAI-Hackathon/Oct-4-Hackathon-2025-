/**
 * Background script for Amazon Product Data Extractor
 */

// Handle extension installation
chrome.runtime.onInstalled.addListener((details) => {
    console.log('Amazon Product Extractor: Extension installed');
    
    // Set default settings
    chrome.storage.sync.set({
        apiEndpoint: 'http://127.0.0.1:5000'
    });
    
    if (details.reason === 'install') {
        // Open welcome tab
        chrome.tabs.create({
            url: chrome.runtime.getURL('welcome.html')
        });
    }
});

// Handle messages from content script
chrome.runtime.onMessage.addListener((request, sender, sendResponse) => {
    if (request.action === 'extractProduct') {
        console.log('Background: Received extract request', request);
        
        // Forward to content script
        chrome.tabs.sendMessage(sender.tab.id, {
            action: 'startExtraction'
        });
    }
    
    return true; // Keep message channel open
});

// Handle tab updates to detect Amazon pages
chrome.tabs.onUpdated.addListener((tabId, changeInfo, tab) => {
    if (changeInfo.status === 'complete' && tab.url) {
        const isAmazonUrl = /amazon\.(com|co\.uk|de|fr|it|es|ca|co\.jp|in|com\.br|com\.mx|com\.au)/.test(tab.url);
        
        if (isAmazonUrl) {
            console.log('Background: Amazon page detected', tab.url);
            
            // Update badge to indicate active
            chrome.action.setBadgeText({
                tabId: tabId,
                text: '✓'
            });
            
            chrome.action.setBadgeBackgroundColor({
                tabId: tabId,
                color: '#FF9900'
            });
        } else {
            // Clear badge for non-Amazon pages
            chrome.action.setBadgeText({
                tabId: tabId,
                text: ''
            });
        }
    }
});

// Handle storage cleanup (keep only last 100 extractions)
chrome.storage.local.onChanged.addListener((changes, namespace) => {
    if (namespace === 'local') {
        chrome.storage.local.get(null, (items) => {
            const extractionKeys = Object.keys(items).filter(key => key.startsWith('extraction_'));
            
            if (extractionKeys.length > 100) {
                // Sort by timestamp and remove oldest
                extractionKeys.sort();
                const toRemove = extractionKeys.slice(0, extractionKeys.length - 100);
                
                toRemove.forEach(key => {
                    chrome.storage.local.remove(key);
                });
                
                console.log(`Background: Cleaned up ${toRemove.length} old extraction records`);
            }
        });
    }
});