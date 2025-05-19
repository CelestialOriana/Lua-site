// static/js/app.js

document.addEventListener('DOMContentLoaded', function() {
    // Gestion des filtres sur le tableau de bord
    const filterButtons = document.querySelectorAll('.filter-btn');
    const materialsTable = document.getElementById('materials-table');
    
    if (filterButtons && materialsTable) {
        filterButtons.forEach(button => {
            button.addEventListener('click', function() {
                // Retirer la classe active de tous les boutons
                filterButtons.forEach(btn => btn.classList.remove('active'));
                
                // Ajouter la classe active au bouton cliqué
                this.classList.add('active');
                
                // Filtrer le tableau
                const filterValue = this.getAttribute('data-filter');
                const rows = materialsTable.querySelectorAll('tbody tr');
                
                rows.forEach(row => {
                    if (filterValue === 'all') {
                        row.style.display = '';
                    } else {
                        const rowType = row.getAttribute('data-type');
                        if (rowType === filterValue) {
                            row.style.display = '';
                        } else {
                            row.style.display = 'none';
                        }
                    }
                });
            });
        });
    }
    
    // Mise en évidence des stocks bas (moins de 20%)
    const rows = document.querySelectorAll('tbody tr');
    rows.forEach(row => {
        const available = parseInt(row.cells[2].textContent);
        const total = parseInt(row.cells[3].textContent);
        
        if (available / total < 0.2) {
            row.cells[2].style.color = 'var(--danger-color)';
            row.cells[2].style.fontWeight = 'bold';
        }
    });
});
