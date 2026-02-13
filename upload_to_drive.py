import streamlit as st
import pandas as pd
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import os

def upload_data():
    st.title("📤 Migration vers Google Drive")
    st.info("Ce script va envoyer vos données locales (Excel/JSON) vers votre Google Sheet 'SUIVI_PERSONNEL_DB'.")

    if st.button("Lancer la migration"):
        # Connect
        scope = ["https://spreadsheets.google.com/feeds", 'https://www.googleapis.com/auth/spreadsheets',
                 "https://www.googleapis.com/auth/drive.file", "https://www.googleapis.com/auth/drive"]
        
        if "gcp_service_account" not in st.secrets:
            st.error("Secrets not found in .streamlit/secrets.toml")
            return

        creds_dict = dict(st.secrets["gcp_service_account"])
        creds = ServiceAccountCredentials.from_json_keyfile_dict(creds_dict, scope)
        client = gspread.authorize(creds)
        
        try:
            sheet = client.open("SUIVI_PERSONNEL_DB")
            st.success("✅ Connecté au Google Sheet 'SUIVI_PERSONNEL_DB'")
        except Exception as e:
            st.error(f"❌ Impossible d'ouvrir le Sheet 'SUIVI_PERSONNEL_DB'. Erreur: {e}")
            return

        # 1. PERSONNEL
        st.header("1. Migration du Personnel")
        if os.path.exists("personnel.json"):
            try:
                df_personnel = pd.read_json("personnel.json")
                st.write(f"Trouvé {len(df_personnel)} employés locaux.")
                
                try:
                    ws_personnel = sheet.worksheet("Personnel")
                    ws_personnel.clear()
                except:
                    ws_personnel = sheet.add_worksheet("Personnel", 1000, 10)
                
                # Headers
                ws_personnel.append_row(["N° ordre", "Nom et Prénoms", "Sexe", "Service"])
                
                rows_to_upload = []
                for idx, row in df_personnel.iterrows():
                    rows_to_upload.append([
                        int(row.get("N° ordre", idx+1)) if pd.notna(row.get("N° ordre")) else idx+1,
                        row.get("Nom et Prénoms", ""),
                        row.get("Sexe", ""),
                        row.get("Service", "")
                    ])
                    
                ws_personnel.append_rows(rows_to_upload)
                st.success(f"✅ {len(rows_to_upload)} employés envoyés sur le Drive.")
            except Exception as e:
                st.error(f"Erreur lors de l'envoi du personnel: {e}")
        else:
            st.warning("Fichier personnel.json introuvable.")

        # 2. MOUVEMENTS
        st.header("2. Migration des Mouvements")
        if os.path.exists("suivi_employes.xlsx"):
            try:
                df_mouv = pd.read_excel("suivi_employes.xlsx")
                st.write(f"Trouvé {len(df_mouv)} mouvements locaux.")
                
                try:
                    ws_mouv = sheet.worksheet("Mouvements")
                    ws_mouv.clear()
                except:
                     ws_mouv = sheet.add_worksheet("Mouvements", 1000, 20)
                     
                ws_mouv.append_row(["N° ordre", "Date", "Nom et Prenoms", "Sexe", "Service", "Heure d'arrivée", "Heure de départ"])
                
                rows_mouv = []
                for idx, row in df_mouv.iterrows():
                    rows_mouv.append([
                        int(row.get("N° ordre")) if pd.notna(row.get("N° ordre")) else idx+1,
                        str(row.get("Date")),
                        row.get("Nom et Prenoms"),
                        row.get("Sexe"),
                        row.get("Service"),
                        str(row.get("Heure d'arrivée", "")) if pd.notna(row.get("Heure d'arrivée")) else "",
                        str(row.get("Heure de départ", "")) if pd.notna(row.get("Heure de départ")) else ""
                    ])
                    
                ws_mouv.append_rows(rows_mouv)
                st.success(f"✅ {len(rows_mouv)} mouvements envoyés sur le Drive.")
            except Exception as e:
                 st.error(f"Erreur lors de l'envoi des mouvements: {e}")
        else:
             st.warning("Fichier suivi_employes.xlsx introuvable.")
             
        st.success("🎉 Migration terminée avec succès ! Vous pouvez fermer cet onglet et retourner sur l'application principale.")

if __name__ == "__main__":
    upload_data()
