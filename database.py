import pandas as pd
import os
from datetime import datetime

class DataManager:
    def __init__(self, file_path="suivi_employes.xlsx"):
        self.file_path = file_path
        self.columns = [
            "N° ordre", 
            "Date", 
            "Nom et Prenoms", 
            "Sexe", 
            "Service", 
            "Heure d'arrivée", 
            "Heure de départ"
        ]
        self.personnel_file = "liste personnel.xlsx"
        self._ensure_file_exists()

    def _ensure_file_exists(self):
        """Creates the excel file if it doesn't exist."""
        if not os.path.exists(self.file_path):
            df = pd.DataFrame(columns=self.columns)
            df.to_excel(self.file_path, index=False)

    def load_data(self):
        """Loads data from the excel file."""
        try:
            return pd.read_excel(self.file_path)
        except Exception as e:
            return pd.DataFrame(columns=self.columns)

    def load_personnel(self):
        """Loads personnel list from JSON for dropdowns and returns a DataFrame."""
        json_path = "personnel.json"
        
        # If JSON doesn't exist but Excel does, convert on the fly
        if not os.path.exists(json_path) and os.path.exists(self.personnel_file):
            try:
                df = pd.read_excel(self.personnel_file)
                # Save as JSON for future use
                df.to_json(json_path, orient='records', force_ascii=False, indent=4)
                return df
            except:
                pass
                
        try:
            if os.path.exists(json_path):
                return pd.read_json(json_path, orient='records')
            return pd.DataFrame()
        except Exception:
            # Fallback to empty if error
            return pd.DataFrame()

    def add_employee(self, name, sexe, service):
        """Adds a new employee to the personnel JSON file."""
        json_path = "personnel.json"
        new_record = {"Nom et Prénoms": name, "Sexe": sexe, "Service": service}
        
        try:
            df = self.load_personnel()
            new_df = pd.DataFrame([new_record])
            
            # Check for duplicates? For now, we allow details to be updated or new entries
             # If name exists, maybe update? Or just append.
             # User said "add function", let's assume append or update if exists.
            
            if not df.empty and "Nom et Prénoms" in df.columns:
                 # If name exists, update it
                 if name in df["Nom et Prénoms"].values:
                     df.loc[df["Nom et Prénoms"] == name, ["Sexe", "Service"]] = [sexe, service]
                     msg = "Mise à jour effectuée."
                 else:
                     df = pd.concat([df, new_df], ignore_index=True)
                     msg = "Employé ajouté avec succès."
            else:
                 df = new_df
                 msg = "Employé ajouté avec succès."
            
            # Save back to JSON
            df.to_json(json_path, orient='records', force_ascii=False, indent=4)
            return True, msg
        except Exception as e:
            return False, f"Erreur ajout: {e}"

    def delete_employee(self, name):
        """Deletes an employee from the personnel JSON file."""
        json_path = "personnel.json"
        
        try:
            df = self.load_personnel()
            if not df.empty and "Nom et Prénoms" in df.columns:
                if name in df["Nom et Prénoms"].values:
                    df = df[df["Nom et Prénoms"] != name]
                    df.to_json(json_path, orient='records', force_ascii=False, indent=4)
                    return True, "Employé supprimé avec succès."
            return False, "Employé non trouvé."
        except Exception as e:
            return False, f"Erreur suppression: {e}"

    def save_data(self, df):
        """Saves the dataframe to the excel file and a JSON backup."""
        # Save Excel
        df.to_excel(self.file_path, index=False)
        
        # Save JSON Backup
        try:
            json_backup_path = self.file_path.replace(".xlsx", ".json")
            # Convert datetime objects to string for JSON serialization if needed, 
            # though pandas to_json usually handles it (ISO format).
            df.to_json(json_backup_path, orient='records', force_ascii=False, indent=4, date_format='iso')
        except Exception as e:
            print(f"Warning: Could not save JSON backup: {e}")

    def get_entry_for_today(self, name, date_val):
        """Checks if an entry exists for the given name and date."""
        try:
            df = self.load_data()
            if df.empty:
                return None
            
            # Filter by matching Name and Date
            # Ensure types match. Excel date might be string or datetime.
            # date_val passed from st.date_input is a date object.
            # Converting to string format DD/MM/YYYY might be safest for comparison if that's how we save.
            
            # We save as %d/%m/%Y in execute_entry (d_str).
            # So we compare strings.
            
            mask = (df["Nom et Prenoms"].astype(str).str.strip() == str(name).strip()) & \
                   (df["Date"].astype(str) == date_val)
            
            match = df[mask]
            if not match.empty:
                return match.iloc[0].to_dict()
            return None
        except Exception:
            return None

    def upsert_entry(self, date_val, name, gender, service, arrival_time, departure_time):
        """Adds or updates an entry based on Date and Name."""
        df = self.load_data()
        
        # Check if exists
        mask = (df["Nom et Prenoms"].astype(str).str.strip() == str(name).strip()) & \
               (df["Date"].astype(str) == date_val)
               
        if mask.any():
            # UPDATE existing
            idx = df.index[mask][0]
            # Update fields
            # We preserve arrival time if it was already there and user didn't change it?
            # Actually, the user passes the desired state. So we overwrite.
            # However, we must ensure we don't accidentally wipe data if user passed empty?
            # The form passes whatever is in the inputs.
            
            df.at[idx, "Sexe"] = gender
            df.at[idx, "Service"] = service
            df.at[idx, "Heure d'arrivée"] = arrival_time
            if departure_time: # Only update departure if provided, or allow clearing?
                df.at[idx, "Heure de départ"] = departure_time
            
            self.save_data(df)
            return True, f"Mise à jour effectuée pour {name} (Date: {date_val})"
            
        else:
            # INSERT new
            if df.empty:
                new_id = 1
            else:
                try:
                    max_id = pd.to_numeric(df["N° ordre"], errors='coerce').max()
                    new_id = int(max_id) + 1 if pd.notna(max_id) else 1
                except:
                    new_id = 1
                    
            new_entry = pd.DataFrame([{
                "N° ordre": new_id,
                "Date": date_val,
                "Nom et Prenoms": name,
                "Sexe": gender,
                "Service": service,
                "Heure d'arrivée": arrival_time,
                "Heure de départ": departure_time
            }])
            
            updated_df = pd.concat([new_entry, df], ignore_index=True)
            self.save_data(updated_df)
            return True, f"Entrée ajoutée avec succès ! (ID: {new_id})"
