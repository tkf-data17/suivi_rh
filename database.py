import pandas as pd
import streamlit as st
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import json

class DataManager:
    def __init__(self):
        # Authenticate with Google Sheets
        self.scope = ["https://spreadsheets.google.com/feeds", 'https://www.googleapis.com/auth/spreadsheets',
                 "https://www.googleapis.com/auth/drive.file", "https://www.googleapis.com/auth/drive"]
        
        self.creds = None
        self.client = None
        self.sheet = None
        
        self._connect_google_sheets()

    def _connect_google_sheets(self):
        """Connects to Google Sheets using Streamlit secrets."""
        try:
            if "gcp_service_account" in st.secrets:
                # Load from secrets.toml
                creds_dict = dict(st.secrets["gcp_service_account"])
                self.creds = ServiceAccountCredentials.from_json_keyfile_dict(creds_dict, self.scope)
            else:
                # Fallback or error if not configured
                st.error("⚠️ Secrets Google Sheets non configurés ! Ajoutez [gcp_service_account] dans .streamlit/secrets.toml")
                return

            self.client = gspread.authorize(self.creds)
            
            # Open the Spreadsheet (Replace with your actual Sheet Name)
            # We assume a single Spreadsheet with two tabs: "Mouvements" and "Personnel"
            sheet_name = "SUIVI_PERSONNEL_DB" # You might want to let user configure this
            try:
                self.sheet = self.client.open(sheet_name)
            except gspread.SpreadsheetNotFound:
                st.error(f"❌ Impossible de trouver le Google Sheet nommé '{sheet_name}'. Veuillez le créer et le partager avec l'email du service account.")
                return

        except Exception as e:
            st.error(f"Erreur de connexion Google Sheets : {e}")

    def load_data(self):
        """Loads movements data from 'Mouvements' worksheet."""
        if not self.sheet: return pd.DataFrame()
        try:
            worksheet = self.sheet.worksheet("Mouvements")
            data = worksheet.get_all_records()
            return pd.DataFrame(data)
        except gspread.WorksheetNotFound:
            # Create if missing
            worksheet = self.sheet.add_worksheet(title="Mouvements", rows="1000", cols="20")
            worksheet.append_row(["N° ordre", "Date", "Nom et Prenoms", "Sexe", "Service", "Heure d'arrivée", "Heure de départ"])
            return pd.DataFrame(columns=["N° ordre", "Date", "Nom et Prenoms", "Sexe", "Service", "Heure d'arrivée", "Heure de départ"])
        except Exception as e:
            st.error(f"Erreur lecture données: {e}")
            return pd.DataFrame()

    def load_personnel(self):
        """Loads personnel list from 'Personnel' worksheet."""
        if not self.sheet: return pd.DataFrame()
        try:
            worksheet = self.sheet.worksheet("Personnel")
            data = worksheet.get_all_records()
            return pd.DataFrame(data)
        except gspread.WorksheetNotFound:
             # Create if missing
            worksheet = self.sheet.add_worksheet(title="Personnel", rows="1000", cols="10")
            worksheet.append_row(["N° ordre", "Nom et Prénoms", "Sexe", "Service"])
            return pd.DataFrame(columns=["N° ordre", "Nom et Prénoms", "Sexe", "Service"])
        except Exception:
            return pd.DataFrame()

    def add_employee(self, name, sexe, service):
        """Adds or updates an employee in 'Personnel' sheet."""
        if not self.sheet: return False, "Erreur connexion."
        
        try:
            worksheet = self.sheet.worksheet("Personnel")
            df = self.load_personnel()
            
            # Check for existing
            if not df.empty and "Nom et Prénoms" in df.columns:
                existing_idx = df.index[df["Nom et Prénoms"] == name].tolist()
                
                if existing_idx:
                    # Update row (Google Sheets is 1-indexed, header is row 1, so row = index + 2)
                    row_num = existing_idx[0] + 2
                    # Update Sexe (Col 3) and Service (Col 4)
                    worksheet.update_cell(row_num, 3, sexe)
                    worksheet.update_cell(row_num, 4, service)
                    return True, "Mise à jour effectuée."
                else:
                    # New ID
                    new_id = 1
                    try:
                        if "N° ordre" in df.columns:
                            max_id = pd.to_numeric(df["N° ordre"], errors='coerce').max()
                            new_id = int(max_id) + 1 if pd.notna(max_id) else 1
                    except:
                        pass
                    
                    worksheet.append_row([new_id, name, sexe, service])
                    return True, f"Employé ajouté avec succès. (ID: {new_id})"
            else:
                worksheet.append_row([1, name, sexe, service])
                return True, "Employé ajouté avec succès. (ID: 1)"

        except Exception as e:
            return False, f"Erreur ajout: {e}"

    def delete_employee(self, name):
        """Deletes an employee from 'Personnel' worksheet."""
        if not self.sheet: return False, "Erreur connexion."
        try:
            worksheet = self.sheet.worksheet("Personnel")
            cell = worksheet.find(name)
            if cell:
                worksheet.delete_rows(cell.row)
                return True, "Employé supprimé avec succès."
            return False, "Employé non trouvé."
        except Exception as e:
            return False, f"Erreur suppression: {e}"

    def upsert_entry(self, date_val, name, gender, service, arrival_time, departure_time):
        """Adds or updates an entry in 'Mouvements'."""
        if not self.sheet: return False, "Erreur connexion."
        
        try:
            worksheet = self.sheet.worksheet("Mouvements")
            df = self.load_data()
            
            # Logic to find row index
            row_to_update = None
            if not df.empty:
                # Iterate or filter. Since we need row number, iteration might be safer if not too large
                # Or find by name, then check date?
                # Let's use simple logic: row index corresponds to df index + 2
                
                mask = (df["Nom et Prenoms"].astype(str).str.strip() == str(name).strip()) & \
                       (df["Date"].astype(str) == date_val)
                
                if mask.any():
                    row_idx = df.index[mask][0]
                    row_to_update = row_idx + 2 # Header + 0-based index

            if row_to_update:
                # Update cols: Sexe(4), Service(5), Arr(6), Dep(7)
                # Col indices: 1=Ordre, 2=Date, 3=Nom, 4=Sexe, 5=Service, 6=Arr, 7=Dep
                worksheet.update_cell(row_to_update, 4, gender)
                worksheet.update_cell(row_to_update, 5, service)
                worksheet.update_cell(row_to_update, 6, arrival_time)
                if departure_time:
                    worksheet.update_cell(row_to_update, 7, departure_time)
                
                return True, f"Mise à jour effectuée pour {name} (Date: {date_val})"
            else:
                # INSERT
                new_id = 1
                if not df.empty and "N° ordre" in df.columns:
                    try:
                        max_id = pd.to_numeric(df["N° ordre"], errors='coerce').max()
                        new_id = int(max_id) + 1 if pd.notna(max_id) else 1
                    except:
                        pass
                
                worksheet.append_row([
                    new_id,
                    date_val,
                    name,
                    gender,
                    service,
                    arrival_time,
                    departure_time
                ])
                # Note: prepend not supported by append_row easily, append is end. 
                # Sorting in visualization handles order.
                return True, f"Entrée ajoutée avec succès ! (ID: {new_id})"

        except Exception as e:
            return False, f"Erreur enregistrement: {e}"

    def get_entry_for_today(self, name, date_val):
         # Helper to check local cache or fetch fresh? 
         # For simplicity, we just reload data. In prod, cache this.
         df = self.load_data()
         if df.empty: return None
         mask = (df["Nom et Prenoms"].astype(str).str.strip() == str(name).strip()) & \
                (df["Date"].astype(str) == date_val)
         match = df[mask]
         if not match.empty:
             return match.iloc[0].to_dict()
         return None


