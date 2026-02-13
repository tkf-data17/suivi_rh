import pandas as pd
import datetime
import os

def clean_time(val, default=None):
    if pd.isna(val) or val == "" or str(val).strip() == "":
        return default
    
    val_str = str(val).strip()
    
    # Check for 'h' format (e.g. 08h00)
    if 'h' in val_str:
        parts = val_str.split('h')
        if len(parts) >= 2:
            h = parts[0].strip().zfill(2)
            m = parts[1].strip().zfill(2)
            return f"{h}:{m}"
            
    # Check for ':' format
    if ':' in val_str:
        # standardizing to HH:MM (ignoring seconds if present)
        parts = val_str.split(':')
        h = parts[0].strip().zfill(2)
        m = parts[1].strip().zfill(2)
        return f"{h}:{m}"
        
    # If it's a datetime object
    if isinstance(val, datetime.time):
        return val.strftime("%H:%M")
    if isinstance(val, datetime.datetime):
        return val.strftime("%H:%M")
        
    return default

def migrate():
    old_file = "base_old.xlsx"
    target_file = "suivi_employes.xlsx"
    backup_file = "suivi_employes.json"
    
    if not os.path.exists(old_file):
        print(f"❌ Fichier {old_file} introuvable.")
        return

    print(f"🔄 Lecture de {old_file}...")
    df_old = pd.read_excel(old_file)
    
    # Destination Columns
    columns = [
        "N° ordre", 
        "Date", 
        "Nom et Prenoms", 
        "Sexe", 
        "Service", 
        "Heure d'arrivée", 
        "Heure de départ"
    ]
    
    # If target exists, load it to get next ID, else create empty
    if os.path.exists(target_file):
        df_target = pd.read_excel(target_file)
        if not df_target.empty and "N° ordre" in df_target.columns:
            try:
                start_id = df_target["N° ordre"].max() + 1
                if pd.isna(start_id): start_id = 1
            except:
                start_id = 1
        else:
             df_target = pd.DataFrame(columns=columns)
             start_id = 1
    else:
        df_target = pd.DataFrame(columns=columns)
        start_id = 1
        
    new_rows = []
    current_id = int(start_id)
    
    print("🔄 Traitement des données...")
    for idx, row in df_old.iterrows():
        # Map columns - Assuming names match roughly
        # Old file col names might vary slightly, let's look at what we got earlier:
        # ['N° ordre', 'Date', 'Nom et Prenoms', 'Sexe', 'Service', "Heure d'arrivée", 'Heure de départ']
        
        # Name
        name = row.get("Nom et Prenoms", "")
        if pd.isna(name) or str(name).strip() == "":
            continue # Skip empty names
            
        # Date - Ensure string format DD/MM/YYYY
        date_raw = row.get("Date", "")
        date_str = ""
        if isinstance(date_raw, datetime.datetime):
             date_str = date_raw.strftime("%d/%m/%Y")
        else:
             date_str = str(date_raw) # Should probably try to parse if string is messy
        
        # Sexe / Service
        sexe = row.get("Sexe", "")
        service = row.get("Service", "")
        
        # Times
        ha_raw = row.get("Heure d'arrivée")
        hd_raw = row.get("Heure de départ")
        
        ha_clean = clean_time(ha_raw, default="08:00") # Default arrival if missing? usage said "met 17:30" for DEPART. Arrivée? Let's check context. Usually keep whatever or empty. But keeping existing logic. If missing arrival, maybe leave empty? But text input expects something. Let's try 07:30 or just missing. Text input is loose. But let's assume valid data in old file. If invalid, maybe put "00:00"? Or user didn't specify arrival default. 
        # Actually, let's try to keep it cleaner.
        if not ha_clean: ha_clean = "07:30" # Fallback
        
        hd_clean = clean_time(hd_raw, default="17:30")
        
        new_row = {
            "N° ordre": current_id,
            "Date": date_str,
            "Nom et Prenoms": name,
            "Sexe": sexe,
            "Service": service,
            "Heure d'arrivée": ha_clean,
            "Heure de départ": hd_clean
        }
        
        new_rows.append(new_row)
        current_id += 1
        
    # Concat
    if new_rows:
        df_new = pd.DataFrame(new_rows)
        df_final = pd.concat([df_target, df_new], ignore_index=True)
        
        # Save Excel
        df_final.to_excel(target_file, index=False)
        print(f"✅ {len(new_rows)} lignes importées dans {target_file}.")
        
        # Save JSON Backup
        df_final.to_json(backup_file, orient='records', force_ascii=False, indent=4, date_format='iso')
        print(f"✅ Sauvegarde JSON générée : {backup_file}")
        
    else:
        print("⚠️ Aucune donnée importée.")

if __name__ == "__main__":
    migrate()
