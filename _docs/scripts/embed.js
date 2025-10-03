/**
 * Embed.js - Fullscreen and interactive functionality for MkDocs
 */

document.addEventListener('DOMContentLoaded', function() {
    // Check for embed parameter in URL
    const urlParams = new URLSearchParams(window.location.search);
    const embedMode = urlParams.get('embed') === 'true' || urlParams.get('fullscreen') === 'true';
    
    // Add fullscreen functionality to tables and other elements
    addFullscreenButtons();
    
    // Add keyboard shortcuts
    addKeyboardShortcuts();
    
    // Add table enhancements
    enhanceTables();
    
    // Auto-enter fullscreen mode if embed parameter is present
    if (embedMode) {
        autoEnterEmbedMode();
    }
});

/**
 * Auto-enter embed mode for the main content area
 */
function autoEnterEmbedMode() {
    // Target the .md-content area specifically for embed mode
    let targetElement = document.querySelector('.md-content');
    
    if (!targetElement) {
        // Fallback to table or other content
        targetElement = document.querySelector('table, .md-content__inner, .md-typeset, main');
    }
    
    if (targetElement) {
        // Create wrapper if needed
        let wrapper = targetElement.closest('.fullscreen-wrapper');
        if (!wrapper) {
            wrapper = document.createElement('div');
            wrapper.className = 'fullscreen-wrapper';
            targetElement.parentNode.insertBefore(wrapper, targetElement);
            wrapper.appendChild(targetElement);
            
            // Add fullscreen button
            const button = document.createElement('button');
            button.className = 'fullscreen-btn';
            button.innerHTML = '⛷';
            button.title = 'Exit Fullscreen (ESC)';
            button.addEventListener('click', () => toggleFullscreen(wrapper));
            wrapper.appendChild(button);
        }
        
        // Enter fullscreen immediately
        enterFullscreen(wrapper);
        
        // Also hide browser chrome if possible (requires user gesture)
        setTimeout(() => {
            if (document.documentElement.requestFullscreen) {
                document.documentElement.requestFullscreen().catch(() => {
                    // Ignore errors - not all browsers support this or it requires user gesture
                });
            }
        }, 500);
    }
}

/**
 * Add fullscreen buttons to tables and other content
 */
function addFullscreenButtons() {
    // Target tables and other elements that should have fullscreen capability
    const targets = document.querySelectorAll('table, .network-container, .treemap-container, .interactive-demo');
    
    targets.forEach(element => {
        // Create fullscreen button
        const button = document.createElement('button');
        button.className = 'fullscreen-btn';
        button.innerHTML = '⛶';
        button.title = 'Toggle Fullscreen (F11)';
        button.setAttribute('aria-label', 'Toggle fullscreen');
        
        // Create wrapper if needed
        let wrapper = element.parentElement;
        if (!wrapper.classList.contains('fullscreen-wrapper')) {
            wrapper = document.createElement('div');
            wrapper.className = 'fullscreen-wrapper';
            element.parentNode.insertBefore(wrapper, element);
            wrapper.appendChild(element);
        }
        
        // Add button to wrapper
        wrapper.appendChild(button);
        
        // Add click handler
        button.addEventListener('click', () => toggleFullscreen(wrapper));
    });
}

/**
 * Toggle fullscreen mode for an element
 */
function toggleFullscreen(element) {
    if (element.classList.contains('fullscreen-active')) {
        exitFullscreen(element);
    } else {
        enterFullscreen(element);
    }
}

/**
 * Enter fullscreen mode
 */
function enterFullscreen(element) {
    element.classList.add('fullscreen-active');
    document.body.classList.add('fullscreen-mode');
    
    // Update button text
    const button = element.querySelector('.fullscreen-btn');
    if (button) {
        button.innerHTML = '⛷';
        button.title = 'Exit Fullscreen (ESC)';
    }
    
    // Focus the element for keyboard navigation
    element.setAttribute('tabindex', '-1');
    element.focus();
}

/**
 * Exit fullscreen mode
 */
function exitFullscreen(element) {
    element.classList.remove('fullscreen-active');
    document.body.classList.remove('fullscreen-mode');
    
    // Update button text
    const button = element.querySelector('.fullscreen-btn');
    if (button) {
        button.innerHTML = '⛶';
        button.title = 'Toggle Fullscreen (F11)';
    }
    
    element.removeAttribute('tabindex');
}

/**
 * Add keyboard shortcuts
 */
function addKeyboardShortcuts() {
    document.addEventListener('keydown', function(e) {
        // ESC to exit fullscreen
        if (e.key === 'Escape') {
            const fullscreenElement = document.querySelector('.fullscreen-active');
            if (fullscreenElement) {
                exitFullscreen(fullscreenElement);
                e.preventDefault();
            }
        }
        
        // F11 to toggle fullscreen on focused element
        if (e.key === 'F11') {
            const focusedWrapper = document.activeElement.closest('.fullscreen-wrapper');
            if (focusedWrapper) {
                toggleFullscreen(focusedWrapper);
                e.preventDefault();
            }
        }
    });
}

/**
 * Enhance tables with sorting and filtering
 */
function enhanceTables() {
    const tables = document.querySelectorAll('table');
    
    tables.forEach(table => {
        // Add table controls
        addTableControls(table);
        
        // Make tables responsive
        makeTableResponsive(table);
        
        // Add sorting functionality
        addTableSorting(table);
    });
}

/**
 * Add controls to tables
 */
function addTableControls(table) {
    const wrapper = table.closest('.fullscreen-wrapper');
    if (!wrapper) return;
    
    // Create controls container
    const controls = document.createElement('div');
    controls.className = 'table-controls';
    
    // Add search input
    const searchInput = document.createElement('input');
    searchInput.type = 'text';
    searchInput.placeholder = 'Search table...';
    searchInput.className = 'table-search';
    
    searchInput.addEventListener('input', () => filterTable(table, searchInput.value));
    
    controls.appendChild(searchInput);
    wrapper.insertBefore(controls, table);
}

/**
 * Make table responsive
 */
function makeTableResponsive(table) {
    // Add responsive wrapper if not already present
    if (!table.parentElement.classList.contains('table-responsive')) {
        const wrapper = document.createElement('div');
        wrapper.className = 'table-responsive';
        table.parentNode.insertBefore(wrapper, table);
        wrapper.appendChild(table);
    }
}

/**
 * Add sorting to table headers
 */
function addTableSorting(table) {
    const headers = table.querySelectorAll('th');
    
    headers.forEach((header, index) => {
        header.style.cursor = 'pointer';
        header.title = 'Click to sort';
        
        header.addEventListener('click', () => {
            sortTable(table, index);
        });
    });
}

/**
 * Sort table by column
 */
function sortTable(table, columnIndex) {
    const tbody = table.querySelector('tbody');
    if (!tbody) return;
    
    const rows = Array.from(tbody.querySelectorAll('tr'));
    const header = table.querySelectorAll('th')[columnIndex];
    
    // Determine sort direction
    const currentSort = header.getAttribute('data-sort') || 'asc';
    const newSort = currentSort === 'asc' ? 'desc' : 'asc';
    
    // Clear all sort indicators
    table.querySelectorAll('th').forEach(th => {
        th.removeAttribute('data-sort');
        th.classList.remove('sort-asc', 'sort-desc');
    });
    
    // Set new sort
    header.setAttribute('data-sort', newSort);
    header.classList.add(`sort-${newSort}`);
    
    // Sort rows
    rows.sort((a, b) => {
        const aText = a.cells[columnIndex]?.textContent.trim() || '';
        const bText = b.cells[columnIndex]?.textContent.trim() || '';
        
        // Try to parse as numbers
        const aNum = parseFloat(aText);
        const bNum = parseFloat(bText);
        
        if (!isNaN(aNum) && !isNaN(bNum)) {
            return newSort === 'asc' ? aNum - bNum : bNum - aNum;
        } else {
            return newSort === 'asc' ? 
                aText.localeCompare(bText) : 
                bText.localeCompare(aText);
        }
    });
    
    // Reorder rows
    rows.forEach(row => tbody.appendChild(row));
}

/**
 * Filter table rows based on search term
 */
function filterTable(table, searchTerm) {
    const tbody = table.querySelector('tbody');
    if (!tbody) return;
    
    const rows = tbody.querySelectorAll('tr');
    const term = searchTerm.toLowerCase();
    
    rows.forEach(row => {
        const text = row.textContent.toLowerCase();
        row.style.display = text.includes(term) ? '' : 'none';
    });
}

/**
 * Utility function to make any element fullscreen
 */
function makeFullscreen(selector) {
    const element = document.querySelector(selector);
    if (element) {
        // Create wrapper if needed
        let wrapper = element.parentElement;
        if (!wrapper.classList.contains('fullscreen-wrapper')) {
            wrapper = document.createElement('div');
            wrapper.className = 'fullscreen-wrapper';
            element.parentNode.insertBefore(wrapper, element);
            wrapper.appendChild(element);
        }
        
        // Add fullscreen button if not present
        if (!wrapper.querySelector('.fullscreen-btn')) {
            const button = document.createElement('button');
            button.className = 'fullscreen-btn';
            button.innerHTML = '⛶';
            button.title = 'Toggle Fullscreen';
            button.addEventListener('click', () => toggleFullscreen(wrapper));
            wrapper.appendChild(button);
        }
    }
}

// Export functions for external use
window.embedUtils = {
    makeFullscreen,
    toggleFullscreen,
    enterFullscreen,
    exitFullscreen,
    autoEnterEmbedMode
};