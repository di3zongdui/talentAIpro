// Find the Ant Design Select for the main search
var selectEl = document.querySelector('.ant-select');
if (!selectEl) {
    // Try to find by selector prefix
    selectEl = document.querySelector('[class*="ant-select"]');
}
if (selectEl) {
    selectEl.click();
    // Wait for dropdown
    setTimeout(function() {
        // Find the search input in the dropdown
        var searchInput = document.querySelector('.ant-select-selection-search-input');
        if (!searchInput) {
            searchInput = document.querySelector('input[placeholder*="关键词"]');
        }
        if (searchInput) {
            // Use native input setter for React
            var nativeInputValueSetter = Object.getOwnPropertyDescriptor(
                window.HTMLInputElement.prototype, 'value'
            ).set;
            nativeInputValueSetter.call(searchInput, '车险精算定价GLM');
            
            // Dispatch proper React events
            searchInput.dispatchEvent(new Event('input', { bubbles: true }));
            searchInput.dispatchEvent(new Event('change', { bubbles: true }));
            
            // Return success
            "SUCCESS: " + searchInput.value;
        } else {
            "ERROR: no search input found";
        }
    }, 1000);
    "WAITING for dropdown...";
} else {
    "ERROR: no ant-select found";
}
