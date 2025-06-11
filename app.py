import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import numpy as np
from datetime import datetime, timedelta
import json
import os
from utils.data_generator import DataGenerator
from utils.data_manager import DataManager

# Configuration de la page
st.set_page_config(
    page_title="Dashboard Maintenance Prédictive",
    page_icon="🔧",
    layout="wide",
    initial_sidebar_state="expanded"
)

# CSS personnalisé
st.markdown("""
<style>
    .metric-card {
        background-color: #f0f2f6;
        padding: 1rem;
        border-radius: 0.5rem;
        border-left: 4px solid #1f77b4;
    }
    .status-running { color: #28a745; }
    .status-breakdown { color: #dc3545; }
    .status-stopped { color: #007bff; }
    .status-quality { color: #ffc107; }
    .alert-box {
        padding: 1rem;
        border-radius: 0.5rem;
        margin: 1rem 0;
    }
    .alert-danger { background-color: #f8d7da; border-left: 4px solid #dc3545; }
    .alert-warning { background-color: #fff3cd; border-left: 4px solid #ffc107; }
    .alert-success { background-color: #d4edda; border-left: 4px solid #28a745; }
</style>
""", unsafe_allow_html=True)

# Initialisation des classes utilitaires
@st.cache_resource
def init_data_components():
    data_gen = DataGenerator()
    data_manager = DataManager()
    return data_gen, data_manager

data_generator, data_manager = init_data_components()

# Sidebar pour navigation
st.sidebar.title("🔧 Dashboard Machine de Coupe")
st.sidebar.markdown("---")

# Navigation
page = st.sidebar.selectbox(
    "Choisir le mode",
    ["📊 Suivi Instantané", "📝 Saisie Causes d'Arrêt", "📈 Historique Machine", "⚙️ Configuration"]
)

# Génération de données si nécessaire
if not os.path.exists("data/machine_data.csv"):
    with st.spinner("Génération des données initiales..."):
        data_generator.generate_initial_data()

# Chargement des données
df = data_manager.load_data()

# PAGE 1: SUIVI INSTANTANÉ
if page == "📊 Suivi Instantané":
    st.title("📊 Suivi Instantané de la Machine")
    
    # Actualisation automatique
    col1, col2, col3 = st.columns([2, 1, 1])
    with col1:
        st.markdown("### État Actuel de la Machine")
    with col2:
        if st.button("🔄 Actualiser"):
            st.rerun()
    with col3:
        auto_refresh = st.checkbox("Auto-refresh (30s)")
    
    if auto_refresh:
        st.rerun()
    
    # Données récentes (dernières 6 heures par défaut)
    hours_back = st.sidebar.slider("Période d'affichage (heures)", 1, 24, 6)
    cutoff_time = datetime.now() - timedelta(hours=hours_back)
    recent_data = df[pd.to_datetime(df['timestamp']) >= cutoff_time].copy()
    
    if len(recent_data) == 0:
        st.warning("Aucune donnée disponible pour la période sélectionnée")
        st.stop()
    
    # État actuel
    current_state = recent_data.iloc[-1]
    
    # Métriques principales
    col1, col2, col3, col4 = st.columns(4)
    
    # Statut machine
    status_colors = {
        'en_marche': '🟢',
        'panne': '🔴', 
        'arret_production': '🔵',
        'probleme_qualite': '🟡'
    }
    
    status_labels = {
        'en_marche': 'En Marche',
        'panne': 'Panne',
        'arret_production': 'Arrêt Production', 
        'probleme_qualite': 'Problème Qualité'
    }
    
    with col1:
        st.metric(
            "État Machine",
            f"{status_colors.get(current_state['etat_machine'], '⚪')} {status_labels.get(current_state['etat_machine'], 'Inconnu')}"
        )
    
    with col2:
        st.metric(
            "Vibration X",
            f"{current_state['vibration_x']:.2f} mm/s",
            delta=f"{current_state['vibration_x'] - recent_data['vibration_x'].mean():.2f}"
        )
    
    with col3:
        st.metric(
            "Vibration Y", 
            f"{current_state['vibration_y']:.2f} mm/s",
            delta=f"{current_state['vibration_y'] - recent_data['vibration_y'].mean():.2f}"
        )
    
    with col4:
        st.metric(
            "Vibration Z",
            f"{current_state['vibration_z']:.2f} mm/s", 
            delta=f"{current_state['vibration_z'] - recent_data['vibration_z'].mean():.2f}"
        )
    
    # Alertes
    vibration_threshold = 2.0
    max_vibration = max(current_state['vibration_x'], current_state['vibration_y'], current_state['vibration_z'])
    
    if max_vibration > vibration_threshold:
        st.markdown(f"""
        <div class="alert-box alert-danger">
            <strong>⚠️ ALERTE VIBRATION!</strong><br>
            Vibration détectée: {max_vibration:.2f} mm/s (Seuil: {vibration_threshold} mm/s)
        </div>
        """, unsafe_allow_html=True)
    elif current_state['etat_machine'] == 'panne':
        st.markdown("""
        <div class="alert-box alert-danger">
            <strong>🔴 MACHINE EN PANNE</strong><br>
            Intervention requise
        </div>
        """, unsafe_allow_html=True)
    else:
        st.markdown("""
        <div class="alert-box alert-success">
            <strong>✅ MACHINE OPÉRATIONNELLE</strong><br>
            Fonctionnement normal
        </div>
        """, unsafe_allow_html=True)
    
    # Graphiques
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.subheader("📈 Évolution des Vibrations")
        
        # Graphique des vibrations
        fig_vibrations = make_subplots(
            rows=3, cols=1,
            subplot_titles=('Vibration X', 'Vibration Y', 'Vibration Z'),
            shared_xaxes=True,
            vertical_spacing=0.05
        )
        
        # Ajout des courbes
        fig_vibrations.add_trace(
            go.Scatter(x=recent_data['timestamp'], y=recent_data['vibration_x'], 
                      name='Vibration X', line=dict(color='red')),
            row=1, col=1
        )
        fig_vibrations.add_trace(
            go.Scatter(x=recent_data['timestamp'], y=recent_data['vibration_y'], 
                      name='Vibration Y', line=dict(color='green')),
            row=2, col=1
        )
        fig_vibrations.add_trace(
            go.Scatter(x=recent_data['timestamp'], y=recent_data['vibration_z'], 
                      name='Vibration Z', line=dict(color='blue')),
            row=3, col=1
        )
        
        # Ligne de seuil
        for i in range(1, 4):
            fig_vibrations.add_hline(y=vibration_threshold, line_dash="dash", 
                                   line_color="orange", row=i, col=1)
        
        fig_vibrations.update_layout(height=500, showlegend=False)
        fig_vibrations.update_xaxes(title_text="Temps", row=3, col=1)
        fig_vibrations.update_yaxes(title_text="mm/s")
        
        st.plotly_chart(fig_vibrations, use_container_width=True)
    
    with col2:
        st.subheader("📊 Répartition des États")
        
        # Calcul du temps dans chaque état
        state_duration = recent_data.groupby('etat_machine').size()
        
        # Graphique circulaire
        fig_pie = px.pie(
            values=state_duration.values,
            names=[status_labels.get(state, state) for state in state_duration.index],
            color_discrete_map={
                'En Marche': '#28a745',
                'Panne': '#dc3545', 
                'Arrêt Production': '#007bff',
                'Problème Qualité': '#ffc107'
            }
        )
        fig_pie.update_layout(height=300)
        st.plotly_chart(fig_pie, use_container_width=True)
        
        # Statistiques
        st.subheader("📋 Statistiques")
        total_points = len(recent_data)
        running_time = len(recent_data[recent_data['etat_machine'] == 'en_marche'])
        downtime = total_points - running_time
        
        st.metric("Temps de fonctionnement", f"{(running_time/total_points*100):.1f}%")
        st.metric("Temps d'arrêt", f"{(downtime/total_points*100):.1f}%")
        st.metric("Vibration moyenne", f"{recent_data[['vibration_x', 'vibration_y', 'vibration_z']].mean().mean():.2f} mm/s")

# PAGE 2: SAISIE CAUSES D'ARRÊT
elif page == "📝 Saisie Causes d'Arrêt":
    st.title("📝 Saisie des Causes d'Arrêt")
    
    col1, col2 = st.columns([1, 1])
    
    with col1:
        st.subheader("🔧 Nouveau Rapport d'Arrêt")
        
        with st.form("arret_form"):
            # Sélection de la date/heure
            date_arret = st.date_input("Date de l'arrêt", datetime.now().date())
            heure_arret = st.time_input("Heure de l'arrêt", datetime.now().time())
            
            # Type d'arrêt
            type_arret = st.selectbox(
                "Type d'arrêt",
                ["panne", "changement_serie", "micro_arret", "changement_technique", "defaut_qualite"]
            )
            
            # Sous-catégorie selon le type
            if type_arret == "panne":
                sous_categorie = st.selectbox(
                    "Type de panne",
                    ["Mécanique", "Électrique", "Hydraulique", "Pneumatique", "Autre"]
                )
            elif type_arret == "changement_serie":
                sous_categorie = st.selectbox(
                    "Type de changement",
                    ["Changement produit", "Changement format", "Réglage machine"]
                )
            else:
                sous_categorie = st.text_input("Précision (optionnel)")
            
            # Pièce concernée
            piece_concernee = st.selectbox(
                "Pièce concernée (optionnel)",
                ["", "Moteur principal", "Lame de coupe", "Système hydraulique", 
                 "Capteurs", "Courroie", "Roulements", "Autre"]
            )
            
            # Durée estimée
            duree_minutes = st.number_input("Durée de l'arrêt (minutes)", min_value=1, value=10)
            
            # Commentaire
            commentaire = st.text_area("Commentaire détaillé")
            
            # Opérateur
            operateur = st.text_input("Nom de l'opérateur", value="Opérateur")
            
            submitted = st.form_submit_button("💾 Enregistrer l'arrêt")
            
            if submitted:
                # Création de l'enregistrement
                timestamp_arret = datetime.combine(date_arret, heure_arret)
                
                nouvel_arret = {
                    'timestamp': timestamp_arret,
                    'type_arret': type_arret,
                    'sous_categorie': sous_categorie,
                    'piece_concernee': piece_concernee,
                    'duree_minutes': duree_minutes,
                    'commentaire': commentaire,
                    'operateur': operateur
                }
                
                # Sauvegarde
                data_manager.save_arret(nouvel_arret)
                st.success("✅ Arrêt enregistré avec succès!")
                st.rerun()
    
    with col2:
        st.subheader("📋 Derniers Arrêts Enregistrés")
        
        # Chargement des arrêts
        arrets_df = data_manager.load_arrets()
        
        if len(arrets_df) > 0:
            # Affichage des 10 derniers arrêts
            recent_arrets = arrets_df.head(10)
            
            for idx, arret in recent_arrets.iterrows():
                with st.expander(f"🔧 {arret['type_arret']} - {arret['timestamp'].strftime('%d/%m/%Y %H:%M')}"):
                    col_a, col_b = st.columns(2)
                    with col_a:
                        st.write(f"**Type:** {arret['type_arret']}")
                        st.write(f"**Sous-catégorie:** {arret['sous_categorie']}")
                        st.write(f"**Durée:** {arret['duree_minutes']} min")
                    with col_b:
                        st.write(f"**Pièce:** {arret['piece_concernee']}")
                        st.write(f"**Opérateur:** {arret['operateur']}")
                    if arret['commentaire']:
                        st.write(f"**Commentaire:** {arret['commentaire']}")
        else:
            st.info("Aucun arrêt enregistré pour le moment")
    
    # Statistiques des arrêts
    st.markdown("---")
    st.subheader("📊 Statistiques des Arrêts")
    
    if len(data_manager.load_arrets()) > 0:
        arrets_stats = data_manager.load_arrets()
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            # Répartition par type
            fig_type = px.pie(
                arrets_stats.groupby('type_arret').size().reset_index(name='count'),
                values='count', names='type_arret',
                title="Répartition par Type d'Arrêt"
            )
            st.plotly_chart(fig_type, use_container_width=True)
        
        with col2:
            # Durée moyenne par type
            duree_moyenne = arrets_stats.groupby('type_arret')['duree_minutes'].mean()
            fig_duree = px.bar(
                x=duree_moyenne.index, y=duree_moyenne.values,
                title="Durée Moyenne par Type (min)"
            )
            st.plotly_chart(fig_duree, use_container_width=True)
        
        with col3:
            # Évolution dans le temps
            arrets_stats['date'] = pd.to_datetime(arrets_stats['timestamp']).dt.date
            evolution = arrets_stats.groupby('date').size()
            fig_evolution = px.line(
                x=evolution.index, y=evolution.values,
                title="Évolution des Arrêts"
            )
            st.plotly_chart(fig_evolution, use_container_width=True)

# PAGE 3: HISTORIQUE MACHINE
elif page == "📈 Historique Machine":
    st.title("📈 Historique de la Machine")
    
    # Filtres
    st.sidebar.subheader("🔍 Filtres")
    
    # Période
    date_debut = st.sidebar.date_input("Date de début", datetime.now().date() - timedelta(days=7))
    date_fin = st.sidebar.date_input("Date de fin", datetime.now().date())
    
    # État machine
    etats_selectionnes = st.sidebar.multiselect(
        "États à afficher",
        ['en_marche', 'panne', 'arret_production', 'probleme_qualite'],
        default=['en_marche', 'panne', 'arret_production', 'probleme_qualite']
    )
    
    # Filtrage des données
    df_filtered = df[
        (pd.to_datetime(df['timestamp']).dt.date >= date_debut) &
        (pd.to_datetime(df['timestamp']).dt.date <= date_fin) &
        (df['etat_machine'].isin(etats_selectionnes))
    ].copy()
    
    if len(df_filtered) == 0:
        st.warning("Aucune donnée disponible pour les filtres sélectionnés")
        st.stop()
    
    # KPIs
    st.subheader("📊 Indicateurs de Performance (KPI)")
    
    col1, col2, col3, col4 = st.columns(4)
    
    total_points = len(df_filtered)
    temps_marche = len(df_filtered[df_filtered['etat_machine'] == 'en_marche'])
    temps_panne = len(df_filtered[df_filtered['etat_machine'] == 'panne'])
    temps_arret = len(df_filtered[df_filtered['etat_machine'] == 'arret_production'])
    
    with col1:
        st.metric("TBF (Temps Brut Fonctionnement)", f"{(temps_marche/total_points*100):.1f}%")
    
    with col2:
        st.metric("Temps de Panne", f"{(temps_panne/total_points*100):.1f}%")
    
    with col3:
        st.metric("Temps d'Arrêt Production", f"{(temps_arret/total_points*100):.1f}%")
    
    with col4:
        disponibilite = (temps_marche + temps_arret) / total_points * 100
        st.metric("Disponibilité", f"{disponibilite:.1f}%")
    
    # Graphiques historiques
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.subheader("📈 Évolution Temporelle")
        
        # Graphique principal avec états et vibrations
        fig_hist = make_subplots(
            rows=2, cols=1,
            subplot_titles=('États de la Machine', 'Vibrations'),
            shared_xaxes=True,
            vertical_spacing=0.1,
            row_heights=[0.3, 0.7]
        )
        
        # États machine (codés numériquement pour l'affichage)
        state_mapping = {'en_marche': 1, 'arret_production': 2, 'panne': 3, 'probleme_qualite': 4}
        df_filtered['etat_numeric'] = df_filtered['etat_machine'].map(state_mapping)
        
        fig_hist.add_trace(
            go.Scatter(x=df_filtered['timestamp'], y=df_filtered['etat_numeric'],
                      mode='markers', name='État Machine',
                      marker=dict(size=8, color=df_filtered['etat_numeric'], 
                                colorscale='Viridis')),
            row=1, col=1
        )
        
        # Vibrations
        fig_hist.add_trace(
            go.Scatter(x=df_filtered['timestamp'], y=df_filtered['vibration_x'],
                      name='Vibration X', line=dict(color='red')),
            row=2, col=1
        )
        fig_hist.add_trace(
            go.Scatter(x=df_filtered['timestamp'], y=df_filtered['vibration_y'],
                      name='Vibration Y', line=dict(color='green')),
            row=2, col=1
        )
        fig_hist.add_trace(
            go.Scatter(x=df_filtered['timestamp'], y=df_filtered['vibration_z'],
                      name='Vibration Z', line=dict(color='blue')),
            row=2, col=1
        )
        
        fig_hist.update_layout(height=600)
        fig_hist.update_xaxes(title_text="Temps", row=2, col=1)
        fig_hist.update_yaxes(title_text="État", row=1, col=1)
        fig_hist.update_yaxes(title_text="Vibration (mm/s)", row=2, col=1)
        
        st.plotly_chart(fig_hist, use_container_width=True)
    
    with col2:
        st.subheader("📊 Analyses")
        
        # Distribution des vibrations
        st.write("**Distribution des Vibrations**")
        vibrations_combined = pd.concat([
            df_filtered['vibration_x'],
            df_filtered['vibration_y'], 
            df_filtered['vibration_z']
        ])
        
        fig_dist = px.histogram(vibrations_combined, nbins=30, title="Distribution")
        fig_dist.update_layout(height=250)
        st.plotly_chart(fig_dist, use_container_width=True)
        
        # Corrélations
        st.write("**Matrice de Corrélation**")
        corr_matrix = df_filtered[['vibration_x', 'vibration_y', 'vibration_z']].corr()
        fig_corr = px.imshow(corr_matrix, text_auto=True, aspect="auto")
        fig_corr.update_layout(height=250)
        st.plotly_chart(fig_corr, use_container_width=True)
    
    # Export des données
    st.markdown("---")
    st.subheader("💾 Export des Données")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("📥 Télécharger CSV"):
            csv = df_filtered.to_csv(index=False)
            st.download_button(
                label="💾 Télécharger le fichier CSV",
                data=csv,
                file_name=f"historique_machine_{date_debut}_{date_fin}.csv",
                mime="text/csv"
            )
    
    with col2:
        if st.button("📥 Télécharger JSON"):
            json_data = df_filtered.to_json(orient='records', date_format='iso')
            st.download_button(
                label="💾 Télécharger le fichier JSON",
                data=json_data,
                file_name=f"historique_machine_{date_debut}_{date_fin}.json",
                mime="application/json"
            )
    
    with col3:
        # Rapport de synthèse
        if st.button("📄 Générer Rapport"):
            rapport = data_manager.generate_report(df_filtered, date_debut, date_fin)
            st.download_button(
                label="💾 Télécharger le rapport",
                data=rapport,
                file_name=f"rapport_machine_{date_debut}_{date_fin}.txt",
                mime="text/plain"
            )

# PAGE 4: CONFIGURATION
elif page == "⚙️ Configuration":
    st.title("⚙️ Configuration du Système")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("🔧 Paramètres Machine")
        
        # Seuils d'alerte
        st.write("**Seuils de Vibration**")
        seuil_vibration = st.slider("Seuil d'alerte vibration (mm/s)", 0.5, 5.0, 2.0, 0.1)
        seuil_critique = st.slider("Seuil critique vibration (mm/s)", 2.0, 10.0, 4.0, 0.1)
        
        # Paramètres de génération de données
        st.write("**Génération de Données**")
        if st.button("🔄 Générer Nouvelles Données"):
            with st.spinner("Génération en cours..."):
                data_generator.generate_additional_data(hours=24)
            st.success("✅ Nouvelles données générées!")
            st.rerun()
        
        # Nettoyage des données
        st.write("**Maintenance des Données**")
        if st.button("🗑️ Nettoyer Anciennes Données"):
            data_manager.cleanup_old_data(days=30)
            st.success("✅ Données anciennes supprimées!")
    
    with col2:
        st.subheader("📊 Statistiques Système")
        
        # Informations sur les données
        total_records = len(df)
        date_debut_data = df['timestamp'].min()
        date_fin_data = df['timestamp'].max()
        
        st.metric("Total d'enregistrements", total_records)
        st.metric("Première donnée", pd.to_datetime(date_debut_data).strftime('%d/%m/%Y %H:%M'))
        st.metric("Dernière donnée", pd.to_datetime(date_fin_data).strftime('%d/%m/%Y %H:%M'))
        
        # Espace disque
        import os
        data_size = os.path.getsize("data/machine_data.csv") / 1024 / 1024  # MB
        st.metric("Taille des données", f"{data_size:.2f} MB")
        
        # Qualité des données
        missing_data = df.isnull().sum().sum()
        data_quality = (1 - missing_data / (len(df) * len(df.columns))) * 100
        st.metric("Qualité des données", f"{data_quality:.1f}%")

# Footer
st.markdown("---")
st.markdown("""
<div style='text-align: center; color: #666;'>
    <p>Dashboard Maintenance Prédictive v1.0 | Développé avec Streamlit</p>
    <p>🔧 Machine de Coupe Industrielle | 📊 Données simulées pour démonstration</p>
</div>
""", unsafe_allow_html=True)
