import pandas as pd
import json
import os

def populate_personnel():
    old_file = "base_old.xlsx"
    json_path = "personnel.json"
    
    if not os.path.exists(old_file):
        print(f"❌ Fichier {old_file} introuvable.")
        return

    print(f"🔄 Lecture de {old_file} pour extraction du personnel...")
    df_old = pd.read_excel(old_file)
    
    # Extract unique employees
    # Columns expected: 'Nom et Prenoms', 'Sexe', 'Service'
    # Check actual columns from df_old.columns to be safe
    # Based on previous check: ['N° ordre', 'Date', 'Nom et Prenoms', 'Sexe', 'Service', ...]
    
    employees = {}
    
    for idx, row in df_old.iterrows():
        name = row.get("Nom et Prenoms", "")
        if pd.isna(name) or str(name).strip() == "":
            continue
            
        full_name = str(name).strip()
        sexe = row.get("Sexe", "")
        service = row.get("Service", "")
        
        # Clean Sexe/Service if needed?
        if pd.isna(sexe): sexe = "M" 
        if pd.isna(service): service = "Autre"
        
        # Store in dict to filter duplicates (last seen wins or first? usually doesn't matter if consistent)
        if full_name not in employees:
            employees[full_name] = {
                "Nom et Prénoms": full_name,
                "Sexe": sexe,
                "Service": service
            }
            
    # Convert to list
    new_personnel_list = list(employees.values())
    
    # Load existing JSON
    current_data = []
    if os.path.exists(json_path):
        try:
            with open(json_path, 'r', encoding='utf-8') as f:
                current_data = json.load(f)
        except:
            current_data = []
            
    # Merge (avoid duplicates)
    existing_names = set(p.get("Nom et Prénoms") for p in current_data)
    added_count = 0
    
    for p in new_personnel_list:
        if p["Nom et Prénoms"] not in existing_names:
            current_data.append(p)
            existing_names.add(p["Nom et Prénoms"])
            added_count += 1
            
    # Save
    with open(json_path, 'w', encoding='utf-8') as f:
        json.dump(current_data, f, ensure_ascii=False, indent=4)
        
    print(f"✅ {added_count} nouveaux employés ajoutés à {json_path} depuis {old_file}.")

if __name__ == "__main__":
    populate_personnel()
