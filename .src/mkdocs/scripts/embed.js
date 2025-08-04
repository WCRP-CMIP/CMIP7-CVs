/**
 * Embed.js - Complete embedded view system
 * Only floating button in bottom-right corner
 * 
 * USAGE:
 * 1. Add ?embed=true to any page URL for embed mode
 * 2. Click floating expand button (⤢) in bottom-right corner  
 * 3. Use F11 or ESC keyboard shortcuts
 */

document.addEventListener('DOMContentLoaded', function() {
    console.log('Embed.js v3 loaded and initializing...');
    
    // Check for embed parameter in URL
    const urlParams = new URLSearchParams(window.location.search);
    const embedMode = urlParams.get('embed') === 'true' || urlParams.get('fullscreen') === 'true';
    
    console.log('Embed mode:', embedMode);
    
    // Add floating expand button to all pages
    addFloatingExpandButton();
    
    // Add keyboard shortcuts
    addKeyboardShortcuts();
    
    // Auto-enter embed mode if parameter is present
    if (embedMode) {
        setTimeout(() => {
            enterEmbedMode();
        }, 500);
    }
});

/**
 * Add floating expand button (bottom-right corner, always visible)
 */
function addFloatingExpandButton() {
    // Remove any old buttons first
    const oldButtons = document.querySelectorAll('.minimize-maximize-btn, .page-maximize-btn, .fullscreen-btn');
    oldButtons.forEach(btn => {
        console.log('Removing old button:', btn.className);
        btn.remove();
    });
    
    // Only add if not already present
    if (document.querySelector('.floating-expand-btn')) {
        return;
    }
    
    console.log('Adding floating expand button...');
    
    const button = document.createElement('button');
    button.className = 'floating-expand-btn';
    button.innerHTML = '⤢'; // Two arrows expanding
    button.title = 'Toggle Fullscreen (F11)';
    button.setAttribute('aria-label', 'Toggle fullscreen');
    
    // Style the button directly to ensure it appears
    button.style.cssText = `
        position: fixed !important;
        bottom: 80px !important;
        right: 20px !important;
        width: 50px !important;
        height: 50px !important;
        background: var(--md-primary-fg-color, #1976d2) !important;
        color: white !important;
        border: none !important;
        border-radius: 50% !important;
        font-size: 1.5rem !important;
        cursor: pointer !important;
        z-index: 1000 !important;
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.3) !important;
        transition: all 0.3s ease !important;
        display: flex !important;
        align-items: center !important;
        justify-content: center !important;
    `;
    
    // Add to body
    document.body.appendChild(button);
    
    // Add click handler
    button.addEventListener('click', () => {
        if (document.body.classList.contains('embed-mode')) {
            exitEmbedMode();
        } else {
            enterEmbedMode();
        }
    });
    
    console.log('Floating expand button added');
}



/**
 * Enter embed mode
 */
function enterEmbedMode() {
    console.log('Entering embed mode');
    
    // Remove any lingering old buttons
    const oldButtons = document.querySelectorAll('.minimize-maximize-btn, .page-maximize-btn, .fullscreen-btn');
    oldButtons.forEach(btn => {
        console.log('Cleaning up old button in embed mode:', btn.className);
        btn.remove();
    });
    
    // Add embed-mode class to body
    document.body.classList.add('embed-mode');
    
    // Hide all MkDocs navigation and chrome
    const elementsToHide = [
        '.md-header', '.md-tabs', '.md-footer', '.md-sidebar',
        '.md-sidebar--primary', '.md-sidebar--secondary', '.md-nav', '.md-search'
    ];
    
    elementsToHide.forEach(selector => {
        const elements = document.querySelectorAll(selector);
        elements.forEach(el => {
            el.style.display = 'none';
            el.style.visibility = 'hidden';
        });
    });
    
    // Adjust content to fill viewport
    const container = document.querySelector('.md-container');
    const main = document.querySelector('.md-main');
    const content = document.querySelector('.md-content');
    
    if (container) {
        container.style.cssText = 'max-width: none !important; margin: 0 !important; padding: 0 !important; width: 100% !important;';
    }
    if (main) {
        main.style.cssText = 'max-width: none !important; margin: 0 !important; padding: 0 !important; width: 100% !important;';
    }
    if (content) {
        content.style.cssText = 'max-width: none !important; margin: 0 !important; padding: 1rem !important; width: 100% !important; min-height: 100vh !important;';
    }
    
    // Convert floating button to close button (top of screen, small and slick)
    const floatingBtn = document.querySelector('.floating-expand-btn');
    if (floatingBtn) {
        floatingBtn.innerHTML = '×'; // Clear × close symbol
        floatingBtn.title = 'Close (ESC)';
        floatingBtn.setAttribute('aria-label', 'Close fullscreen');
        
        // Move to top and make small and slick
        floatingBtn.style.cssText = `
            position: fixed !important;
            top: 15px !important;
            right: 15px !important;
            width: 32px !important;
            height: 32px !important;
            background: rgba(0, 0, 0, 0.7) !important;
            color: white !important;
            border: none !important;
            border-radius: 0.25rem !important;
            font-size: 16px !important;
            font-weight: bold !important;
            cursor: pointer !important;
            z-index: 10000 !important;
            box-shadow: 0 2px 8px rgba(0, 0, 0, 0.4) !important;
            transition: all 0.2s ease !important;
            display: flex !important;
            align-items: center !important;
            justify-content: center !important;
        `;
    }
    
    console.log('Embed mode activated');
}

/**
 * Exit embed mode
 */
function exitEmbedMode() {
    console.log('Exiting embed mode');
    
    // Remove embed-mode class from body
    document.body.classList.remove('embed-mode');
    
    // Show all MkDocs navigation and chrome
    const elementsToShow = [
        '.md-header', '.md-tabs', '.md-footer', '.md-sidebar',
        '.md-sidebar--primary', '.md-sidebar--secondary', '.md-nav', '.md-search'
    ];
    
    elementsToShow.forEach(selector => {
        const elements = document.querySelectorAll(selector);
        elements.forEach(el => {
            el.style.display = '';
            el.style.visibility = '';
        });
    });
    
    // Reset content styling
    const container = document.querySelector('.md-container');
    const main = document.querySelector('.md-main');
    const content = document.querySelector('.md-content');
    
    if (container) {
        container.style.cssText = '';
    }
    if (main) {
        main.style.cssText = '';
    }
    if (content) {
        content.style.cssText = '';
    }
    
    // Convert close button back to floating expand button (bottom-right, round)
    const floatingBtn = document.querySelector('.floating-expand-btn');
    if (floatingBtn) {
        floatingBtn.innerHTML = '⤢'; // Expand symbol
        floatingBtn.title = 'Toggle Fullscreen (F11)';
        floatingBtn.setAttribute('aria-label', 'Toggle fullscreen');
        
        // Reset to original floating button style (moved up to avoid footer)
        floatingBtn.style.cssText = `
            position: fixed !important;
            bottom: 80px !important;
            right: 20px !important;
            width: 50px !important;
            height: 50px !important;
            background: var(--md-primary-fg-color, #1976d2) !important;
            color: white !important;
            border: none !important;
            border-radius: 50% !important;
            font-size: 1.5rem !important;
            cursor: pointer !important;
            z-index: 1000 !important;
            box-shadow: 0 4px 12px rgba(0, 0, 0, 0.3) !important;
            transition: all 0.3s ease !important;
            display: flex !important;
            align-items: center !important;
            justify-content: center !important;
        `;
    }
    
    console.log('Embed mode deactivated');
}

/**
 * Add keyboard shortcuts
 */
function addKeyboardShortcuts() {
    document.addEventListener('keydown', function(e) {
        // ESC to exit embed mode
        if (e.key === 'Escape') {
            if (document.body.classList.contains('embed-mode')) {
                exitEmbedMode();
                e.preventDefault();
            }
        }
        
        // F11 to toggle embed mode
        if (e.key === 'F11') {
            e.preventDefault();
            if (document.body.classList.contains('embed-mode')) {
                exitEmbedMode();
            } else {
                enterEmbedMode();
            }
        }
    });
}

// Export functions for external use
window.embedUtils = {
    enterEmbedMode,
    exitEmbedMode,
    addFloatingExpandButton
};
