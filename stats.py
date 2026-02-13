import streamlit as st
import pandas as pd
import altair as alt
from datetime import datetime, timedelta

def view_dashboard(db):
    """
    Displays the dashboard with key metrics and statistics.
    """
    # 1. Load Data
    df_mouvements = db.load_data()  # Returns DataFrame of movements
    df_personnel = db.load_personnel() # Returns DataFrame of personnel

    # Container
    st.markdown("<div class='info-card'><h3>📊 Tableau de Bord Analytique</h3>", unsafe_allow_html=True)
    
    if df_mouvements.empty:
        st.info("Données insuffisantes pour générer des graphiques.")
        st.markdown("</div>", unsafe_allow_html=True)
        return

    # --- DATE FILTERS ---
    # Pre-processing for Date
    df_chart = df_mouvements.copy()
    if "Date" in df_chart.columns:
        df_chart['Date_dt'] = pd.to_datetime(df_chart['Date'], dayfirst=True, errors='coerce')
        df_chart = df_chart.dropna(subset=['Date_dt'])
    
    # Get Mix/Max dates for default
    min_date = df_chart['Date_dt'].min().date() if not df_chart.empty else datetime.now().date()
    max_date = df_chart['Date_dt'].max().date() if not df_chart.empty else datetime.now().date()
    
    col_filter1, col_filter2 = st.columns([2, 2])
    with col_filter1:
        date_range = st.date_input(
            "📅 Filtrer par Période",
            value=(min_date, max_date),
            min_value=min_date,
            max_value=datetime.now().date() + timedelta(days=365) # Allow future if needed, but usually past
        )
    
    # Filter Logic
    start_date, end_date = min_date, max_date
    if isinstance(date_range, tuple):
        if len(date_range) == 2:
            start_date, end_date = date_range
        elif len(date_range) == 1:
            start_date = date_range[0]
            end_date = start_date

    # Apply Filter
    mask_date = (df_chart['Date_dt'].dt.date >= start_date) & (df_chart['Date_dt'].dt.date <= end_date)
    df_filter = df_chart[mask_date].copy()

    # --- KPI HEADER ---
    col1, col2, col3, col4 = st.columns(4)
    
    # Metric 1: Total Employees (Static, from DB)
    total_emp = len(df_personnel) if not df_personnel.empty else 0
    col1.metric("👥 Total Personnel", total_emp)
    
    # Metric 2: Total Movements (Filtered)
    total_mov = len(df_filter)
    col2.metric("📝 Enregistrements", total_mov)
    
    # Metric 3: Today's Count (Static context usually, but let's keep it real-time independent of filter?)
    # User might want to see "Today" regardless of filter, OR filtered today. 
    # Let's keep "Today" as absolute "Today" for dashboard awareness.
    today_str = datetime.now().strftime("%d/%m/%Y")
    today_count = 0
    if not df_mouvements.empty and "Date" in df_mouvements.columns:
        today_mask = df_mouvements["Date"].astype(str) == today_str
        today_count = len(df_mouvements[today_mask])
    
    col3.metric("📅 Aujourd'hui (Global)", today_count)

    # Metric 4: Active Departments (Filtered)
    unique_services = 0
    if not df_filter.empty and "Service" in df_filter.columns:
        unique_services = df_filter["Service"].nunique()
    col4.metric("🏢 Services Actifs", unique_services)

    st.markdown("---")

    if df_filter.empty:
        st.warning(f"Aucune donnée trouvée pour la période du {start_date} au {end_date}.")
        st.markdown("</div>", unsafe_allow_html=True)
        return

    # --- CHARTS SECTION ---
    c_chart1, c_chart2 = st.columns(2)
    
    with c_chart1:
        st.markdown("#### 🥧 Répartition par Service")
        if "Service" in df_filter.columns:
            service_counts = df_filter["Service"].value_counts().reset_index()
            service_counts.columns = ["Service", "Nombre"]
            
            bar_chart = alt.Chart(service_counts).mark_bar(cornerRadiusTopLeft=3, cornerRadiusTopRight=3).encode(
                x=alt.X('Service', sort='-y', axis=alt.Axis(labelAngle=-45)),
                y='Nombre',
                color=alt.Color('Service', legend=None),
                tooltip=['Service', 'Nombre']
            ).properties(height=300)
            st.altair_chart(bar_chart, use_container_width=True)
            
    with c_chart2:
        st.markdown("#### 📈 Évolution des entrées")
        if "Date_dt" in df_filter.columns:
            daily_counts = df_filter.groupby('Date_dt').size().reset_index(name='Nombre')
            daily_counts = daily_counts.sort_values('Date_dt')
            
            line_chart = alt.Chart(daily_counts).mark_line(point=True, interpolate='monotone').encode(
                x=alt.X('Date_dt', axis=alt.Axis(format='%d/%m', title='Date')),
                y='Nombre',
                tooltip=[alt.Tooltip('Date_dt', format='%d/%m/%Y', title='Date'), 'Nombre']
            ).properties(height=300)
            st.altair_chart(line_chart, use_container_width=True)

    # --- ADVANCED ANALYSIS ---
    st.markdown("---")
    st.subheader("🔍 Analyse détaillée")
    
    tab1, tab2 = st.tabs(["👤 Par Employé & Tendances", "🏢 Par Service"])
    
    # TAB 1: Employee Stats
    with tab1:
        col_select, col_stats = st.columns([1, 2])
        
        with col_select:
            names_list = []
            if not df_personnel.empty and "Nom et Prénoms" in df_personnel.columns:
                names_list = sorted(df_personnel["Nom et Prénoms"].astype(str).unique().tolist())
            
            selected_emp = st.selectbox("Choisir un employé :", [""] + names_list)
        
        with col_stats:
            if selected_emp:
                # Filter movements for this employee (within global date filter)
                # Normalize case and whitespace for comparison
                mask_emp = df_filter["Nom et Prenoms"].astype(str).str.strip().str.upper() == str(selected_emp).strip().upper()
                emp_data = df_filter[mask_emp].sort_values(by="Date_dt", ascending=False)
                
                if not emp_data.empty:
                    # Specific Metrics
                    last_visit = emp_data.iloc[0]["Date"]
                    last_time = emp_data.iloc[0].get("Heure d'arrivée", "-")
                    total_visits = len(emp_data)
                    
                    m1, m2, m3 = st.columns(3)
                    m1.metric("Total sur Période", total_visits)
                    m2.metric("Dernière Date", last_visit)
                    m3.metric("Dernière Arrivée", last_time)

                    # --- TREND CHART (Hours) ---
                    st.markdown("##### ⏱️ Tendance des Horaires (Arrivée vs Départ)")
                    
                    # Prepare data for plotting
                    # We need to normalize time to a dummy date to plot on Y-axis
                    chart_data = emp_data.copy().sort_values("Date_dt")
                    
                    # Function to convert HH:MM string to datetime on a dummy day
                    def parse_time_to_dummy(t_str):
                        if not isinstance(t_str, str): return None
                        try:
                            t_str = t_str.replace('h', ':').strip()
                            t = datetime.strptime(t_str, "%H:%M").time()
                            return datetime.combine(datetime(2000, 1, 1), t)
                        except:
                            return None

                    chart_data['Arrival_DT'] = chart_data["Heure d'arrivée"].apply(parse_time_to_dummy)
                    chart_data['Departure_DT'] = chart_data["Heure de départ"].apply(parse_time_to_dummy)

                    # Melt for dual line chart
                    melted = chart_data.melt(
                        id_vars=['Date_dt'], 
                        value_vars=['Arrival_DT', 'Departure_DT'],
                        var_name='Type', 
                        value_name='Time_Value'
                    ).dropna(subset=['Time_Value'])
                    
                    # Map readable names
                    melted['Type'] = melted['Type'].map({'Arrival_DT': 'Arrivée', 'Departure_DT': 'Départ'})

                    if not melted.empty:
                        # Time Axis formatting
                        hours_chart = alt.Chart(melted).mark_line(point=True).encode(
                            x=alt.X('Date_dt', axis=alt.Axis(format='%d/%m', title='Date')),
                            y=alt.Y('Time_Value', axis=alt.Axis(format='%H:%M', title='Heure')),
                            color=alt.Color('Type', scale=alt.Scale(domain=['Arrivée', 'Départ'], range=['green', 'red'])),
                            tooltip=[
                                alt.Tooltip('Date_dt', format='%d/%m/%Y', title='Date'),
                                alt.Tooltip('Type', title='Type'),
                                alt.Tooltip('Time_Value', format='%H:%M', title='Heure')
                            ]
                        ).properties(height=300)
                        
                        st.altair_chart(hours_chart, use_container_width=True)
                    else:
                        st.info("Pas assez de données horaires valides pour le graphique.")
                    
                    st.caption("Historique récent (filtré) :")
                    st.dataframe(
                        emp_data[["Date", "Heure d'arrivée", "Heure de départ", "Service"]].head(5),
                        hide_index=True,
                        use_container_width=True
                    )
                else:
                    st.warning(f"Aucun mouvement enregistré pour {selected_emp} sur cette période.")
            else:
                st.info("Sélectionnez un employé pour voir ses statistiques personnelles.")

    # TAB 2: Service Stats
    with tab2:
        if "Service" in df_filter.columns:
            # Group by Service
            grouped_svc = df_filter.groupby("Service").size().reset_index(name="Total Mouvements")
            # Calculate unique people per service seen
            people_per_svc = df_filter.groupby("Service")["Nom et Prenoms"].nunique().reset_index(name="Employés Uniques")
            
            merged_stats = pd.merge(grouped_svc, people_per_svc, on="Service")
            
            st.dataframe(
                merged_stats.style.background_gradient(cmap="Greens"), 
                use_container_width=True,
                hide_index=True
            )
        else:
            st.error("Colonne 'Service' manquante dans les données.")

    st.markdown("</div>", unsafe_allow_html=True)
