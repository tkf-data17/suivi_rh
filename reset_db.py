import pandas as pd
import os
import json

# Reset Movements Database
movements_file = "suivi_employes.xlsx"
columns = [
    "N° ordre", 
    "Date", 
    "Nom et Prenoms", 
    "Sexe", 
    "Service", 
    "Heure d'arrivée", 
    "Heure de départ"
]
df_movements = pd.DataFrame(columns=columns)
df_movements.to_excel(movements_file, index=False)
print(f"✅ Fichier '{movements_file}' réinitialisé.")

# Reset Personnel Database
personnel_file = "personnel.json"
# Create an empty list in JSON
with open(personnel_file, 'w') as f:
    json.dump([], f)
print(f"✅ Fichier '{personnel_file}' vidé.")

# Note: We do NOT delete 'liste personnel.xlsx' as it might be a backup source, 
# but preserving an empty JSON prevents it from being reloaded automatically.
