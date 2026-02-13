import pandas as pd
import json

def convert_excel_to_json(excel_file, json_file):
    try:
        df = pd.read_excel(excel_file)
        # Rename columns to standard ones if needed
        # Assuming columns: Nom et Prénoms, Sexe, Service
        # We'll adapt based on first row
        records = df.to_dict(orient='records')
        
        # Clean up records (handle NaN)
        cleaned_records = []
        for r in records:
            # Drop NaN values
            item = {k: v for k, v in r.items() if pd.notna(v)}
            cleaned_records.append(item)
            
        with open(json_file, 'w', encoding='utf-8') as f:
            json.dump(cleaned_records, f, ensure_ascii=False, indent=4)
            
        print(f"Conversion successful: {len(cleaned_records)} records saved to {json_file}")
    except Exception as e:
        print(f"Error converting: {e}")

if __name__ == "__main__":
    convert_excel_to_json("liste personnel.xlsx", "personnel.json")
