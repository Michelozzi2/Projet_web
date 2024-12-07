$(document).ready(function() {
    // Fonction pour actualiser le tableau
    function fetchItems() {
        var searchQuery = $('#search-input').val();
        var sortQuery = $('#sort-select').val();

        $.ajax({
            url: inventoryListUrl, // Utiliser la variable définie dans le template
            type: 'GET',
            data: {
                search: searchQuery,
                sort: sortQuery
            },
            success: function(response) {
                $('#inventory-body').html(response.items_html);
            }
        });
    }

    // Actualisation du tableau lors de la saisie dans le champ de recherche
    $('#search-input').on('input', function() {
        fetchItems();
    });

    // Actualisation du tableau lors du changement de tri
    $('#sort-select').on('change', function() {
        fetchItems();
    });
});


$.ajaxSetup({
    headers: {
        'X-CSRFToken': $('#csrf-token').val()
    }
});