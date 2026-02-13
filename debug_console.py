from database import DataManager
import pandas as pd

print("--- DEBUGGING DATA MATCHING ---")

try:
    db = DataManager()
    print("DB Initialized")
    
    df_mov = db.load_data()
    print(f"Mouvements Loaded: {len(df_mov)} rows")
    
    df_pers = db.load_personnel()
    print(f"Personnel Loaded: {len(df_pers)} rows")

    if not df_pers.empty:
        cols_p = df_pers.columns.tolist()
        print("Personnel Columns:", cols_p)
        name_col_p = next((c for c in cols_p if "nom" in c.lower()), None)
        
        if name_col_p:
            names_p = sorted(df_pers[name_col_p].dropna().unique().tolist())
            print(f"Sample Personnel Names ({len(names_p)}): {names_p[:5]}")
        else:
            print("ERROR: No 'nom' column found in Personnel")
            names_p = []

    if not df_mov.empty:
        cols_m = df_mov.columns.tolist()
        print("Mouvements Columns:", cols_m)
        name_col_m = next((c for c in cols_m if "nom" in c.lower()), None)
        
        if name_col_m:
            names_m = sorted(df_mov[name_col_m].dropna().unique().tolist())
            print(f"Sample Mouvements Names ({len(names_m)}): {names_m[:5]}")
        else:
            print("ERROR: No 'nom' column found in Mouvements")
            names_m = []

    print("\n--- EXACT MATCH CHECK ---")
    match_count = 0
    fail_count = 0
    
    for name_p in names_p:
        # Check against Mouvements
        # Try finding exact match
        found = False
        for name_m in names_m:
             if str(name_p) == str(name_m):
                 found = True
                 break
        
        if found:
            match_count += 1
        else:
            fail_count += 1
            print(f"FAIL: '{name_p}' not found in Mouvements (Example close match?)")
            # suggestive match
            for name_m in names_m:
                if str(name_p).strip().lower() == str(name_m).strip().lower():
                     print(f"   -> BUT found near match: '{name_m}' (Differ by case/whitespace?)")

    print(f"\nSummary: {match_count} Matches, {fail_count} Fails")

except Exception as e:
    print(f"CRITICAL ERROR: {e}")
