import streamlit as st
from database import DataManager
import pandas as pd
import traceback

st.title("Debug Direct File Write")

try:
    with open("debug_direct.txt", "w", encoding="utf-8") as f:
        f.write("--- DEBUG START ---\n")
        f.flush()
        
        db = DataManager()
        f.write("DB Init OK\n")
        
        df_mov = db.load_data()
        f.write(f"Mov Loaded: {len(df_mov)}\n")
        
        df_pers = db.load_personnel()
        f.write(f"Pers Loaded: {len(df_pers)}\n")
        
        names_p = []
        if not df_pers.empty:
            cols = df_pers.columns.tolist()
            f.write(f"Pers Cols: {cols}\n")
            name_col = next((c for c in cols if "nom" in c.lower()), None)
            if name_col:
                names_p = sorted(df_pers[name_col].astype(str).unique().tolist())
                f.write(f"Pers Sample: {names_p[:2]}\n")
        
        names_m = []
        if not df_mov.empty:
            cols = df_mov.columns.tolist()
            f.write(f"Mov Cols: {cols}\n")
            name_col = next((c for c in cols if "nom" in c.lower()), None)
            if name_col:
                 names_m = sorted(df_mov[name_col].astype(str).unique().tolist())
                 f.write(f"Mov Sample: {names_m[:2]}\n")
        
        f.write("\nMatching:\n")
        for name_p in names_p:
            match = False
            for name_m in names_m:
                 if name_p == name_m:
                     match = True
                     break
            if not match: 
                 f.write(f"FAIL: '{name_p}'\n")
                 # Check stripped
                 for name_m in names_m:
                     if name_p.strip() == name_m.strip():
                          f.write(f"   -> STRIP MATCH with '{name_m}'\n")
        
        f.write("--- DEBUG END ---\n")

except Exception as e:
    with open("debug_direct.txt", "a") as f:
        f.write(f"ERROR: {e}\n")
        traceback.print_exc(file=f)

st.success("Wrote to debug_direct.txt")
