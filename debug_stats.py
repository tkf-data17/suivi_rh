import streamlit as st
from database import DataManager
import pandas as pd
import sys

# Redirect stdout to a file
with open("debug_output.txt", "w", encoding="utf-8") as f:
    orig_stdout = sys.stdout
    sys.stdout = f

    print("--- DEBUG START ---")
    try:
        db = DataManager()
        df_mov = db.load_data()
        df_pers = db.load_personnel()

        print(f"Mouvements: {len(df_mov)}")
        print(f"Personnel: {len(df_pers)}")

        names_p = []
        if not df_pers.empty:
            cols = df_pers.columns.tolist()
            print(f"Pers Cols: {cols}")
            name_col = next((c for c in cols if "nom" in c.lower()), None)
            if name_col:
                names_p = sorted(df_pers[name_col].astype(str).unique().tolist())
                print(f"P Names Sample: {names_p[:3]}")

        names_m = []
        if not df_mov.empty:
            cols = df_mov.columns.tolist()
            print(f"Mov Cols: {cols}")
            name_col = next((c for c in cols if "nom" in c.lower()), None)
            if name_col:
                names_m = sorted(df_mov[name_col].astype(str).unique().tolist())
                print(f"M Names Sample: {names_m[:3]}")

        print("\n--- MATCHING ---")
        for name_p in names_p:
            match = False
            for name_m in names_m:
                 if name_p == name_m:
                     match = True
                     break
            if not match:
                print(f"FAIL: '{name_p}' not in Mov")
                for name_m in names_m:
                    if name_p.strip() == name_m.strip():
                         print(f"   -> WHITESPACE MATCH: '{name_m}'")
    except Exception as e:
        print(f"ERROR: {e}")
    
    print("--- DEBUG END ---")
    
    sys.stdout = orig_stdout

st.write("Debug finished. Check debug_output.txt")
