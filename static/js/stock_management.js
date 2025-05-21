document.addEventListener('DOMContentLoaded', function() {
    // Références aux éléments du formulaire
    const materialForm = document.getElementById('materialForm');
    
    if (materialForm) {
        // Intercepter la soumission du formulaire pour mise à jour des statistiques
        materialForm.addEventListener('submit', function(e) {
            e.preventDefault();
            
            // Récupérer les données du formulaire
            const materialId = document.getElementById('materialId').value;
            const materialData = {
                name: document.getElementById('name').value,
                type: document.getElementById('type').value,
                available: parseInt(document.getElementById('available').value),
                total: parseInt(document.getElementById('total').value),
                description: document.getElementById('description').value
            };
            
            // Ajouter l'ID si on est en mode édition
            if (materialId) {
                materialData.id = parseInt(materialId);
            }
            
            // Détermine si c'est un ajout ou une modification
            const method = materialId ? 'PUT' : 'POST';
            
            fetch('/api/admin/materials', {
                method: method,
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify(materialData)
            })
            .then(response => {
                if (!response.ok) {
                    return response.json().then(data => {
                        throw new Error(data.error || "Une erreur est survenue");
                    });
                }
                return response.json();
            })
            .then(data => {
                if (data.success) {
                    // Fermer le modal
                    const materialModal = document.getElementById('materialModal');
                    if (materialModal) {
                        materialModal.style.display = 'none';
                    }
                    
                    // Si on a reçu des statistiques mises à jour, les enregistrer en localStorage
                    if (data.stats) {
                        localStorage.setItem('dashboard_stats', JSON.stringify(data.stats));
                    }
                    
                    // Actualiser la liste des matériels
                    loadMaterials();
                    
                    // Afficher un message de succès
                    alert(materialId ? "Matériel mis à jour avec succès" : "Matériel ajouté avec succès");
                } else {
                    alert("Erreur: " + (data.message || "Une erreur est survenue"));
                }
            })
            .catch(error => {
                console.error('Erreur:', error);
                alert("Erreur: " + error.message);
            });
        });
    }
    
    // Également intercepter les suppressions
    document.addEventListener('click', function(e) {
        if (e.target && e.target.classList.contains('delete-btn')) {
            e.preventDefault();
            
            if (!confirm('Êtes-vous sûr de vouloir supprimer ce matériel ?')) {
                return;
            }
            
            const materialId = parseInt(e.target.getAttribute('data-id'));
            
            fetch('/api/admin/materials', {
                method: 'DELETE',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({ id: materialId })
            })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    // Si on a reçu des statistiques mises à jour, les enregistrer en localStorage
                    if (data.stats) {
                        localStorage.setItem('dashboard_stats', JSON.stringify(data.stats));
                    }
                    
                    // Actualiser la liste
                    loadMaterials();
                    
                    // Afficher un message de succès
                    alert("Matériel supprimé avec succès");
                } else {
                    alert("Erreur: " + (data.error || "Une erreur est survenue"));
                }
            })
            .catch(error => {
                console.error('Erreur:', error);
                alert("Erreur lors de la suppression");
            });
        }
    });
});