import pandas as pd
import json
import os

def import_personnel_list():
    excel_path = "liste personnel.xlsx"
    json_path = "personnel.json"
    
    if not os.path.exists(excel_path):
        print(f"❌ Fichier '{excel_path}' introuvable.")
        return

    print(f"🔄 Lecture de '{excel_path}'...")
    try:
        df = pd.read_excel(excel_path)
    except Exception as e:
        print(f"❌ Erreur lecture Excel: {e}")
        return

    # Expected columns usually found: 'Nom et Prénoms', 'Service', 'Sexe' (maybe 'Fonction' too)
    # We will prioritize these.
    
    employees = []
    
    print(f"Colonnes trouvées: {df.columns.tolist()}")
    
    # Normalize column names for easier access (strip whitespace)
    df.columns = [str(c).strip() for c in df.columns]
    
    count_imported = 0
    
    for idx, row in df.iterrows():
        # Get Name
        name = row.get("Nom et Prénoms", "")
        if pd.isna(name) or str(name).strip() == "":
            continue
            
        full_name = str(name).strip().upper() # Ensure uppercase as requested for Names generally
        
        # Get Sexe
        sexe = row.get("Sexe", "M") # Default if missing? Or empty. Let's try to get it.
        if pd.isna(sexe): sexe = "M"
        sexe = str(sexe).strip().upper()
        if sexe not in ["M", "F"]: sexe = "M" # Basic validation
        
        # Get Service
        service = row.get("Service", "Autre")
        if pd.isna(service): service = "Autre"
        service = str(service).strip()
        
        # Get Order Number if exists, otherwise generate or leave empty?
        # User requested consistency and "met un numéro d'ordre aussi".
        # Let's try to find it in Excel or generate sequential 1..N
        num_ordre = row.get("N° ordre", idx + 1)
        if pd.isna(num_ordre): num_ordre = idx + 1
        
        employees.append({
            "N° ordre": int(num_ordre),
            "Nom et Prénoms": full_name,
            "Sexe": sexe,
            "Service": service
        })
        count_imported += 1

    # Save to JSON
    with open(json_path, 'w', encoding='utf-8') as f:
        json.dump(employees, f, ensure_ascii=False, indent=4)
        
    print(f"✅ {count_imported} employés importés correctement dans '{json_path}' avec numéros d'ordre.")

if __name__ == "__main__":
    import_personnel_list()
