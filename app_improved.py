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

# CSS personnalisé amélioré
st.markdown("""
<style>
    .metric-card {
        background-color: #f0f2f6;
        padding: 1rem;
        border-radius: 0.5rem;
        border-left: 4px solid #1f77b4;
    }
    .arret-card {
        padding: 1rem;
        border-radius: 0.5rem;
        margin: 0.5rem 0;
        border-left: 4px solid;
    }
    .arret-maintenance { border-left-color: #1f4e79; background-color: #e8f4fd; }
    .arret-prevu { border-left-color: #40e0d0; background-color: #e0fffe; }
    .arret-imprevu { border-left-color: #9932cc; background-color: #f5e8ff; }
    .arret-conducteur { border-left-color: #ffd700; background-color: #fffde8; }
    .arret-qualite { border-left-color: #ff0000; background-color: #ffe8e8; }
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
    .alert-info { background-color: #d1ecf1; border-left: 4px solid #17a2b8; }
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
    ["📊 Suivi Instantané", "📝 Saisie Causes d'Arrêt", "🤖 Détection Automatique", "📈 Historique Machine", "⚙️ Configuration"]
)

# Génération de données si nécessaire
if not os.path.exists("data/machine_data.csv"):
    with st.spinner("Génération des données initiales..."):
        data_generator.generate_initial_data()

# Chargement des données
df = data_manager.load_data()

# PAGE: SAISIE CAUSES D'ARRÊT AMÉLIORÉE
if page == "📝 Saisie Causes d'Arrêt":
    st.title("📝 Saisie des Causes d'Arrêt")
    
    # Onglets pour organiser les fonctionnalités
    tab1, tab2, tab3 = st.tabs(["🔧 Nouveau Rapport", "📋 Arrêts Récents", "📊 Statistiques"])
    
    with tab1:
        col1, col2 = st.columns([1, 1])
        
        with col1:
            st.subheader("🔧 Nouveau Rapport d'Arrêt")
            
            with st.form("arret_form_improved"):
                # Sélection de la date/heure
                date_arret = st.date_input("Date de l'arrêt", datetime.now().date())
                heure_arret = st.time_input("Heure de l'arrêt", datetime.now().time())
                
                # Type d'arrêt selon le nouveau diagramme
                type_arret = st.selectbox(
                    "Type d'arrêt",
                    list(data_manager.types_arrets.keys()),
                    format_func=lambda x: data_manager.types_arrets[x]['label']
                )
                
                # Sous-catégorie dynamique selon le type
                sous_categories = data_manager.types_arrets[type_arret]['sous_categories']
                sous_categorie = st.selectbox("Sous-catégorie", sous_categories)
                
                # Pièce concernée (optionnel)
                piece_concernee = st.selectbox(
                    "Pièce concernée (optionnel)",
                    ["", "Moteur principal", "Lame de coupe", "Système hydraulique", 
                     "Capteurs", "Courroie", "Roulements", "Système électrique", "Autre"]
                )
                
                # Durée estimée
                duree_minutes = st.number_input("Durée de l'arrêt (minutes)", min_value=1, value=10)
                
                # Commentaire détaillé
                commentaire = st.text_area("Commentaire détaillé", height=100)
                
                # Opérateur
                operateur = st.text_input("Nom de l'opérateur", value="Opérateur")
                
                # Priorité/Urgence
                urgence = st.selectbox("Niveau d'urgence", ["Faible", "Moyen", "Élevé", "Critique"])
                
                submitted = st.form_submit_button("💾 Enregistrer l'arrêt", use_container_width=True)
                
                if submitted:
                    timestamp_arret = datetime.combine(date_arret, heure_arret)
                    
                    nouvel_arret = {
                        'timestamp': timestamp_arret,
                        'type_arret': type_arret,
                        'sous_categorie': sous_categorie,
                        'piece_concernee': piece_concernee,
                        'duree_minutes': duree_minutes,
                        'commentaire': commentaire,
                        'operateur': operateur,
                        'urgence': urgence,
                        'date_saisie': datetime.now()
                    }
                    
                    data_manager.save_arret(nouvel_arret)
                    st.success("✅ Arrêt enregistré avec succès!")
                    st.rerun()
        
        with col2:
            st.subheader("🎨 Aperçu de la Classification")
            
            # Affichage des types d'arrêts avec couleurs
            for type_key, type_info in data_manager.types_arrets.items():
                color = type_info['color']
                label = type_info['label']
                
                st.markdown(f"""
                <div class="arret-card" style="border-left-color: {color}; background-color: {color}20;">
                    <strong style="color: {color};">● {label}</strong><br>
                    <small>Sous-catégories: {', '.join(type_info['sous_categories'][:3])}{'...' if len(type_info['sous_categories']) > 3 else ''}</small>
                </div>
                """, unsafe_allow_html=True)
    
    with tab2:
        st.subheader("📋 Derniers Arrêts Enregistrés")
        
        # Chargement des arrêts
        arrets_df = data_manager.load_arrets()
        
        if len(arrets_df) > 0:
            # Filtres
            col_filter1, col_filter2 = st.columns(2)
            with col_filter1:
                filtre_type = st.multiselect(
                    "Filtrer par type",
                    list(data_manager.types_arrets.keys()),
                    format_func=lambda x: data_manager.types_arrets[x]['label']
                )
            with col_filter2:
                filtre_operateur = st.multiselect(
                    "Filtrer par opérateur",
                    arrets_df['operateur'].unique()
                )
            
            # Application des filtres
            arrets_filtered = arrets_df.copy()
            if filtre_type:
                arrets_filtered = arrets_filtered[arrets_filtered['type_arret'].isin(filtre_type)]
            if filtre_operateur:
                arrets_filtered = arrets_filtered[arrets_filtered['operateur'].isin(filtre_operateur)]
            
            # Affichage des arrêts
            for idx, arret in arrets_filtered.head(10).iterrows():
                type_info = data_manager.types_arrets.get(arret['type_arret'], {'color': '#666666', 'label': arret['type_arret']})
                color = type_info['color']
                
                with st.expander(f"🔧 {type_info['label']} - {arret['timestamp'].strftime('%d/%m/%Y %H:%M')}"):
                    col_a, col_b, col_c = st.columns(3)
                    with col_a:
                        st.write(f"**Type:** {type_info['label']}")
                        st.write(f"**Sous-catégorie:** {arret['sous_categorie']}")
                        st.write(f"**Durée:** {arret['duree_minutes']} min")
                    with col_b:
                        st.write(f"**Pièce:** {arret.get('piece_concernee', 'Non spécifiée')}")
                        st.write(f"**Opérateur:** {arret['operateur']}")
                        st.write(f"**Urgence:** {arret.get('urgence', 'Non spécifiée')}")
                    with col_c:
                        if arret.get('commentaire'):
                            st.write(f"**Commentaire:** {arret['commentaire']}")
        else:
            st.info("Aucun arrêt enregistré pour le moment")
    
    with tab3:
        st.subheader("📊 Statistiques des Arrêts")
        
        if len(data_manager.load_arrets()) > 0:
            arrets_stats = data_manager.load_arrets()
            
            # Métriques principales
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                st.metric("Total arrêts", len(arrets_stats))
            with col2:
                st.metric("Durée totale", f"{arrets_stats['duree_minutes'].sum():.0f} min")
            with col3:
                st.metric("Durée moyenne", f"{arrets_stats['duree_minutes'].mean():.1f} min")
            with col4:
                arrets_aujourd_hui = len(arrets_stats[arrets_stats['timestamp'].dt.date == datetime.now().date()])
                st.metric("Arrêts aujourd'hui", arrets_aujourd_hui)
            
            # Graphiques
            col1, col2 = st.columns(2)
            
            with col1:
                # Répartition par type avec couleurs personnalisées
                type_counts = arrets_stats['type_arret'].value_counts()
                colors = [data_manager.types_arrets.get(t, {'color': '#666666'})['color'] for t in type_counts.index]
                labels = [data_manager.types_arrets.get(t, {'label': t})['label'] for t in type_counts.index]
                
                fig_type = px.pie(
                    values=type_counts.values,
                    names=labels,
                    title="Répartition par Type d'Arrêt",
                    color_discrete_sequence=colors
                )
                st.plotly_chart(fig_type, use_container_width=True)
            
            with col2:
                # Durée moyenne par type
                duree_moyenne = arrets_stats.groupby('type_arret')['duree_minutes'].mean()
                labels_duree = [data_manager.types_arrets.get(t, {'label': t})['label'] for t in duree_moyenne.index]
                colors_duree = [data_manager.types_arrets.get(t, {'color': '#666666'})['color'] for t in duree_moyenne.index]
                
                fig_duree = px.bar(
                    x=labels_duree,
                    y=duree_moyenne.values,
                    title="Durée Moyenne par Type (min)",
                    color=labels_duree,
                    color_discrete_sequence=colors_duree
                )
                fig_duree.update_layout(showlegend=False)
                st.plotly_chart(fig_duree, use_container_width=True)
            
            # Évolution dans le temps
            st.subheader("📈 Évolution Temporelle")
            arrets_stats['date'] = arrets_stats['timestamp'].dt.date
            evolution_daily = arrets_stats.groupby(['date', 'type_arret']).size().reset_index(name='count')
            
            fig_evolution = px.line(
                evolution_daily,
                x='date',
                y='count',
                color='type_arret',
                title="Évolution des Arrêts par Jour",
                color_discrete_map={t: data_manager.types_arrets.get(t, {'color': '#666666'})['color'] for t in evolution_daily['type_arret'].unique()}
            )
            st.plotly_chart(fig_evolution, use_container_width=True)

# PAGE: DÉTECTION AUTOMATIQUE
elif page == "🤖 Détection Automatique":
    st.title("🤖 Détection Automatique d'Arrêts")
    
    st.markdown("""
    Cette page implémente la logique du diagramme de flux pour détecter automatiquement les arrêts 
    basés sur l'analyse des signaux de vibration.
    """)
    
    # Bouton pour lancer la détection
    col1, col2, col3 = st.columns([1, 1, 1])
    with col2:
        if st.button("🔍 Lancer Détection Automatique", use_container_width=True):
            with st.spinner("Analyse des signaux de vibration..."):
                # Détection des arrêts
                arrets_detectes = data_manager.detect_machine_stops(df)
                
                # Sauvegarde des nouveaux arrêts détectés
                for arret in arrets_detectes:
                    arret['statut'] = 'detecte_auto'
                    arret['classifie'] = False
                    data_manager.save_arret_auto(arret)
                
                st.success(f"✅ {len(arrets_detectes)} arrêts détectés automatiquement!")
                st.rerun()
    
    # Affichage des arrêts non classifiés
    arrets_non_classifies = data_manager.get_arrets_non_classifies()
    
    if len(arrets_non_classifies) > 0:
        st.markdown("---")
        st.subheader("⚠️ Arrêts Détectés Nécessitant une Classification")
        
        st.markdown("""
        <div class="alert-box alert-info">
            <strong>ℹ️ Information:</strong><br>
            Les arrêts suivants ont été détectés automatiquement par analyse des vibrations. 
            Veuillez les classifier selon leur cause réelle.
        </div>
        """, unsafe_allow_html=True)
        
        for idx, arret in arrets_non_classifies.iterrows():
            with st.expander(f"🔍 Arrêt détecté: {arret['debut_arret'].strftime('%d/%m/%Y %H:%M')} - Durée: {arret['duree_minutes']} min"):
                col1, col2 = st.columns([1, 1])
                
                with col1:
                    st.write(f"**Début:** {arret['debut_arret'].strftime('%d/%m/%Y %H:%M:%S')}")
                    st.write(f"**Fin:** {arret['fin_arret'].strftime('%d/%m/%Y %H:%M:%S')}")
                    st.write(f"**Durée:** {arret['duree_minutes']} minutes")
                    st.write(f"**Statut:** Détection automatique")
                
                with col2:
                    with st.form(f"classification_form_{idx}"):
                        st.write("**Classification de l'arrêt:**")
                        
                        type_arret_class = st.selectbox(
                            "Type d'arrêt",
                            list(data_manager.types_arrets.keys()),
                            format_func=lambda x: data_manager.types_arrets[x]['label'],
                            key=f"type_{idx}"
                        )
                        
                        sous_categories_class = data_manager.types_arrets[type_arret_class]['sous_categories']
                        sous_categorie_class = st.selectbox(
                            "Sous-catégorie",
                            sous_categories_class,
                            key=f"sous_cat_{idx}"
                        )
                        
                        commentaire_class = st.text_area(
                            "Commentaire",
                            key=f"comment_{idx}",
                            height=80
                        )
                        
                        operateur_class = st.text_input(
                            "Opérateur",
                            value="Opérateur",
                            key=f"op_{idx}"
                        )
                        
                        if st.form_submit_button("✅ Classifier cet arrêt"):
                            success = data_manager.classifier_arret(
                                idx, type_arret_class, sous_categorie_class,
                                commentaire_class, operateur_class
                            )
                            if success:
                                st.success("✅ Arrêt classifié avec succès!")
                                st.rerun()
                            else:
                                st.error("❌ Erreur lors de la classification")
    else:
        st.info("✅ Tous les arrêts détectés ont été classifiés")
    
    # Statistiques de détection
    st.markdown("---")
    st.subheader("📊 Statistiques de Détection Automatique")
    
    arrets_auto_all = data_manager.load_arrets_auto()
    
    if len(arrets_auto_all) > 0:
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("Arrêts détectés", len(arrets_auto_all))
        
        with col2:
            classifies = len(arrets_auto_all[arrets_auto_all.get('classifie', False) == True])
            st.metric("Arrêts classifiés", classifies)
        
        with col3:
            taux_classification = (classifies / len(arrets_auto_all)) * 100 if len(arrets_auto_all) > 0 else 0
            st.metric("Taux de classification", f"{taux_classification:.1f}%")
        
        with col4:
            duree_totale = arrets_auto_all['duree_minutes'].sum()
            st.metric("Durée totale détectée", f"{duree_totale:.0f} min")

# Ajout des autres pages existantes...
# (Le reste du code reste identique)

# Footer
st.markdown("---")
st.markdown("""
<div style='text-align: center; color: #666;'>
    <p>Dashboard Maintenance Prédictive v2.0 | Développé avec Streamlit</p>
    <p>🔧 Machine de Coupe Industrielle | 🤖 Détection Automatique Intégrée</p>
</div>
""", unsafe_allow_html=True)
