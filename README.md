# Dashboard IoT pour Maintenance Prédictive

## 🎯 Objectif du Projet

Ce dashboard permet de suivre en temps réel et historiquement l'état opérationnel d'une machine de coupe industrielle équipée de capteurs de vibrations. L'objectif à long terme est la mise en place d'un système de maintenance prédictive.

## 🚀 Fonctionnalités Principales

### 📊 Mode Suivi Instantané
- Affichage visuel de l'état de la machine avec code couleur
- Courbes de vibrations en temps réel (X, Y, Z)
- Alertes automatiques en cas de dépassement de seuils
- Résumé des dernières heures d'activité
- Métriques de performance en temps réel

### 📝 Saisie des Causes d'Arrêt
- Formulaire intuitif pour documenter les arrêts
- Catégorisation des types d'arrêts (panne, changement série, etc.)
- Association avec les pièces concernées
- Historique des interventions
- Statistiques des causes d'arrêt 

### 📈 Mode Historique Machine
- Visualisation complète de l'historique
- Calcul des KPIs (TBF, TFN, MTBF, MTTR)
- Filtres par date et type d'événement
- Export des données (CSV, JSON, Excel)
- Génération de rapports de synthèse

### ⚙️ Configuration Système
- Paramétrage des seuils d'alerte
- Génération de données simulées
- Maintenance des données
- Statistiques système

## 🛠️ Technologies Utilisées

- **Frontend**: Streamlit (Python)
- **Visualisation**: Plotly, Matplotlib
- **Données**: Pandas, NumPy
- **Stockage**: CSV, JSON (extensible vers bases de données)
- **Simulation**: Générateur de données réalistes

## 📦 Installation et Lancement

### Prérequis
- Python 3.8 ou supérieur
- pip (gestionnaire de paquets Python)

### Installation

1. **Cloner ou télécharger le projet**
\`\`\`bash
git clone <url-du-projet>
cd dashboard-machine-coupe
\`\`\`

2. **Installer les dépendances**
\`\`\`bash
pip install -r requirements.txt
\`\`\`

3. **Lancer l'application**
\`\`\`bash
streamlit run app.py
\`\`\`

4. **Accéder au dashboard**
- Ouvrir votre navigateur à l'adresse: `http://localhost:8501`

## 📁 Structure du Projet

\`\`\`
dashboard-machine-coupe/
│
├── app.py                      # Application principale Streamlit
├── requirements.txt            # Dépendances Python
├── README.md                   # Documentation
│
├── utils/
│   ├── data_generator.py       # Générateur de données simulées
│   └── data_manager.py         # Gestionnaire de données
│
└── data/
    ├── machine_data.csv        # Données de la machine (généré)
    └── arrets_data.csv         # Données des arrêts (généré)
\`\`\`

## 🎮 Guide d'Utilisation

### Premier Lancement
1. Au premier lancement, des données simulées sont automatiquement générées
2. Naviguez entre les différents modes via la barre latérale
3. Explorez les fonctionnalités de chaque section

### Mode Suivi Instantané
- Surveillez l'état actuel de la machine
- Ajustez la période d'affichage (1-24h)
- Observez les courbes de vibration en temps réel
- Vérifiez les alertes et métriques

### Saisie des Causes d'Arrêt
- Documentez chaque arrêt de la machine
- Sélectionnez le type et la cause
- Ajoutez des commentaires détaillés
- Consultez l'historique des interventions

### Mode Historique
- Analysez les performances sur plusieurs jours/semaines
- Filtrez par date et type d'événement
- Exportez les données pour analyse externe
- Générez des rapports de synthèse

## 📊 Données Simulées

Le système génère des données réalistes incluant:
- **États machine**: En marche, Panne, Arrêt production, Problème qualité
- **Vibrations**: Valeurs X, Y, Z avec corrélations réalistes
- **Transitions**: Changements d'état logiques et temporisés
- **Anomalies**: Pics de vibration et dégradations progressives

## 🔧 Configuration Avancée

### Paramètres de Vibration
- Seuils d'alerte configurables
- Paramètres par état de machine
- Détection d'anomalies automatique

### Génération de Données
- Ajout de nouvelles données simulées
- Simulation d'anomalies spécifiques
- Nettoyage des données anciennes

## 📈 KPIs Calculés

- **TBF**: Temps Brut de Fonctionnement
- **TFN**: Temps de Fonctionnement Net
- **Disponibilité**: Pourcentage de temps opérationnel
- **MTBF**: Temps Moyen Entre Pannes
- **MTTR**: Temps Moyen de Réparation
- **Taux de Panne**: Pourcentage de temps en panne

## 🚀 Évolutions Futures

### Phase 1: Intégration IoT Réelle
- Connexion avec capteurs ESP32
- Transmission de données en temps réel
- Protocoles MQTT/HTTP

### Phase 2: Intelligence Artificielle
- Modèles de machine learning pour prédiction
- Détection d'anomalies avancée
- Recommandations de maintenance

### Phase 3: Optimisation
- Base de données robuste (PostgreSQL/MongoDB)
- API REST pour intégration
- Interface mobile

## 🐛 Dépannage

### Problèmes Courants

**Erreur au lancement**
\`\`\`bash
# Vérifier l'installation de Streamlit
pip install --upgrade streamlit

# Relancer l'application
streamlit run app.py
\`\`\`

**Données manquantes**
- Les données sont générées automatiquement au premier lancement
- Utiliser "Configuration > Générer Nouvelles Données" si nécessaire

**Performance lente**
- Réduire la période d'affichage dans le mode instantané
- Nettoyer les anciennes données via la configuration

## 📞 Support

Pour toute question ou problème:
1. Vérifier la documentation
2. Consulter les logs dans le terminal
3. Redémarrer l'application si nécessaire

## 📄 Licence

Ce projet est développé pour des fins de démonstration et d'apprentissage de la maintenance prédictive industrielle.

---

**Version**: 1.0  
**Dernière mise à jour**: Décembre 2024  
**Développé avec**: ❤️ et Streamlit
\`\`\`
