document.addEventListener('DOMContentLoaded', function() {
    const searchInput = document.getElementById('searchInput');
    const typeFilter = document.getElementById('typeFilter');
    const table = document.getElementById('inventoryTable');
    const rows = table.getElementsByTagName('tr');

    function filterTable() {
        const searchText = searchInput.value.toLowerCase();
        const filterType = typeFilter.value;
    
        Array.from(rows).forEach((row, index) => {
            if (index === 0) return; // Skip header row
            
            const type = row.getAttribute('data-type');
            const text = row.textContent.toLowerCase();
            
            const typeMatch = filterType === 'all' || type === filterType;
            const textMatch = text.includes(searchText);
    
            row.style.display = typeMatch && textMatch ? '' : 'none';
        });
    }

    searchInput.addEventListener('input', filterTable);
    typeFilter.addEventListener('change', filterTable);
});