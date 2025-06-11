import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import numpy as np
from datetime import datetime, timedelta
import json
import os
import time
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
        .main-header {
        background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
        padding: 1rem;
        border-radius: 10px;
        color: white;
        margin-bottom: 2rem;
        text-align: center;
    }
    metric-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 1.5rem;
        border-radius: 15px;
        color: white;
        box-shadow: 0 8px 32px rgba(0,0,0,0.1);
        border: 1px solid rgba(255,255,255,0.1);
        backdrop-filter: blur(10px);
        margin-bottom: 1rem;
    }
            .metric-card-green {
        background: linear-gradient(135deg, #11998e 0%, #38ef7d 100%);
    }
    
    .metric-card-red {
        background: linear-gradient(135deg, #ff416c 0%, #ff4b2b 100%);
    }
    
    .metric-card-blue {
        background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%);
    }
    
    .metric-card-purple {
        background: linear-gradient(135deg, #a8edea 0%, #fed6e3 100%);
        color: #333;
    }
    
    .metric-value {
        font-size: 2.5rem;
        font-weight: bold;
        margin: 0.5rem 0;
    }
    
    .metric-label {
        font-size: 0.9rem;
        opacity: 0.9;
        margin-bottom: 0.5rem;
    }
    
    .metric-delta {
        font-size: 0.8rem;
        opacity: 0.8;
    }
    .alert-card {
        padding: 1rem;
        border-radius: 10px;
        margin: 1rem 0;
        border-left: 4px solid;
        backdrop-filter: blur(10px);
    }
            
    .arret-maintenance { border-left-color: #1f4e79; background-color: #e8f4fd; }
    .arret-prevu { border-left-color: #40e0d0; background-color: #e0fffe; }
    .arret-imprevu { border-left-color: #9932cc; background-color: #f5e8ff; }
    .arret-conducteur { border-left-color: #ffd700; background-color: #fffde8; }
    .arret-qualite { border-left-color: #ff0000; background-color: #ffe8e8; }
    .status-indicator {
        display: inline-block;
        width: 12px;
        height: 12px;
        border-radius: 50%;
        margin-right: 8px;
        animation: pulse 2s infinite;
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
    .alert-danger { 
        background: rgba(220, 53, 69, 0.1); 
        border-left-color: #dc3545; 
        color: #dc3545;
    }
    
    .alert-warning { 
        background: rgba(255, 193, 7, 0.1); 
        border-left-color: #ffc107; 
        color: #ffc107;
    }
    
    .alert-success { 
        background: rgba(40, 167, 69, 0.1); 
        border-left-color: #28a745; 
        color: #28a745;
    }
    .alert-info { background-color: #d1ecf1; border-left: 4px solid #17a2b8; }
    .chart-container {
        background: rgba(255, 255, 255, 0.05);
        border-radius: 15px;
        padding: 1rem;
        backdrop-filter: blur(10px);
        border: 1px solid rgba(255, 255, 255, 0.1);
        margin-bottom: 1rem;
    }
    @keyframes pulse {
        0% { opacity: 1; }
        50% { opacity: 0.5; }
        100% { opacity: 1; }
    }
    .signal-zero {
        background-color: #f8d7da;
        border-left: 4px solid #dc3545;
        padding: 1rem;
        border-radius: 0.5rem;
        margin: 1rem 0;
    }
    .signal-nonzero {
        background-color: #d4edda;
        border-left: 4px solid #28a745;
        padding: 1rem;
        border-radius: 0.5rem;
        margin: 1rem 0;
    }
    .flow-step {
        background-color: #f8f9fa;
        border: 1px solid #dee2e6;
        border-radius: 0.5rem;
        padding: 1.5rem;
        margin-bottom: 1rem;
        position: relative;
    }
    .flow-step-number {
        position: absolute;
        top: -15px;
        left: 20px;
        background-color: #007bff;
        color: white;
        width: 30px;
        height: 30px;
        border-radius: 50%;
        display: flex;
        align-items: center;
        justify-content: center;
        font-weight: bold;
    }
    .flow-arrow {
        text-align: center;
        font-size: 24px;
        color: #6c757d;
        margin: -0.5rem 0;
    }
    
            
    .classification-card {
        border: 1px solid #dee2e6;
        border-radius: 0.5rem;
        padding: 1rem;
        margin-bottom: 1rem;
        background-color: white;
    }
    .classification-header {
        display: flex;
        justify-content: space-between;
        margin-bottom: 0.5rem;
    }
    .classification-badge {
        padding: 0.25rem 0.5rem;
        border-radius: 0.25rem;
        font-size: 0.875rem;
        font-weight: 600;
    }
            
            .dashboard-grid {
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
        gap: 1rem;
        margin-bottom: 2rem;
    }
    
    .stSelectbox > div > div {
        background-color: rgba(255, 255, 255, 0.1);
        border-radius: 10px;
    }
    
    .stButton > button {
        background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
        color: white;
        border: none;
        border-radius: 10px;
        padding: 0.5rem 1rem;
        font-weight: bold;
    }
    
    .stButton > button:hover {
        background: linear-gradient(90deg, #764ba2 0%, #667eea 100%);
        transform: translateY(-2px);
        box-shadow: 0 5px 15px rgba(0,0,0,0.2);
    }
    .footer {
        text-align: center;
        color: #666;
        padding: 1rem;
        border-top: 1px solid #dee2e6;
        margin-top: 2rem;
    }
            
            
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

# PAGE 1: SUIVI INSTANTANÉ AMÉLIORÉ
if page == "📊 Suivi Instantané":
    # En-tête principal
    st.markdown("""
    <div class="main-header">
        <h1>🔧 Dashboard Maintenance Prédictive</h1>
        <p>Surveillance en temps réel de la machine de coupe industrielle</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Contrôles
    col1, col2, col3, col4 = st.columns([2, 1, 1, 1])
    with col1:
        hours_back = st.selectbox("Période d'affichage", [1, 3, 6, 12, 24], index=2, format_func=lambda x: f"{x}h")
    with col2:
        auto_refresh = st.checkbox("Auto-refresh", value=False)
    with col3:
        if st.button("🔄 Actualiser"):
            st.rerun()
    with col4:
        real_time = st.checkbox("Temps réel", value=True)
    
    # Données récentes
    cutoff_time = datetime.now() - timedelta(hours=hours_back)
    recent_data = df[pd.to_datetime(df['timestamp']) >= cutoff_time].copy()
    
    if len(recent_data) == 0:
        st.warning("Aucune donnée disponible pour la période sélectionnée")
        st.stop()
    
    # État actuel
    current_state = recent_data.iloc[-1]
    
    # Calcul des métriques
    vibration_threshold = data_manager.config.get('seuil_vibration_alerte', 2.0)
    max_vibration = max(current_state['vibration_x'], current_state['vibration_y'], current_state['vibration_z'])
    
    # Métriques principales avec design moderne
    st.markdown("### 📊 Métriques Principales")
    
    col1, col2, col3, col4 = st.columns(4)
    
    # État machine avec indicateur animé
    status_colors = {
        'en_marche': '#28a745',
        'panne': '#dc3545', 
        'arret_production': '#007bff',
        'probleme_qualite': '#ffc107'
    }
    
    status_labels = {
        'en_marche': 'En Marche',
        'panne': 'Panne',
        'arret_production': 'Arrêt Production', 
        'probleme_qualite': 'Problème Qualité'
    }
    
    current_status = current_state['etat_machine']
    status_color = status_colors.get(current_status, '#6c757d')
    
    with col1:
        card_class = "metric-card-green" if current_status == 'en_marche' else "metric-card-red" if current_status == 'panne' else "metric-card-blue"
        st.markdown(f"""
        <div class="metric-card {card_class}">
            <div class="metric-label">État Machine</div>
            <div class="metric-value">
                <span class="status-indicator" style="background-color: {status_color};"></span>
                {status_labels.get(current_status, 'Inconnu')}
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        delta_x = current_state['vibration_x'] - recent_data['vibration_x'].mean()
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-label">Vibration X</div>
            <div class="metric-value">{current_state['vibration_x']:.2f}</div>
            <div class="metric-delta">mm/s (Δ {delta_x:+.2f})</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        delta_y = current_state['vibration_y'] - recent_data['vibration_y'].mean()
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-label">Vibration Y</div>
            <div class="metric-value">{current_state['vibration_y']:.2f}</div>
            <div class="metric-delta">mm/s (Δ {delta_y:+.2f})</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col4:
        delta_z = current_state['vibration_z'] - recent_data['vibration_z'].mean()
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-label">Vibration Z</div>
            <div class="metric-value">{current_state['vibration_z']:.2f}</div>
            <div class="metric-delta">mm/s (Δ {delta_z:+.2f})</div>
        </div>
        """, unsafe_allow_html=True)
    
    # Alertes avec design amélioré
    if max_vibration > vibration_threshold:
        st.markdown(f"""
        <div class="alert-card alert-danger">
            <h4>⚠️ ALERTE VIBRATION CRITIQUE!</h4>
            <p>Vibration détectée: <strong>{max_vibration:.2f} mm/s</strong> (Seuil: {vibration_threshold} mm/s)</p>
            <p>Action immédiate requise - Vérifier les composants mécaniques</p>
        </div>
        """, unsafe_allow_html=True)
    elif current_state['etat_machine'] == 'panne':
        st.markdown("""
        <div class="alert-card alert-danger">
            <h4>🔴 MACHINE EN PANNE</h4>
            <p>Intervention technique requise</p>
            <p>Contactez l'équipe de maintenance</p>
        </div>
        """, unsafe_allow_html=True)
    else:
        st.markdown("""
        <div class="alert-card alert-success">
            <h4>✅ MACHINE OPÉRATIONNELLE</h4>
            <p>Fonctionnement normal - Tous les paramètres dans les limites</p>
        </div>
        """, unsafe_allow_html=True)
    
    # Graphiques avec design moderne
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.markdown("### 📈 Évolution des Vibrations en Temps Réel")
        
        # Graphique des vibrations avec style moderne
        fig_vibrations = go.Figure()
        
        # Ajout des courbes avec style amélioré
        fig_vibrations.add_trace(go.Scatter(
            x=recent_data['timestamp'], 
            y=recent_data['vibration_x'],
            name='Vibration X',
            line=dict(color='#ff6b6b', width=3),
            fill='tonexty' if len(fig_vibrations.data) > 0 else None,
            fillcolor='rgba(255, 107, 107, 0.1)'
        ))
        
        fig_vibrations.add_trace(go.Scatter(
            x=recent_data['timestamp'], 
            y=recent_data['vibration_y'],
            name='Vibration Y',
            line=dict(color='#4ecdc4', width=3),
            fill='tonexty',
            fillcolor='rgba(78, 205, 196, 0.1)'
        ))
        
        fig_vibrations.add_trace(go.Scatter(
            x=recent_data['timestamp'], 
            y=recent_data['vibration_z'],
            name='Vibration Z',
            line=dict(color='#45b7d1', width=3),
            fill='tonexty',
            fillcolor='rgba(69, 183, 209, 0.1)'
        ))
        
        # Ligne de seuil
        fig_vibrations.add_hline(
            y=vibration_threshold, 
            line_dash="dash", 
            line_color="orange", 
            line_width=2,
            annotation_text=f"Seuil d'alerte ({vibration_threshold} mm/s)"
        )
        
        # Style du graphique
        fig_vibrations.update_layout(
            height=400,
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)',
            font=dict(color='white'),
            xaxis=dict(
                gridcolor='rgba(255,255,255,0.1)',
                title="Temps"
            ),
            yaxis=dict(
                gridcolor='rgba(255,255,255,0.1)',
                title="Vibration (mm/s)"
            ),
            legend=dict(
                orientation="h",
                yanchor="bottom",
                y=1.02,
                xanchor="right",
                x=1
            )
        )
        
        st.plotly_chart(fig_vibrations, use_container_width=True)
    
    with col2:
        st.markdown("### 📊 Répartition des États")
        
        # Calcul du temps dans chaque état
        state_duration = recent_data.groupby('etat_machine').size()
        
        # Graphique circulaire moderne (donut chart)
        fig_pie = go.Figure(data=[go.Pie(
            labels=[status_labels.get(state, state) for state in state_duration.index],
            values=state_duration.values,
            hole=0.6,
            marker=dict(
                colors=['#28a745', '#dc3545', '#007bff', '#ffc107'],
                line=dict(color="#666666", width=2)
            ),
            textinfo='label+percent',
            textfont=dict(size=12, color="#666666")
        )])
        
        fig_pie.update_layout(
            height=300,
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)',
            font=dict(color="#666666"),
            showlegend=False,
            annotations=[dict(text='États<br>Machine', x=0.5, y=0.5, font_size=16, showarrow=False, font_color='#666666')]
        )
        
        st.plotly_chart(fig_pie, use_container_width=True)
        
        # Statistiques détaillées
        st.markdown("### 📋 Statistiques Détaillées")
        
        total_points = len(recent_data)
        running_time = len(recent_data[recent_data['etat_machine'] == 'en_marche'])
        downtime = total_points - running_time
        avg_vibration = recent_data[['vibration_x', 'vibration_y', 'vibration_z']].mean().mean()
        
        # Métriques secondaires
        st.markdown(f"""
        <div class="metric-card metric-card-purple">
            <div class="metric-label">Temps de fonctionnement</div>
            <div class="metric-value">{(running_time/total_points*100):.1f}%</div>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown(f"""
        <div class="metric-card metric-card-purple">
            <div class="metric-label">Temps d'arrêt</div>
            <div class="metric-value">{(downtime/total_points*100):.1f}%</div>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown(f"""
        <div class="metric-card metric-card-purple">
            <div class="metric-label">Vibration moyenne</div>
            <div class="metric-value">{avg_vibration:.2f}</div>
            <div class="metric-delta">mm/s</div>
        </div>
        """, unsafe_allow_html=True)
    
    # Graphique de tendance avancé
    st.markdown("### 📈 Analyse de Tendance Avancée")
    
    # Calcul de la vibration totale
    recent_data['vibration_totale'] = np.sqrt(
        recent_data['vibration_x']**2 + 
        recent_data['vibration_y']**2 + 
        recent_data['vibration_z']**2
    )
    
    # Graphique combiné avec zone remplie
    fig_trend = go.Figure()
    
    # Zone de vibration totale
    fig_trend.add_trace(go.Scatter(
        x=recent_data['timestamp'],
        y=recent_data['vibration_totale'],
        fill='tozeroy',
        fillcolor='rgba(106, 90, 205, 0.3)',
        line=dict(color='rgba(106, 90, 205, 1)', width=3),
        name='Vibration Totale',
        hovertemplate='<b>Vibration Totale</b><br>%{y:.2f} mm/s<br>%{x}<extra></extra>'
    ))
    
    # Ligne de tendance
    z = np.polyfit(range(len(recent_data)), recent_data['vibration_totale'], 1)
    p = np.poly1d(z)
    trend_line = p(range(len(recent_data)))
    
    fig_trend.add_trace(go.Scatter(
        x=recent_data['timestamp'],
        y=trend_line,
        line=dict(color='#ff6b6b', width=2, dash='dash'),
        name='Tendance',
        hovertemplate='<b>Tendance</b><br>%{y:.2f} mm/s<extra></extra>'
    ))
    
    # Zones de seuil
    fig_trend.add_hrect(
        y0=0, y1=vibration_threshold,
        fillcolor="rgba(40, 167, 69, 0.1)",
        layer="below", line_width=0,
        annotation_text="Zone Normale", annotation_position="top left"
    )
    
    fig_trend.add_hrect(
        y0=vibration_threshold, y1=vibration_threshold*2,
        fillcolor="rgba(255, 193, 7, 0.1)",
        layer="below", line_width=0,
        annotation_text="Zone d'Alerte", annotation_position="top left"
    )
    
    fig_trend.update_layout(
        height=400,
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        font=dict(color='white'),
        xaxis=dict(
            gridcolor='rgba(255,255,255,0.1)',
            title="Temps"
        ),
        yaxis=dict(
            gridcolor='rgba(255,255,255,0.1)',
            title="Vibration (mm/s)"
        ),
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1
        )
    )
    
    st.plotly_chart(fig_trend, use_container_width=True)
    
    # Indicateurs de performance en temps réel
    st.markdown("### ⚡ Indicateurs de Performance")
    
    col1, col2, col3, col4, col5 = st.columns(5)
    
    # Calcul des KPIs
    efficiency = (running_time / total_points) * 100
    availability = ((total_points - len(recent_data[recent_data['etat_machine'] == 'panne'])) / total_points) * 100
    quality_rate = ((total_points - len(recent_data[recent_data['etat_machine'] == 'probleme_qualite'])) / total_points) * 100
    oee = (efficiency * availability * quality_rate) / 10000  # OEE approximatif
    
    with col1:
        st.metric("Efficacité", f"{efficiency:.1f}%", f"{efficiency-85:.1f}%")
    
    with col2:
        st.metric("Disponibilité", f"{availability:.1f}%", f"{availability-90:.1f}%")
    
    with col3:
        st.metric("Qualité", f"{quality_rate:.1f}%", f"{quality_rate-95:.1f}%")
    
    with col4:
        st.metric("OEE", f"{oee:.1f}%", f"{oee-75:.1f}%")
    
    with col5:
        # Calcul de la santé globale
        health_score = (efficiency + availability + quality_rate) / 3
        health_color = "🟢" if health_score > 90 else "🟡" if health_score > 75 else "🔴"
        st.metric("Santé Globale", f"{health_color} {health_score:.1f}%")
    
    # Auto-refresh
    if auto_refresh:
        import time
        time.sleep(30)
        st.rerun()

# PAGE 2: SAISIE CAUSES D'ARRÊT
elif page == "📝 Saisie Causes d'Arrêt":
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
                    data_manager.composants_machine
                )
                
                # Durée estimée
                duree_minutes = st.number_input("Durée de l'arrêt (minutes)", min_value=1, value=10)
                
                # Commentaire détaillé
                commentaire = st.text_area("Commentaire détaillé", height=100)
                
                # Opérateur
                operateur = st.text_input("Nom de l'opérateur", value="Opérateur")
                
                # Priorité/Urgence
                urgence = st.selectbox("Niveau d'urgence", data_manager.niveaux_urgence)
                
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
                    
                    success = data_manager.save_arret(nouvel_arret)
                    if success:
                        st.success("✅ Arrêt enregistré avec succès!")
                        st.rerun()
                    else:
                        st.error("❌ Erreur lors de l'enregistrement de l'arrêt")
        
        with col2:
            st.subheader("🎨 Aperçu de la Classification")
            
            # Affichage des types d'arrêts avec couleurs
            for type_key, type_info in data_manager.types_arrets.items():
                color = type_info['color']
                label = type_info['label']
                icon = type_info.get('icon', '●')
                
                st.markdown(f"""
                <div class="arret-card" style="border-left-color: {color}; background-color: {color}20;">
                    <strong style="color: {color};">{icon} {label}</strong><br>
                    <small>Sous-catégories: {', '.join(type_info['sous_categories'][:3])}{'...' if len(type_info['sous_categories']) > 3 else ''}</small>
                </div>
                """, unsafe_allow_html=True)
    
    with tab2:
        st.subheader("📋 Derniers Arrêts Enregistrés")
        
        # Chargement des arrêts
        arrets_df = data_manager.load_arrets()
        
        if len(arrets_df) > 0:
            # Filtres
            col_filter1, col_filter2, col_filter3 = st.columns(3)
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
            with col_filter3:
                filtre_urgence = st.multiselect(
                    "Filtrer par urgence",
                    data_manager.niveaux_urgence
                )
            
            # Application des filtres
            arrets_filtered = arrets_df.copy()
            if filtre_type:
                arrets_filtered = arrets_filtered[arrets_filtered['type_arret'].isin(filtre_type)]
            if filtre_operateur:
                arrets_filtered = arrets_filtered[arrets_filtered['operateur'].isin(filtre_operateur)]
            if filtre_urgence:
                arrets_filtered = arrets_filtered[arrets_filtered['urgence'].isin(filtre_urgence)]
            
            # Affichage des arrêts
            for idx, arret in arrets_filtered.head(10).iterrows():
                type_info = data_manager.types_arrets.get(arret['type_arret'], {'color': '#666666', 'label': arret['type_arret'], 'icon': '●'})
                color = type_info['color']
                icon = type_info.get('icon', '●')
                
                with st.expander(f"{icon} {type_info['label']} - {arret['timestamp'].strftime('%d/%m/%Y %H:%M')}"):
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
            
            # Répartition par urgence
            st.subheader("🚨 Répartition par Niveau d'Urgence")
            if 'urgence' in arrets_stats.columns:
                urgence_counts = arrets_stats['urgence'].value_counts()
                
                urgence_colors = {
                    'Faible': '#28a745',
                    'Moyen': '#ffc107',
                    'Élevé': '#fd7e14',
                    'Critique': '#dc3545'
                }
                
                fig_urgence = px.pie(
                    values=urgence_counts.values,
                    names=urgence_counts.index,
                    title="Répartition par Niveau d'Urgence",
                    color=urgence_counts.index,
                    color_discrete_map=urgence_colors
                )
                st.plotly_chart(fig_urgence, use_container_width=True)
        else:
            st.info("Aucune donnée d'arrêt disponible pour générer des statistiques")

# PAGE: DÉTECTION AUTOMATIQUE
elif page == "🤖 Détection Automatique":
    st.title("🤖 Détection Automatique d'Arrêts")
    
    # Introduction avec diagramme de flux
    st.markdown("""
    <div class="alert-box alert-info">
        <strong>ℹ️ Fonctionnement:</strong><br>
        Cette page implémente la logique du diagramme de flux pour détecter automatiquement les arrêts 
        basés sur l'analyse des signaux de vibration. Le système détecte quand le signal est égal à zéro 
        (machine arrêtée) ou différent de zéro (machine en fonctionnement).
    </div>
    """, unsafe_allow_html=True)
    
    # Visualisation du flux de détection
    st.subheader("🔄 Flux de Détection")
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        # Étape 1: Signal de vibration
        st.markdown("""
        <div class="flow-step">
            <div class="flow-step-number">1</div>
            <h4>Signal de vibration</h4>
            <p>Le système analyse en continu les signaux de vibration (X, Y, Z) provenant des capteurs.</p>
        </div>
        <div class="flow-arrow">↓</div>
        """, unsafe_allow_html=True)
        
        # Étape 2: Décision
        st.markdown("""
        <div class="flow-step">
            <div class="flow-step-number">2</div>
            <h4>Décision: Signal = 0 ?</h4>
            <p>Le système détermine si le signal de vibration est égal ou proche de zéro.</p>
            <div style="display: flex; justify-content: space-around; margin-top: 10px;">
                <div style="text-align: center;">
                    <div style="font-weight: bold; color: #dc3545;">Signal = 0</div>
                    <div style="font-size: 24px;">↙</div>
                </div>
                <div style="text-align: center;">
                    <div style="font-weight: bold; color: #28a745;">Signal ≠ 0</div>
                    <div style="font-size: 24px;">↘</div>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        # Étape 3: États
        col_a, col_b = st.columns(2)
        
        with col_a:
            st.markdown("""
            <div class="signal-zero">
                <h4>Machine en arrêt</h4>
                <p>Enregistrement de la période et la durée</p>
                <div style="font-size: 24px; text-align: center;">↓</div>
                <p>Message de demande de sélection du motif d'arrêt</p>
            </div>
            """, unsafe_allow_html=True)
        
        with col_b:
            st.markdown("""
            <div class="signal-nonzero">
                <h4>Machine en fonctionnement</h4>
                <p>Enregistrement de la période et la durée</p>
                <p>Aucune action requise</p>
            </div>
            """, unsafe_allow_html=True)
    
    with col2:
        # Statistiques actuelles
        st.markdown("### 📊 Statistiques")
        
        # Dernière vibration
        if len(df) > 0:
            last_row = df.iloc[-1]
            vibration_totale = np.sqrt(
                last_row['vibration_x']**2 + 
                last_row['vibration_y']**2 + 
                last_row['vibration_z']**2
            )
            
            # Seuil de détection
            seuil = data_manager.config.get('seuil_arret_vibration', 0.1)
            
            # Affichage du statut actuel
            if vibration_totale <= seuil:
                st.markdown("""
                <div class="signal-zero" style="text-align: center;">
                    <h3>⚠️ Machine actuellement arrêtée</h3>
                    <p>Signal de vibration proche de zéro</p>
                </div>
                """, unsafe_allow_html=True)
            else:
                st.markdown("""
                <div class="signal-nonzero" style="text-align: center;">
                    <h3>✅ Machine en fonctionnement</h3>
                    <p>Signal de vibration détecté</p>
                </div>
                """, unsafe_allow_html=True)
            
            # Affichage des valeurs
            st.metric("Vibration totale", f"{vibration_totale:.3f} mm/s")
            st.metric("Seuil de détection", f"{seuil:.3f} mm/s")
            
            # Derniers arrêts détectés
            arrets_auto = data_manager.load_arrets_auto()
            if len(arrets_auto) > 0:
                st.metric("Arrêts détectés", len(arrets_auto))
                st.metric("Arrêts non classifiés", len(data_manager.get_arrets_non_classifies()))
    
    # Bouton pour lancer la détection
    st.markdown("---")
    st.subheader("🔍 Lancer une Détection")
    
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        if st.button("🔍 Analyser les Signaux de Vibration", use_container_width=True):
            with st.spinner("Analyse des signaux de vibration en cours..."):
                # Simulation de traitement
                progress_bar = st.progress(0)
                for i in range(101):
                    time.sleep(0.01)
                    progress_bar.progress(i)
                
                # Détection des arrêts
                arrets_detectes = data_manager.detect_machine_stops(df)
                
                # Compteur d'arrêts ajoutés
                arrets_ajoutes = 0
                
                # Sauvegarde des nouveaux arrêts détectés
                for arret in arrets_detectes:
                    arret['statut'] = 'detecte_auto'
                    arret['classifie'] = False
                    success = data_manager.save_arret_auto(arret)
                    if success:
                        arrets_ajoutes += 1
                
                st.success(f"✅ Analyse terminée: {len(arrets_detectes)} arrêts détectés, {arrets_ajoutes} nouveaux arrêts ajoutés!")
    
    # Affichage des arrêts non classifiés
    st.markdown("---")
    st.subheader("⚠️ Arrêts Détectés Nécessitant une Classification")
    
    arrets_non_classifies = data_manager.get_arrets_non_classifies()
    
    if len(arrets_non_classifies) > 0:
        st.markdown("""
        <div class="alert-box alert-warning">
            <strong>⚠️ Action requise:</strong><br>
            Les arrêts suivants ont été détectés automatiquement par analyse des vibrations. 
            Veuillez les classifier selon leur cause réelle pour améliorer la maintenance prédictive.
        </div>
        """, unsafe_allow_html=True)
        
        # Affichage des arrêts à classifier
        for idx, arret in arrets_non_classifies.iterrows():
            with st.expander(f"🔍 Arrêt #{idx+1}: {arret['debut_arret'].strftime('%d/%m/%Y %H:%M')} - Durée: {arret['duree_minutes']} min"):
                col1, col2 = st.columns([1, 1])
                
                with col1:
                    st.markdown(f"""
                    <div class="classification-card">
                        <div class="classification-header">
                            <span>Informations de l'arrêt</span>
                            <span class="classification-badge" style="background-color: #dc3545; color: white;">Non classifié</span>
                        </div>
                        <hr>
                        <p><strong>Début:</strong> {arret['debut_arret'].strftime('%d/%m/%Y %H:%M:%S')}</p>
                        <p><strong>Fin:</strong> {arret['fin_arret'].strftime('%d/%m/%Y %H:%M:%S')}</p>
                        <p><strong>Durée:</strong> {arret['duree_minutes']} minutes</p>
                        <p><strong>Détecté le:</strong> {arret.get('date_detection', 'N/A')}</p>
                    </div>
                    """, unsafe_allow_html=True)
                
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
                        
                        urgence_class = st.selectbox(
                            "Niveau d'urgence",
                            data_manager.niveaux_urgence,
                            key=f"urgence_{idx}"
                        )
                        
                        if st.form_submit_button("✅ Classifier cet arrêt"):
                            success = data_manager.classifier_arret(
                                idx, type_arret_class, sous_categorie_class,
                                commentaire_class, operateur_class, urgence_class
                            )
                            if success:
                                st.success("✅ Arrêt classifié avec succès!")
                                st.rerun()
                            else:
                                st.error("❌ Erreur lors de la classification")
    else:
        st.success("✅ Tous les arrêts détectés ont été classifiés")
    
    # Statistiques de détection
    st.markdown("---")
    st.subheader("📊 Statistiques de Détection Automatique")
    
    arrets_auto_all = data_manager.load_arrets_auto()
    
    if len(arrets_auto_all) > 0:
        # Métriques principales
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
        
        # Graphiques
        col1, col2 = st.columns(2)
        
        with col1:
            # Distribution des durées d'arrêt
            fig_duree_dist = px.histogram(
                arrets_auto_all,
                x='duree_minutes',
                nbins=20,
                title="Distribution des Durées d'Arrêt",
                labels={'duree_minutes': 'Durée (minutes)'},
                color_discrete_sequence=['#007bff']
            )
            fig_duree_dist.update_layout(bargap=0.1)
            st.plotly_chart(fig_duree_dist, use_container_width=True)
        
        with col2:
            # Répartition par type (pour les arrêts classifiés)
            arrets_classifies = arrets_auto_all[arrets_auto_all.get('classifie', False) == True]
            
            if len(arrets_classifies) > 0 and 'type_arret' in arrets_classifies.columns:
                type_counts = arrets_classifies['type_arret'].value_counts()
                
                if len(type_counts) > 0:
                    colors = [data_manager.types_arrets.get(t, {'color': '#666666'})['color'] for t in type_counts.index]
                    labels = [data_manager.types_arrets.get(t, {'label': t})['label'] for t in type_counts.index]
                    
                    fig_type = px.pie(
                        values=type_counts.values,
                        names=labels,
                        title="Répartition par Type d'Arrêt",
                        color_discrete_sequence=colors
                    )
                    st.plotly_chart(fig_type, use_container_width=True)
                else:
                    st.info("Pas assez de données pour afficher la répartition par type")
            else:
                st.info("Classifiez des arrêts pour voir leur répartition par type")
        
        # Évolution temporelle
        st.subheader("📈 Évolution des Arrêts Détectés")
        
        # Préparation des données
        arrets_auto_all['date'] = arrets_auto_all['debut_arret'].dt.date
        arrets_par_jour = arrets_auto_all.groupby('date').size().reset_index(name='count')
        
        # Graphique d'évolution
        fig_evolution = px.line(
            arrets_par_jour,
            x='date',
            y='count',
            title="Nombre d'Arrêts Détectés par Jour",
            labels={'date': 'Date', 'count': 'Nombre d\'arrêts'},
            markers=True
        )
        fig_evolution.update_traces(line_color='#007bff')
        st.plotly_chart(fig_evolution, use_container_width=True)
        
        # Tableau récapitulatif
        st.subheader("📋 Récapitulatif des Arrêts Classifiés")
        
        if len(arrets_classifies) > 0:
            # Préparation des données pour le tableau
            recap_data = []
            
            for type_key, type_info in data_manager.types_arrets.items():
                type_arrets = arrets_classifies[arrets_classifies['type_arret'] == type_key]
                
                if len(type_arrets) > 0:
                    recap_data.append({
                        'Type': type_info['label'],
                        'Nombre': len(type_arrets),
                        'Durée totale (min)': type_arrets['duree_minutes'].sum(),
                        'Durée moyenne (min)': type_arrets['duree_minutes'].mean(),
                        'Pourcentage': (len(type_arrets) / len(arrets_classifies)) * 100
                    })
            
            if recap_data:
                recap_df = pd.DataFrame(recap_data)
                recap_df['Durée moyenne (min)'] = recap_df['Durée moyenne (min)'].round(1)
                recap_df['Pourcentage'] = recap_df['Pourcentage'].round(1).astype(str) + '%'
                
                st.dataframe(recap_df, use_container_width=True)
            else:
                st.info("Pas de données récapitulatives disponibles")
        else:
            st.info("Classifiez des arrêts pour voir le récapitulatif")
    else:
        st.info("Aucun arrêt détecté automatiquement pour le moment")
        
        # Suggestion pour lancer une détection
        st.markdown("""
        <div class="alert-box alert-info">
            <strong>💡 Suggestion:</strong><br>
            Cliquez sur le bouton "Analyser les Signaux de Vibration" ci-dessus pour détecter automatiquement 
            les arrêts machine basés sur les données de vibration disponibles.
        </div>
        """, unsafe_allow_html=True)

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
    
    # Calcul des KPIs
    kpis = data_manager.calculate_kpis(df_filtered, date_debut, date_fin)
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("TBF (Temps Brut Fonctionnement)", f"{kpis.get('TBF', 0)}%")
    
    with col2:
        st.metric("Temps de Panne", f"{kpis.get('Taux_Panne', 0)}%")
    
    with col3:
        st.metric("MTBF", f"{kpis.get('MTBF', 0)} h")
    
    with col4:
        st.metric("MTTR", f"{kpis.get('MTTR', 0)} h")
    
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
    
    # Anomalies détectées
    st.subheader("⚠️ Anomalies Détectées")
    
    anomalies = data_manager.detect_anomalies(df_filtered)
    
    if anomalies:
        st.markdown(f"""
        <div class="alert-box alert-warning">
            <strong>⚠️ Attention:</strong> {len(anomalies)} anomalies détectées dans la période sélectionnée.
        </div>
        """, unsafe_allow_html=True)
        
        # Tableau des anomalies
        anomalies_df = pd.DataFrame(anomalies)
        anomalies_df['timestamp'] = pd.to_datetime(anomalies_df['timestamp'])
        anomalies_df = anomalies_df.sort_values('timestamp', ascending=False)
        
        # Conversion pour affichage
        anomalies_display = anomalies_df.copy()
        anomalies_display['timestamp'] = anomalies_display['timestamp'].dt.strftime('%d/%m/%Y %H:%M:%S')
        anomalies_display['value'] = anomalies_display['value'].round(2)
        anomalies_display['threshold'] = anomalies_display['threshold'].round(2)
        
        st.dataframe(
            anomalies_display[['timestamp', 'axis', 'value', 'threshold', 'severity']],
            column_config={
                'timestamp': 'Horodatage',
                'axis': 'Axe',
                'value': 'Valeur (mm/s)',
                'threshold': 'Seuil (mm/s)',
                'severity': 'Sévérité'
            },
            use_container_width=True
        )
    else:
        st.success("✅ Aucune anomalie détectée dans la période sélectionnée")
    
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
            with st.spinner("Génération du rapport en cours..."):
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
    
    # Onglets pour organiser les paramètres
    tab1, tab2, tab3 = st.tabs(["🔧 Paramètres Machine", "📊 Statistiques Système", "💾 Maintenance Données"])
    
    with tab1:
        st.subheader("🔧 Paramètres Machine")
        
        # Chargement de la configuration actuelle
        config = data_manager.config
        
        with st.form("config_form"):
            # Seuils de vibration
            st.write("**Seuils de Vibration**")
            seuil_vibration = st.slider(
                "Seuil d'alerte vibration (mm/s)", 
                0.5, 5.0, 
                float(config.get('seuil_vibration_alerte', 2.0)), 
                0.1
            )
            
            seuil_critique = st.slider(
                "Seuil critique vibration (mm/s)", 
                2.0, 10.0, 
                float(config.get('seuil_vibration_critique', 4.0)), 
                0.1
            )
            
            # Paramètres de détection automatique
            st.write("**Détection Automatique**")
            seuil_arret = st.slider(
                "Seuil de détection d'arrêt (mm/s)", 
                0.01, 0.5, 
                float(config.get('seuil_arret_vibration', 0.1)), 
                0.01
            )
            
            duree_min_arret = st.slider(
                "Durée minimale d'un arrêt (minutes)", 
                1, 10, 
                int(config.get('duree_min_arret', 2))
            )
            
            # Paramètres généraux
            st.write("**Paramètres Généraux**")
            auto_detection = st.checkbox(
                "Activer la détection automatique", 
                bool(config.get('auto_detection_enabled', True))
            )
            
            notifications = st.checkbox(
                "Activer les notifications", 
                bool(config.get('notifications_enabled', True))
            )
            
            # Bouton de sauvegarde
            submitted = st.form_submit_button("💾 Enregistrer les paramètres")
            
            if submitted:
                # Mise à jour de la configuration
                data_manager.update_config('seuil_vibration_alerte', seuil_vibration)
                data_manager.update_config('seuil_vibration_critique', seuil_critique)
                data_manager.update_config('seuil_arret_vibration', seuil_arret)
                data_manager.update_config('duree_min_arret', duree_min_arret)
                data_manager.update_config('auto_detection_enabled', auto_detection)
                data_manager.update_config('notifications_enabled', notifications)
                
                st.success("✅ Paramètres enregistrés avec succès!")
    
    with tab2:
        st.subheader("📊 Statistiques Système")
        
        # Récupération des statistiques
        stats = data_manager.get_system_stats()
        
        # Affichage des statistiques
        col1, col2 = st.columns(2)
        
        with col1:
            st.write("**Données Machine**")
            st.metric("Total d'enregistrements", stats.get('machine_records', 0))
            
            if stats.get('date_debut') and stats.get('date_fin'):
                st.metric("Période couverte", f"{pd.to_datetime(stats['date_debut']).strftime('%d/%m/%Y')} - {pd.to_datetime(stats['date_fin']).strftime('%d/%m/%Y')}")
            
            st.metric("Qualité des données", f"{stats.get('data_quality', 0):.1f}%")
            st.metric("Taille des données", f"{stats.get('machine_data_size', 0):.2f} MB")
        
        with col2:
            st.write("**Données d'Arrêts**")
            st.metric("Arrêts manuels", stats.get('arrets_manuels', 0))
            st.metric("Arrêts auto détectés", stats.get('arrets_auto_total', 0))
            st.metric("Arrêts auto classifiés", stats.get('arrets_auto_classifies', 0))
            st.metric("Taux de classification", f"{stats.get('taux_classification', 0):.1f}%")
        
        # Graphique d'utilisation du disque
        st.subheader("💽 Utilisation du Disque")
        
        disk_data = {
            'Type': ['Données Machine', 'Arrêts Manuels', 'Arrêts Auto', 'Configuration'],
            'Taille (MB)': [
                stats.get('machine_data_size', 0),
                0.1,  # Approximation pour les arrêts manuels
                0.1,  # Approximation pour les arrêts auto
                0.01  # Approximation pour la configuration
            ]
        }
        
        fig_disk = px.bar(
            disk_data,
            x='Type',
            y='Taille (MB)',
            title="Répartition de l'Espace Disque",
            color='Type',
            color_discrete_sequence=['#007bff', '#28a745', '#ffc107', '#6c757d']
        )
        st.plotly_chart(fig_disk, use_container_width=True)
    
    with tab3:
        st.subheader("💾 Maintenance des Données")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.write("**Génération de Données**")
            
            heures_generation = st.number_input("Nombre d'heures à générer", min_value=1, max_value=168, value=24)
            
            if st.button("🔄 Générer Nouvelles Données", use_container_width=True):
                with st.spinner("Génération en cours..."):
                    data_generator.generate_additional_data(hours=heures_generation)
                st.success(f"✅ {heures_generation} heures de nouvelles données générées!")
                st.rerun()
            
            st.write("**Simulation d'Anomalies**")
            
            type_anomalie = st.selectbox(
                "Type d'anomalie",
                ["vibration_spike", "gradual_degradation"]
            )
            
            if st.button("🔄 Simuler Anomalie", use_container_width=True):
                with st.spinner("Simulation en cours..."):
                    data_generator.simulate_anomaly(type_anomalie)
                st.success(f"✅ Anomalie '{type_anomalie}' simulée avec succès!")
                st.rerun()
        
        with col2:
            st.write("**Nettoyage des Données**")
            
            jours_retention = st.number_input("Jours de rétention", min_value=1, max_value=365, value=30)
            
            if st.button("🗑️ Nettoyer Anciennes Données", use_container_width=True):
                with st.spinner("Nettoyage en cours..."):
                    removed = data_manager.cleanup_old_data(days=jours_retention)
                st.success(f"✅ {removed} enregistrements anciens supprimés!")
                st.rerun()
            
            st.write("**Sauvegarde des Données**")
            
            if st.button("💾 Créer une Sauvegarde", use_container_width=True):
                with st.spinner("Sauvegarde en cours..."):
                    backup_files = data_manager.backup_data()
                    if backup_files:
                        st.success(f"✅ Sauvegarde créée avec succès! ({len(backup_files)} fichiers)")
                    else:
                        st.error("❌ Erreur lors de la sauvegarde")


# Footer
st.markdown("---")
st.markdown("""
<div style='text-align: center; color: #666;'>
    <p>Dashboard Maintenance Prédictive v1.0 | Développé avec Streamlit</p>
    <p>🔧 Machine de Coupe Industrielle | 📊 Données simulées pour démonstration</p>
</div>
""", unsafe_allow_html=True)
