/**
 * Embed.js - Clean embed functionality for MkDocs
 */

document.addEventListener('DOMContentLoaded', function() {
    console.log('Embed.js loaded and initializing...');
    
    // Check for embed parameter in URL
    const urlParams = new URLSearchParams(window.location.search);
    const embedMode = urlParams.get('embed') === 'true';
    
    console.log('Embed mode:', embedMode);
    
    // Add table enhancements
    enhanceTables();
    
    // Add floating expand icon (only on non-embed pages)
    if (!embedMode) {
        addFloatingExpandIcon();
    }
    
    // Auto-enter embed mode if parameter is present
    if (embedMode) {
        console.log('Activating embed mode...');
        activateEmbedMode();
    }
});

/**
 * Add a floating expand icon for easy access to embed mode
 */
function addFloatingExpandIcon() {
    // Create floating button
    const floatingBtn = document.createElement('button');
    floatingBtn.className = 'floating-expand-btn';
    floatingBtn.innerHTML = '⤢'; // Diagonal arrows
    floatingBtn.title = 'Open in embed view';
    floatingBtn.setAttribute('aria-label', 'Open in embed view');
    
    // Add click handler to redirect to embed=true
    floatingBtn.addEventListener('click', function() {
        const currentUrl = new URL(window.location.href);
        // Clear any hash/fragment
        currentUrl.hash = '';
        // Add embed parameter
        currentUrl.searchParams.set('embed', 'true');
        window.location.href = currentUrl.toString();
    });
    
    // Add to page
    document.body.appendChild(floatingBtn);
    
    console.log('Floating expand icon added');
}

/**
 * Activate embed mode by applying the CSS class
 */
function activateEmbedMode() {
    // Add embed mode class to body
    document.body.classList.add('embed-mode');
    
    // Debug: Log the DOM structure
    console.log('DOM structure analysis:');
    console.log('- .md-container:', document.querySelector('.md-container'));
    console.log('- .md-main:', document.querySelector('.md-main'));
    console.log('- .md-content:', document.querySelector('.md-content'));
    console.log('- .md-content__inner:', document.querySelector('.md-content__inner'));
    console.log('- .md-typeset:', document.querySelector('.md-typeset'));
    
    // Check all direct children of .md-main
    const mdMain = document.querySelector('.md-main');
    if (mdMain) {
        console.log('.md-main children:', Array.from(mdMain.children).map(el => el.className));
    }
    
    // Add a simple close button
    addEmbedCloseButton();
    
    console.log('Embed mode activated successfully');
}

/**
 * Add a close button to exit embed mode
 */
function addEmbedCloseButton() {
    const closeBtn = document.createElement('button');
    closeBtn.className = 'embed-close-btn';
    closeBtn.innerHTML = '✕';
    closeBtn.title = 'Exit embed view';
    closeBtn.setAttribute('aria-label', 'Exit embed view');
    
    // Add click handler to remove embed parameter
    closeBtn.addEventListener('click', function() {
        const url = new URL(window.location);
        url.searchParams.delete('embed');
        // Keep any existing hash
        window.location.href = url.toString();
    });
    
    // Add to page
    document.body.appendChild(closeBtn);
}

/**
 * Enhance tables with sorting and filtering
 */
function enhanceTables() {
    const tables = document.querySelectorAll('table');
    
    console.log('Enhancing', tables.length, 'tables');
    
    tables.forEach(table => {
        // Skip tables that are inside details elements (like version info)
        const parentDetails = table.closest('details');
        if (parentDetails) {
            console.log('Skipping table inside details element - no search needed');
            // Still make it responsive and sortable, just no search
            makeTableResponsive(table);
            addTableSorting(table);
            return;
        }
        
        // Add table controls (includes search)
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
    
    // Insert controls before the table
    table.parentNode.insertBefore(controls, table);
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

// Export functions for external use
window.embedUtils = {
    activateEmbedMode
};
