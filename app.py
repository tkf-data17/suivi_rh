import streamlit as st
import pandas as pd
from datetime import datetime
import style
from database import DataManager
import io
import re
import base64
import os
import stats

# Page Configuration
st.set_page_config(
    page_title="Suivi Personnel INH",
    page_icon="📅",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Inject Custom CSS
st.markdown(style.get_custom_css(), unsafe_allow_html=True)

# Initialize Data Manager
if 'db' not in st.session_state:
    st.session_state.db = DataManager()
elif not hasattr(st.session_state.db, 'load_services'):
    # Force reload if old instance doesn't have the new method
    del st.session_state.db
    st.session_state.db = DataManager()

db = st.session_state.db

# Load personnel data (Force reload if specified)
if 'personnel_list' not in st.session_state:
    st.session_state.personnel_list = db.load_personnel()

# Initialize session state for form fields if not present
if 'form_date' not in st.session_state: st.session_state.form_date = datetime.now()
if 'form_name' not in st.session_state: st.session_state.form_name = None
if 'form_sex' not in st.session_state: st.session_state.form_sex = "M"
if 'form_service' not in st.session_state: st.session_state.form_service = "Prélèvements"
# Store times as STRINGS now for text_input
if 'form_arrivee' not in st.session_state: st.session_state.form_arrivee = datetime.now().strftime("%H:%M")
if 'form_depart' not in st.session_state: st.session_state.form_depart = "17:30"
if 'form_save_depart' not in st.session_state: st.session_state.form_save_depart = True
if 'is_update_mode' not in st.session_state: st.session_state.is_update_mode = False

# New Employee Form State
if 'new_emp_name' not in st.session_state: st.session_state.new_emp_name = ""

# Management state
if 'confirm_action_type' not in st.session_state: st.session_state.confirm_action_type = None
if 'confirm_emp_data' not in st.session_state: st.session_state.confirm_emp_data = {}

# --- HELPER FUNCTIONS ---

def get_personnel_info(name):
    """Retrieve Sex and Service for a given name."""
    df_p = st.session_state.personnel_list
    if not df_p.empty and name:
        cols = df_p.columns.tolist()
        name_col = next((c for c in cols if "nom" in c.lower()), None)
        sex_col = next((c for c in cols if "sexe" in c.lower() or "genre" in c.lower()), None)
        service_col = next((c for c in cols if "service" in c.lower() or "département" in c.lower()), None)
        
        if name_col:
            # Flexible matching: exact or contains
            # Ensure column is string for comparison to match dropdown
            mask = df_p[name_col].astype(str).str.strip() == str(name).strip()
            row = df_p[mask]
            
            if not row.empty:
                s_val = row.iloc[0][sex_col] if sex_col else None
                svc_val = row.iloc[0][service_col] if service_col else None
                return s_val, svc_val
    return None, None

def validate_time_format(time_str):
    """Regex validation for HH:MM format"""
    if not time_str: return False
    # Matches 00:00 to 23:59
    pattern = r'^([0-1]?[0-9]|2[0-3]):[0-5][0-9]$'
    return re.match(pattern, time_str) is not None

def update_form_defaults():
    """Callback when name changes"""
    name = st.session_state.form_name
    
    # Reset update mode
    st.session_state.is_update_mode = False
    st.session_state.form_save_depart = True
    
    if name:
        # 1. Update Sex and Service
        s, svc = get_personnel_info(name)
        if s:
            st.session_state.form_sex = s
            st.session_state.form_sex_display = s
        else:
            st.session_state.form_sex = ""
            st.session_state.form_sex_display = ""
            
        if svc:
            st.session_state.form_service = svc
            st.session_state.form_service_display = svc
        else:
            st.session_state.form_service = ""
            st.session_state.form_service_display = ""
            
        # 2. Check for existing entry TODAY
        date_str = st.session_state.form_date.strftime("%d/%m/%Y")
        existing = db.get_entry_for_today(name, date_str)
        
        if existing:
            st.session_state.is_update_mode = True
            st.toast(f"Entrée existante trouvée pour {name}. Mode Modification activé.", icon="✏️")
            
            # Load Arrival Time
            try:
                arr_val = existing.get("Heure d'arrivée", "")
                if arr_val:
                    # Could be time object or string
                    if hasattr(arr_val, 'strftime'):
                         st.session_state.form_arrivee = arr_val.strftime("%H:%M")
                    elif isinstance(arr_val, str):
                        # Clean up 'h' to ':'
                        clean_time = arr_val.replace('h', ':').strip()
                        st.session_state.form_arrivee = clean_time
                    else:
                        st.session_state.form_arrivee = datetime.now().strftime("%H:%M")
            except:
                pass
                
            # Load Departure Time if exists
            dep_val = existing.get("Heure de départ", "")
            if pd.notna(dep_val) and dep_val:
                st.session_state.form_save_depart = True 
                try:
                    if hasattr(dep_val, 'strftime'):
                         st.session_state.form_depart = dep_val.strftime("%H:%M")
                    elif isinstance(dep_val, str):
                        clean_time = dep_val.replace('h', ':').strip()
                        st.session_state.form_depart = clean_time
                    else:
                        st.session_state.form_depart = "17:30"
                except:
                     pass
            else:
                st.session_state.form_save_depart = True 
                st.session_state.form_depart = "17:30"
    else:
        pass
        
    if name and not existing:
         st.session_state.form_depart = "17:30"

def submit_entry_callback():
    """Callback linked to submit button"""
    if not st.session_state.form_name:
         st.session_state.error_msg_entry = "⚠️ Veuillez sélectionner un nom."
         return

    # Validate Time Formats
    ha_input = st.session_state.form_arrivee
    hd_input = st.session_state.form_depart
    
    if not validate_time_format(ha_input):
         st.session_state.error_msg_entry = "⚠️ Format d'heure d'arrivée invalide (Ex: 08:30)"
         return
         
    if st.session_state.form_save_depart and not validate_time_format(hd_input):
         st.session_state.error_msg_entry = "⚠️ Format d'heure de départ invalide (Ex: 17:30)"
         return

    d_str = st.session_state.form_date.strftime("%d/%m/%Y")
    ha_str = ha_input # Already string validated
    hd_str = hd_input if st.session_state.form_save_depart else ""
    
    # Use values directly from session state as they are now read-only derived from name
    final_sex = st.session_state.form_sex
    final_service = st.session_state.form_service

    success, msg = st.session_state.db.upsert_entry(
        d_str, 
        st.session_state.form_name, 
        final_sex, 
        final_service, 
        ha_str, 
        hd_str
    )
    
    if success:
        st.session_state.success_msg_entry = msg
        st.session_state.form_name = None # Reset name selection
        st.session_state.form_save_depart = True
        st.session_state.form_depart = "17:30" # Reset default time
        if 'error_msg_entry' in st.session_state: del st.session_state.error_msg_entry
    else:
        st.session_state.error_msg_entry = "Erreur lors de l'enregistrement."

# --- VIEWS ---

def view_saisie_mouvements():
    st.markdown("<div class='info-card'><h3>📝 Nouvelle Saisie / Modification</h3>", unsafe_allow_html=True)
    
    # Check for success message
    if 'success_msg_entry' in st.session_state and st.session_state.success_msg_entry:
        st.success(st.session_state.success_msg_entry)
        st.session_state.success_msg_entry = None

    # Prepare dropdown list
    personnel_names = []
    if not st.session_state.personnel_list.empty:
        cols = st.session_state.personnel_list.columns.tolist()
        name_col = next((c for c in cols if "nom" in c.lower()), None)
        if name_col:
            personnel_names = st.session_state.personnel_list[name_col].dropna().astype(str).unique().tolist()
            personnel_names.sort()

    # FORM UI
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.date_input("Date", key="form_date", on_change=update_form_defaults)
        # SEXE Display (Read-only)
        current_sex = st.session_state.form_sex or ""
        st.text_input("Sexe", value=current_sex, disabled=True, key="form_sex_display")

    with col2:
        # NAME Selection with Callback
        st.selectbox(
            "Nom et Prénoms", 
            options=[""] + personnel_names,
            key="form_name",
            on_change=update_form_defaults
        )
        
        # SERVICE Display (Read-only)
        current_service = st.session_state.form_service or ""
        st.text_input("Service", value=current_service, disabled=True, key="form_service_display")

    with col3:
            st.text_input("Heure d'arrivée (HH:MM)", key="form_arrivee", max_chars=5, placeholder="08:00")
            st.text_input("Heure de départ (HH:MM)", key="form_depart", max_chars=5, placeholder="17:30")
            st.checkbox("Enregistrer le départ", key="form_save_depart", help="Cochez pour valider l'heure de départ")

    st.markdown("<br>", unsafe_allow_html=True)
    
    # Submit Button with Callback
    btn_label = "Mettre à jour" if st.session_state.get('is_update_mode', False) else "Enregistrer l'entrée"
    st.button(btn_label, type="primary", use_container_width=True, on_click=submit_entry_callback)

    # Check for error msg from callback
    if 'error_msg_entry' in st.session_state and st.session_state.error_msg_entry:
        st.error(st.session_state.error_msg_entry)
        st.session_state.error_msg_entry = None

    st.markdown("</div>", unsafe_allow_html=True)

    # Recent entries preview
    st.markdown("### 🕒 Derniers Enregistrements")
    df = db.load_data()
    if not df.empty:
        # Sort by Order Number Descending (Latest entries first)
        if "N° ordre" in df.columns:
             # Ensure numeric for sorting
             df["N° ordre"] = pd.to_numeric(df["N° ordre"], errors='coerce')
             df = df.sort_values(by="N° ordre", ascending=False)
        st.dataframe(df.head(5), use_container_width=True, hide_index=True)

def view_nouveau_personnel():
    # Calculate total employees
    total_emp = len(st.session_state.personnel_list) if not st.session_state.personnel_list.empty else 0
    
    st.markdown(f"<div class='info-card'><h3>👤 Ajouter un employé <span style='font-size:0.7em; color:#666; float:right'>Total: {total_emp}</span></h3>", unsafe_allow_html=True)
    
    # Success message for this tab
    if 'success_msg_new' in st.session_state and st.session_state.success_msg_new:
        st.success(st.session_state.success_msg_new)
        st.session_state.success_msg_new = None

    # Helper to get consolidated services list
    def get_all_services():
        # 1. Start with services from DB reference sheet
        services = db.load_services()
        
        # 2. Add any services currently attached to employees but not in ref list
        if not st.session_state.personnel_list.empty:
            cols = st.session_state.personnel_list.columns.tolist()
            svc_col = next((c for c in cols if "service" in c.lower()), None)
            if svc_col:
                used_services = st.session_state.personnel_list[svc_col].dropna().astype(str).unique().tolist()
                for s in used_services:
                    if s not in services and s.strip():
                        services.append(s)
        
        # 3. Clean and Sort
        services = sorted(list(set([s.strip() for s in services if s.strip()])))
        
        # 4. Fallback if empty
        if not services:
             services = [
                "Prélèvements", "Parc Auto", "Comptabilité Matière", 
                "Hygiène Assainissement", "Biologie Moléculaire", 
                "Administration", "Autre"
            ]
        
        # Final Sort
        services.sort(key=lambda x: x.lower())
        return services

    all_services = get_all_services()

    with st.form("new_employee_form", clear_on_submit=True):
        col_n1, col_n2 = st.columns(2)
        with col_n1:
            new_nom = st.text_input("Nom de famille")
            new_sex = st.selectbox("Sexe", ["M", "F"])
        with col_n2:
            new_prenoms = st.text_input("Prénoms")
            # Service selection from consolidated list
            # If user wants a new one, they must add it below first
            new_service = st.selectbox("Service", all_services)
        
        st.markdown("<br>", unsafe_allow_html=True)
        submitted_new = st.form_submit_button("Ajouter à la base de données")
        
        if submitted_new:
            if not new_nom or not new_prenoms:
                st.error("Le nom et le prénom sont obligatoires.")
            else:
                # Concatenate Name: NOM (upper) + Prenoms (capitalized/as is)
                full_name = f"{new_nom.strip().upper()} {new_prenoms.strip()}"
                
                success, msg = db.add_employee(full_name, new_sex, new_service)
                if success:
                    st.session_state.success_msg_new = msg
                    # Reload personnel list
                    st.session_state.personnel_list = db.load_personnel()
                    st.rerun()
                else:
                    st.error(msg)
    
    st.markdown("</div>", unsafe_allow_html=True)

    # --- MANAGE SERVICES SECTION ---
    st.markdown("<div class='info-card'><h3>🏢 Gestion des Services</h3>", unsafe_allow_html=True)
    
    if 'success_msg_service' in st.session_state and st.session_state.success_msg_service:
        st.success(st.session_state.success_msg_service)
        st.session_state.success_msg_service = None
    
    col_svc_inp, col_svc_btn = st.columns([3, 1])
    with col_svc_inp:
        new_service_input = st.text_input("Nouveau Service", placeholder="Ex: Ressources Humaines", key="new_svc_add_input")
    
    with col_svc_btn:
        st.write("") # Spacer
        st.write("")
        if st.button("➕ Créer Service", type="primary", use_container_width=True):
            if new_service_input:
                success, msg = db.add_service_ref(new_service_input.strip())
                if success:
                    st.session_state.success_msg_service = msg
                    st.rerun()
                else:
                    st.error(msg)
            else:
                st.error("Nom du service requis.")

    st.markdown("</div>", unsafe_allow_html=True)

    # --- MANAGE EXISTING EMPLOYEES ---
    st.markdown("<div class='info-card'><h3>🛠️ Gérer le personnel existant</h3>", unsafe_allow_html=True)
    
    col_search_emp, col_action_emp = st.columns([2, 1])
    
    personnel_names = []
    if not st.session_state.personnel_list.empty:
         cols = st.session_state.personnel_list.columns.tolist()
         name_col = next((c for c in cols if "nom" in c.lower()), None)
         if name_col:
             personnel_names = st.session_state.personnel_list[name_col].dropna().astype(str).unique().tolist()
             personnel_names.sort()

    with col_search_emp:
        # Reset confirmation on change
        def on_emp_select_change():
            st.session_state.confirm_action_type = None
            st.session_state.confirm_emp_data = {}
            
        selected_emp_manage = st.selectbox(
            "Sélectionner un employé à modifier/supprimer", 
            [""] + personnel_names, 
            key="manage_emp_select",
            on_change=on_emp_select_change
        )
    
    if selected_emp_manage:
        s_current, svc_current = get_personnel_info(selected_emp_manage)
        
        # Determine index for Sex
        sex_idx = 0
        if s_current == "F": sex_idx = 1
        
        # Determine dynamic services for management too
        mgmt_services = get_all_services()

        # Ensure current service is in the list (if it's a weird legacy one)
        if svc_current and svc_current not in mgmt_services:
            mgmt_services.append(svc_current)
            mgmt_services.sort()

        svc_idx = 0
        if svc_current in mgmt_services:
            svc_idx = mgmt_services.index(svc_current)

        # Use columns for layout same as before, but outside st.form for interactivity
        # Prepare content for split name
        parts = selected_emp_manage.split(' ', 1)
        val_nom = parts[0]
        val_prenoms = parts[1] if len(parts) > 1 else ""

        col_m1, col_m2 = st.columns(2)
        with col_m1:
            new_nom_m = st.text_input("Nom de famille", value=val_nom, key=f"m_nom_{selected_emp_manage}")
            new_sex_m = st.selectbox("Sexe", ["M", "F"], index=sex_idx, key="m_sex")
        
        with col_m2:
            new_prenoms_m = st.text_input("Prénoms", value=val_prenoms, key=f"m_prenom_{selected_emp_manage}")
            target_service_m = st.selectbox("Service", mgmt_services, index=svc_idx, key="m_svc_select")

        st.markdown("<br>", unsafe_allow_html=True)

        # Action Buttons
        col_btn1, col_btn2 = st.columns(2)
        
        # Check current confirmation state
        action = st.session_state.confirm_action_type
        
        with col_btn1:
            if st.button("💾 Mettre à jour", type="primary", use_container_width=True):
                st.session_state.confirm_action_type = 'UPDATE'
                if not target_service_m:
                    st.error("Nom du service invalide")
                elif not new_nom_m or not new_prenoms_m:
                    st.error("Nom et Prénoms requis")
                else: 
                    new_full_name = f"{new_nom_m.strip().upper()} {new_prenoms_m.strip()}"
                    st.session_state.confirm_emp_data = {
                        'name': new_full_name,
                        'sex': new_sex_m, 
                        'service': target_service_m,
                        'original_name': selected_emp_manage
                    }
                    st.rerun()

        with col_btn2:
            if st.button("🗑️ Supprimer", type="secondary", use_container_width=True):
                st.session_state.confirm_action_type = 'DELETE'
                st.rerun()
             
        # Confirmation Dialogs
        if st.session_state.confirm_action_type == 'UPDATE':
            # Safe access to current data being confirmed
            c_data = st.session_state.confirm_emp_data
            target_name_display = c_data.get('name', selected_emp_manage)
            
            st.info(f"❓ Confirmer la mise à jour pour **{target_name_display}** ?")
            col_yes, col_no = st.columns(2)
            if col_yes.button("✅ Oui, mettre à jour", use_container_width=True):
                success, msg = db.add_employee(
                    c_data.get('name'), 
                    c_data.get('sex'), 
                    c_data.get('service'),
                    original_name=c_data.get('original_name')
                )
                if success:
                    st.success(f"Détails mis à jour pour {target_name_display}")
                    st.session_state.personnel_list = db.load_personnel()
                    st.session_state.confirm_action_type = None
                    st.rerun()
                else:
                    st.error(msg)
            
            if col_no.button("❌ Annuler", use_container_width=True):
                 st.session_state.confirm_action_type = None
                 st.rerun()

        elif st.session_state.confirm_action_type == 'DELETE':
            st.error(f"⚠️ **ATTENTION** : Vous êtes sur le point de supprimer **{selected_emp_manage}** définitivement.")
            col_yes, col_no = st.columns(2)
            if col_yes.button("🗑️ Oui, supprimer définitivement", type="primary", use_container_width=True):
                success, msg = db.delete_employee(selected_emp_manage)
                if success:
                    st.warning(f"Employé {selected_emp_manage} a été supprimé.")
                    st.session_state.personnel_list = db.load_personnel()
                    st.session_state.confirm_action_type = None
                    # DO NOT reset manage_emp_select manually as it's a widget key, just rerun.
                    # Rerunning will likely reset or refresh the state naturally if the item is gone.
                    # Or we can rely on on_change callback next time.
                    st.rerun()
                else:
                    st.error(msg)
            
            if col_no.button("❌ Annuler", use_container_width=True):
                 st.session_state.confirm_action_type = None
                 st.rerun()

    st.markdown("</div>", unsafe_allow_html=True)

def view_visualisation():
    st.markdown("<div class='info-card'><h3>📊 Bibliothèque des Données</h3>", unsafe_allow_html=True)
    
    df_all = db.load_data()
    
    if not df_all.empty:
        # Sort by Order Number Descending (Latest entries first)
        if "N° ordre" in df_all.columns:
            # Ensure numeric for sorting
            df_all["N° ordre"] = pd.to_numeric(df_all["N° ordre"], errors='coerce')
            df_all = df_all.sort_values(by="N° ordre", ascending=False)
            
        col_search, col_dl = st.columns([3, 1])
        with col_search:
            search_query = st.text_input("Recherche globale", placeholder="Nom, Service, Date...", key="search_visu")
        
        # Filter logic
        filtered_df = df_all.copy()
        if search_query:
            mask = filtered_df.astype(str).apply(lambda x: x.str.contains(search_query, case=False, na=False)).any(axis=1)
            filtered_df = filtered_df[mask]

        with col_dl:
            st.write("") # Spacer
            output = io.BytesIO()
            with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
                filtered_df.to_excel(writer, index=False, sheet_name='Donnees_Export')
            
            st.download_button(
                label="📥 Exporter (.xlsx)",
                data=output.getvalue(),
                file_name=f"export_personnel_{datetime.now().strftime('%Y%m%d_%H%M')}.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            )
        
        st.dataframe(
            filtered_df,
            use_container_width=True,
            height=600,
            hide_index=True,
            column_config={
                "N° ordre": st.column_config.NumberColumn(format="%d"),
            }
        )
        st.caption(f"Affichage de {len(filtered_df)} enregistrements.")
    else:
        st.info("La base de données est vide pour le moment.")
    st.markdown("</div>", unsafe_allow_html=True)

def main():
    
    # Sidebar Navigation
    with st.sidebar:
        st.image("https://cdn-icons-png.flaticon.com/512/2942/2942813.png", width=80)
        st.markdown("### 🏥 Menu Principal")
        
        selection = st.radio(
            "Navigation",
            ["📝 Saisie Mouvements", "➕ Nouveau Personnel", "📊 Visualisation", "📊 Statistiques"],
            label_visibility="collapsed"
        )
        
        st.divider()
        st.info("💡 Sélectionnez une option ci-dessus pour naviguer.")
        st.caption("Version 1.0.2")

    # Header with Logo and Title using HTML/CSS for better alignment
    logo_path = "logo_inh.jpg"
    logo_html = ""
    
    if os.path.exists(logo_path):
        with open(logo_path, "rb") as f:
            data = f.read()
            encoded = base64.b64encode(data).decode()
        logo_html = f'<img src="data:image/jpeg;base64,{encoded}" style="width:100px; height:auto; margin-right:20px;">'
    else:
        logo_html = '<span style="font-size:3rem; margin-right:20px;">🏥</span>'

    st.markdown(
        f"""
        <div style="display: flex; align-items: center; justify-content: start; background-color: white; padding: 10px; border-radius: 10px; margin-bottom: 20px; box-shadow: 0 2px 4px rgba(0,0,0,0.05);">
            {logo_html}
            <h1 style="margin: 0; padding: 0; border: none; text-align: left; color: #2E865F;">Suivi des Arrivées et Départs - INH</h1>
        </div>
        """, 
        unsafe_allow_html=True
    )

    if selection == "📝 Saisie Mouvements":
        view_saisie_mouvements()
    elif selection == "➕ Nouveau Personnel":
        view_nouveau_personnel()
    elif selection == "📊 Visualisation":
        view_visualisation()
    elif selection == "📊 Statistiques":
        stats.view_dashboard(db)

if __name__ == "__main__":
    main()
