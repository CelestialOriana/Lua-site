# debug_materials.py
from app import MATERIALS, calculate_total_materials, count_material_types

# Afficher les matériels
print("Liste des matériels :")
for material in MATERIALS:
    print(f"ID: {material['id']}, Nom: {material['name']}, Disponible: {material['available']}, Total: {material['total']}")

# Calculer les statistiques
total = calculate_total_materials()
available = sum(material["available"] for material in MATERIALS)
types = count_material_types()

print("\nStatistiques :")
print(f"Total : {total}")
print(f"Disponible : {available}")
print(f"Types : {types}")