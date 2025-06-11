import pandas as pd
import numpy as np
import os
import json
from datetime import datetime, timedelta
import warnings
warnings.filterwarnings('ignore')

class DataManager:
    def __init__(self):
        self.data_file = 'data/machine_data.csv'
        self.arrets_file = 'data/arrets_data.csv'
        self.arrets_auto_file = 'data/arrets_auto_data.csv'
        self.config_file = 'data/config.json'
        
        # Seuil de vibration pour détecter l'arrêt (proche de zéro)
        self.seuil_arret_vibration = 0.1
        
        # Classification des arrêts selon le diagramme
        self.types_arrets = {
            'maintenance_preventive': {
                'label': 'Maintenance préventive',
                'color': '#1f4e79',
                'sous_categories': ['Kit 500hr', 'Kit 1000hr', 'Kit 2000hr', 'Kit 4000hr'],
                'icon': '🔧'
            },
            'arret_prevu': {
                'label': 'Arrêt prévu',
                'color': '#40e0d0',
                'sous_categories': ['Changement de série', 'Nettoyage planifié', 'Formation', 'Réglage machine'],
                'icon': '📅'
            },
            'arret_imprevu': {
                'label': 'Arrêt imprévu',
                'color': '#9932cc',
                'sous_categories': ['Panne machine', 'Manque alimentation', 'Défaillance capteur', 'Problème hydraulique'],
                'icon': '⚠️'
            },
            'arret_conducteur': {
                'label': 'Arrêt conducteur',
                'color': '#ffd700',
                'sous_categories': ['Discussion technique', 'Besoin naturel', 'Pause', 'Formation opérateur'],
                'icon': '👤'
            },
            'arret_probleme_qualite': {
                'label': 'Arrêt problème qualité',
                'color': '#ff0000',
                'sous_categories': ['Défaut produit', 'Réglage qualité', 'Contrôle qualité', 'Non-conformité'],
                'icon': '🔍'
            }
        }
        
        # Composants de la machine
        self.composants_machine = [
            "Moteur principal",
            "Lame de coupe", 
            "Système hydraulique",
            "Capteurs de vibration",
            "Courroie de transmission",
            "Roulements",
            "Système électrique",
            "Système pneumatique",
            "Interface utilisateur",
            "Système de refroidissement",
            "Autre"
        ]
        
        # Niveaux d'urgence
        self.niveaux_urgence = ["Faible", "Moyen", "Élevé", "Critique"]
        
        # Création du dossier data si nécessaire
        if not os.path.exists('data'):
            os.makedirs('data')
        
        # Chargement de la configuration
        self.load_config()
    
    def load_config(self):
        """Charge la configuration du système"""
        default_config = {
            'seuil_vibration_alerte': 2.0,
            'seuil_vibration_critique': 4.0,
            'seuil_arret_vibration': 0.1,
            'duree_min_arret': 2,  # minutes
            'auto_detection_enabled': True,
            'notifications_enabled': True
        }
        
        if os.path.exists(self.config_file):
            try:
                with open(self.config_file, 'r') as f:
                    self.config = json.load(f)
                # Mise à jour avec les valeurs par défaut si manquantes
                for key, value in default_config.items():
                    if key not in self.config:
                        self.config[key] = value
            except:
                self.config = default_config
        else:
            self.config = default_config
            self.save_config()
    
    def save_config(self):
        """Sauvegarde la configuration"""
        with open(self.config_file, 'w') as f:
            json.dump(self.config, f, indent=2)
    
    def update_config(self, key, value):
        """Met à jour un paramètre de configuration"""
        self.config[key] = value
        self.save_config()
    
    def detect_machine_stops(self, df):
        """Détecte automatiquement les arrêts de machine basés sur les vibrations"""
        if len(df) == 0:
            return []
        
        # Calcul de la vibration totale (magnitude)
        df = df.copy()
        df['vibration_totale'] = np.sqrt(
            df['vibration_x']**2 + 
            df['vibration_y']**2 + 
            df['vibration_z']**2
        )
        
        # Détection des périodes d'arrêt (vibration proche de zéro)
        df['machine_arretee'] = df['vibration_totale'] <= self.config['seuil_arret_vibration']
        
        # Identification des transitions
        df['transition'] = df['machine_arretee'].diff()
        
        arrets_detectes = []
        debut_arret = None
        
        for idx, row in df.iterrows():
            # Début d'arrêt (transition vers arrêt)
            if row['transition'] == True:
                debut_arret = row['timestamp']
            
            # Fin d'arrêt (transition vers fonctionnement)
            elif row['transition'] == False and debut_arret is not None:
                fin_arret = row['timestamp']
                duree_minutes = (pd.to_datetime(fin_arret) - pd.to_datetime(debut_arret)).total_seconds() / 60
                
                # Ne considérer que les arrêts de plus de la durée minimale configurée
                if duree_minutes >= self.config['duree_min_arret']:
                    arrets_detectes.append({
                        'debut_arret': debut_arret,
                        'fin_arret': fin_arret,
                        'duree_minutes': round(duree_minutes, 1),
                        'statut': 'detecte_auto',
                        'necessite_classification': True,
                        'date_detection': datetime.now(),
                        'classifie': False
                    })
                
                debut_arret = None
        
        return arrets_detectes
    
    def load_arrets_auto(self):
        """Charge les arrêts détectés automatiquement"""
        if os.path.exists(self.arrets_auto_file):
            try:
                df = pd.read_csv(self.arrets_auto_file)
                df['debut_arret'] = pd.to_datetime(df['debut_arret'])
                df['fin_arret'] = pd.to_datetime(df['fin_arret'])
                if 'date_detection' in df.columns:
                    df['date_detection'] = pd.to_datetime(df['date_detection'])
                if 'date_classification' in df.columns:
                    df['date_classification'] = pd.to_datetime(df['date_classification'])
                return df.sort_values('debut_arret', ascending=False)
            except Exception as e:
                print(f"Erreur lors du chargement des arrêts auto: {e}")
                return self._create_empty_arrets_auto_df()
        else:
            return self._create_empty_arrets_auto_df()
    
    def _create_empty_arrets_auto_df(self):
        """Crée un DataFrame vide pour les arrêts automatiques"""
        return pd.DataFrame(columns=[
            'debut_arret', 'fin_arret', 'duree_minutes', 'statut',
            'type_arret', 'sous_categorie', 'commentaire', 'operateur', 
            'classifie', 'date_detection', 'date_classification', 'urgence'
        ])
    
    def save_arret_auto(self, arret_data):
        """Sauvegarde un arrêt détecté automatiquement"""
        arrets_df = self.load_arrets_auto()
        
        # Vérification des doublons
        if len(arrets_df) > 0:
            # Vérifier si un arrêt similaire existe déjà
            debut_arret = pd.to_datetime(arret_data['debut_arret'])
            existing = arrets_df[
                (abs((arrets_df['debut_arret'] - debut_arret).dt.total_seconds()) < 300)  # 5 minutes de tolérance
            ]
            if len(existing) > 0:
                return False  # Arrêt déjà existant
        
        new_arret = pd.DataFrame([arret_data])
        arrets_df = pd.concat([new_arret, arrets_df], ignore_index=True)
        arrets_df.to_csv(self.arrets_auto_file, index=False)
        return True
    
    def classifier_arret(self, arret_id, type_arret, sous_categorie, commentaire, operateur, urgence="Moyen"):
        """Classifie un arrêt détecté automatiquement"""
        arrets_df = self.load_arrets_auto()
        
        if arret_id < len(arrets_df):
            arrets_df.loc[arret_id, 'type_arret'] = type_arret
            arrets_df.loc[arret_id, 'sous_categorie'] = sous_categorie
            arrets_df.loc[arret_id, 'commentaire'] = commentaire
            arrets_df.loc[arret_id, 'operateur'] = operateur
            arrets_df.loc[arret_id, 'urgence'] = urgence
            arrets_df.loc[arret_id, 'classifie'] = True
            arrets_df.loc[arret_id, 'date_classification'] = datetime.now()
            
            arrets_df.to_csv(self.arrets_auto_file, index=False)
            return True
        return False
    
    def get_arrets_non_classifies(self):
        """Retourne les arrêts non encore classifiés"""
        arrets_df = self.load_arrets_auto()
        if len(arrets_df) == 0:
            return arrets_df
        return arrets_df[arrets_df.get('classifie', False) != True]
    
    def load_data(self):
        """Charge les données de la machine"""
        if os.path.exists(self.data_file):
            try:
                df = pd.read_csv(self.data_file)
                df['timestamp'] = pd.to_datetime(df['timestamp'])
                return df
            except Exception as e:
                print(f"Erreur lors du chargement des données: {e}")
                return self._create_empty_machine_df()
        else:
            return self._create_empty_machine_df()
    
    def _create_empty_machine_df(self):
        """Crée un DataFrame vide pour les données machine"""
        return pd.DataFrame(columns=['timestamp', 'etat_machine', 'vibration_x', 'vibration_y', 'vibration_z'])
    
    def save_data(self, df):
        """Sauvegarde les données de la machine"""
        try:
            df.to_csv(self.data_file, index=False)
            return True
        except Exception as e:
            print(f"Erreur lors de la sauvegarde: {e}")
            return False
    
    def load_arrets(self):
        """Charge les données des arrêts manuels"""
        if os.path.exists(self.arrets_file):
            try:
                df = pd.read_csv(self.arrets_file)
                df['timestamp'] = pd.to_datetime(df['timestamp'])
                if 'date_saisie' in df.columns:
                    df['date_saisie'] = pd.to_datetime(df['date_saisie'])
                return df.sort_values('timestamp', ascending=False)
            except Exception as e:
                print(f"Erreur lors du chargement des arrêts: {e}")
                return self._create_empty_arrets_df()
        else:
            return self._create_empty_arrets_df()
    
    def _create_empty_arrets_df(self):
        """Crée un DataFrame vide pour les arrêts manuels"""
        return pd.DataFrame(columns=[
            'timestamp', 'type_arret', 'sous_categorie', 'piece_concernee',
            'duree_minutes', 'commentaire', 'operateur', 'urgence', 'date_saisie'
        ])
    
    def save_arret(self, arret_data):
        """Sauvegarde un nouvel arrêt manuel"""
        try:
            arrets_df = self.load_arrets()
            new_arret = pd.DataFrame([arret_data])
            arrets_df = pd.concat([new_arret, arrets_df], ignore_index=True)
            arrets_df.to_csv(self.arrets_file, index=False)
            return True
        except Exception as e:
            print(f"Erreur lors de la sauvegarde de l'arrêt: {e}")
            return False
    
    def get_machine_status_summary(self, df, hours=24):
        """Calcule un résumé du statut de la machine"""
        if len(df) == 0:
            return {}
        
        cutoff_time = datetime.now() - timedelta(hours=hours)
        recent_data = df[df['timestamp'] >= cutoff_time]
        
        if len(recent_data) == 0:
            return {}
        
        total_points = len(recent_data)
        summary = {}
        
        for state in recent_data['etat_machine'].unique():
            count = len(recent_data[recent_data['etat_machine'] == state])
            percentage = (count / total_points) * 100
            summary[state] = {
                'count': count,
                'percentage': round(percentage, 1),
                'duration_hours': round((count / 60), 1)  # Approximation si 1 point = 1 minute
            }
        
        return summary
    
    def get_vibration_statistics(self, df, hours=24):
        """Calcule les statistiques de vibration"""
        if len(df) == 0:
            return {}
        
        cutoff_time = datetime.now() - timedelta(hours=hours)
        recent_data = df[df['timestamp'] >= cutoff_time]
        
        if len(recent_data) == 0:
            return {}
        
        stats = {}
        for axis in ['vibration_x', 'vibration_y', 'vibration_z']:
            if axis in recent_data.columns:
                stats[axis] = {
                    'mean': round(recent_data[axis].mean(), 2),
                    'std': round(recent_data[axis].std(), 2),
                    'min': round(recent_data[axis].min(), 2),
                    'max': round(recent_data[axis].max(), 2),
                    'current': round(recent_data[axis].iloc[-1], 2) if len(recent_data) > 0 else 0
                }
        
        return stats
    
    def detect_anomalies(self, df, threshold_multiplier=2.5):
        """Détecte les anomalies dans les données de vibration"""
        if len(df) == 0:
            return []
        
        anomalies = []
        
        for axis in ['vibration_x', 'vibration_y', 'vibration_z']:
            if axis not in df.columns:
                continue
                
            mean_val = df[axis].mean()
            std_val = df[axis].std()
            
            if std_val == 0:  # Éviter la division par zéro
                continue
                
            threshold = mean_val + (threshold_multiplier * std_val)
            
            anomaly_points = df[df[axis] > threshold]
            
            for idx, point in anomaly_points.iterrows():
                anomalies.append({
                    'timestamp': point['timestamp'],
                    'axis': axis,
                    'value': point[axis],
                    'threshold': round(threshold, 2),
                    'severity': 'high' if point[axis] > threshold * 1.5 else 'medium'
                })
        
        return sorted(anomalies, key=lambda x: x['timestamp'], reverse=True)
    
    def calculate_kpis(self, df, start_date=None, end_date=None):
        """Calcule les KPIs de performance de la machine"""
        if len(df) == 0:
            return {}
        
        df_filtered = df.copy()
        
        if start_date:
            df_filtered = df_filtered[df_filtered['timestamp'] >= pd.to_datetime(start_date)]
        if end_date:
            df_filtered = df_filtered[df_filtered['timestamp'] <= pd.to_datetime(end_date)]
        
        if len(df_filtered) == 0:
            return {}
        
        total_points = len(df_filtered)
        
        # Calcul des temps
        temps_marche = len(df_filtered[df_filtered['etat_machine'] == 'en_marche'])
        temps_panne = len(df_filtered[df_filtered['etat_machine'] == 'panne'])
        temps_arret_prod = len(df_filtered[df_filtered['etat_machine'] == 'arret_production'])
        temps_qualite = len(df_filtered[df_filtered['etat_machine'] == 'probleme_qualite'])
        
        # KPIs principaux
        kpis = {
            'TBF': round((temps_marche / total_points) * 100, 1),  # Temps Brut de Fonctionnement
            'TFN': round(((temps_marche + temps_arret_prod) / total_points) * 100, 1),  # Temps de Fonctionnement Net
            'Disponibilite': round(((total_points - temps_panne) / total_points) * 100, 1),
            'Taux_Panne': round((temps_panne / total_points) * 100, 1),
            'Taux_Qualite': round((temps_qualite / total_points) * 100, 1),
            'MTBF': self.calculate_mtbf(df_filtered),  # Mean Time Between Failures
            'MTTR': self.calculate_mttr(df_filtered),   # Mean Time To Repair
            'Efficacite_Globale': round(((temps_marche / total_points) * 100) * 0.95, 1)  # OEE approximatif
        }
        
        return kpis
    
    def calculate_mtbf(self, df):
        """Calcule le MTBF (Mean Time Between Failures)"""
        if len(df) == 0:
            return 0
        
        # Identification des périodes de panne
        panne_starts = []
        in_panne = False
        
        for idx, row in df.iterrows():
            if row['etat_machine'] == 'panne' and not in_panne:
                panne_starts.append(row['timestamp'])
                in_panne = True
            elif row['etat_machine'] != 'panne' and in_panne:
                in_panne = False
        
        if len(panne_starts) <= 1:
            return 0
        
        # Calcul des intervalles entre pannes
        intervals = []
        for i in range(1, len(panne_starts)):
            interval = (panne_starts[i] - panne_starts[i-1]).total_seconds() / 3600  # en heures
            intervals.append(interval)
        
        return round(np.mean(intervals), 1) if intervals else 0
    
    def calculate_mttr(self, df):
        """Calcule le MTTR (Mean Time To Repair)"""
        if len(df) == 0:
            return 0
        
        panne_durations = []
        panne_start = None
        
        for idx, row in df.iterrows():
            if row['etat_machine'] == 'panne' and panne_start is None:
                panne_start = row['timestamp']
            elif row['etat_machine'] != 'panne' and panne_start is not None:
                duration = (row['timestamp'] - panne_start).total_seconds() / 3600  # en heures
                panne_durations.append(duration)
                panne_start = None
        
        return round(np.mean(panne_durations), 1) if panne_durations else 0
    
    def export_data(self, df, format='csv', filename=None):
        """Exporte les données dans différents formats"""
        if filename is None:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = f'export_machine_{timestamp}'
        
        try:
            if format == 'csv':
                filepath = f'data/{filename}.csv'
                df.to_csv(filepath, index=False)
            elif format == 'json':
                filepath = f'data/{filename}.json'
                df.to_json(filepath, orient='records', date_format='iso')
            elif format == 'excel':
                filepath = f'data/{filename}.xlsx'
                df.to_excel(filepath, index=False)
            else:
                return None
            
            return filepath
        except Exception as e:
            print(f"Erreur lors de l'export: {e}")
            return None
    
    def generate_report(self, df, start_date, end_date):
        """Génère un rapport de synthèse complet"""
        try:
            kpis = self.calculate_kpis(df, start_date, end_date)
            anomalies = self.detect_anomalies(df)
            vibration_stats = self.get_vibration_statistics(df, hours=24*7)  # 7 jours
            
            # Statistiques des arrêts
            arrets_auto = self.load_arrets_auto()
            arrets_manuels = self.load_arrets()
            
            report = f"""
RAPPORT DE MAINTENANCE PRÉDICTIVE
=================================

Période d'analyse: {start_date} à {end_date}
Date de génération: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}

INDICATEURS DE PERFORMANCE (KPIs)
---------------------------------
• Temps Brut de Fonctionnement (TBF): {kpis.get('TBF', 0)}%
• Temps de Fonctionnement Net (TFN): {kpis.get('TFN', 0)}%
• Disponibilité: {kpis.get('Disponibilite', 0)}%
• Taux de Panne: {kpis.get('Taux_Panne', 0)}%
• Taux Problème Qualité: {kpis.get('Taux_Qualite', 0)}%
• MTBF (Temps Moyen Entre Pannes): {kpis.get('MTBF', 0)} heures
• MTTR (Temps Moyen de Réparation): {kpis.get('MTTR', 0)} heures
• Efficacité Globale (OEE): {kpis.get('Efficacite_Globale', 0)}%

DÉTECTION AUTOMATIQUE D'ARRÊTS
------------------------------
"""
            
            if len(arrets_auto) > 0:
                arrets_periode = arrets_auto[
                    (arrets_auto['debut_arret'] >= pd.to_datetime(start_date)) &
                    (arrets_auto['debut_arret'] <= pd.to_datetime(end_date))
                ]
                
                classifies = len(arrets_periode[arrets_periode.get('classifie', False) == True])
                taux_classification = (classifies / len(arrets_periode)) * 100 if len(arrets_periode) > 0 else 0
                
                report += f"• Arrêts détectés automatiquement: {len(arrets_periode)}\n"
                report += f"• Arrêts classifiés: {classifies}\n"
                report += f"• Taux de classification: {taux_classification:.1f}%\n"
                report += f"• Durée totale d'arrêts: {arrets_periode['duree_minutes'].sum():.1f} minutes\n"
                
                # Répartition par type d'arrêt
                if classifies > 0:
                    arrets_classifies = arrets_periode[arrets_periode.get('classifie', False) == True]
                    report += "\nRépartition des arrêts classifiés:\n"
                    for type_arret in arrets_classifies['type_arret'].value_counts().items():
                        type_label = self.types_arrets.get(type_arret[0], {'label': type_arret[0]})['label']
                        report += f"  - {type_label}: {type_arret[1]} arrêts\n"
            
            report += f"""

ARRÊTS MANUELS
--------------
• Total arrêts saisis manuellement: {len(arrets_manuels)}
• Durée totale: {arrets_manuels['duree_minutes'].sum():.1f} minutes
"""
            
            report += f"""

STATISTIQUES DE VIBRATION
-------------------------
"""
            for axis, stats in vibration_stats.items():
                report += f"• {axis.upper()} - Moyenne: {stats.get('mean', 0)} mm/s, Max: {stats.get('max', 0)} mm/s\n"
            
            report += f"""

ANOMALIES DÉTECTÉES
------------------
Nombre d'anomalies: {len(anomalies)}
"""
            
            if anomalies:
                report += "\nDétail des anomalies récentes:\n"
                for i, anomaly in enumerate(anomalies[:5]):  # Top 5
                    report += f"• {anomaly['timestamp'].strftime('%d/%m/%Y %H:%M')} - {anomaly['axis']}: {anomaly['value']} mm/s (Seuil: {anomaly['threshold']})\n"
            
            report += f"""

RECOMMANDATIONS
---------------
"""
            
            # Recommandations basées sur les KPIs
            if kpis.get('Taux_Panne', 0) > 10:
                report += "• CRITIQUE: Taux de panne élevé - Inspection immédiate recommandée\n"
            
            if kpis.get('Disponibilite', 100) < 85:
                report += "• ATTENTION: Disponibilité faible - Révision de la maintenance préventive\n"
            
            if len(anomalies) > 10:
                report += "• INFO: Nombreuses anomalies détectées - Surveillance renforcée conseillée\n"
            
            if all(kpi > 90 for kpi in [kpis.get('TBF', 0), kpis.get('Disponibilite', 0)]):
                report += "• EXCELLENT: Performance optimale - Maintenir le programme de maintenance actuel\n"
            
            # Recommandations sur la classification
            arrets_non_classifies = self.get_arrets_non_classifies()
            if len(arrets_non_classifies) > 0:
                report += f"• ACTION REQUISE: {len(arrets_non_classifies)} arrêts détectés nécessitent une classification\n"
            
            report += "\n" + "="*50 + "\n"
            
            return report
            
        except Exception as e:
            return f"Erreur lors de la génération du rapport: {e}"
    
    def cleanup_old_data(self, days=30):
        """Nettoie les données anciennes"""
        cutoff_date = datetime.now() - timedelta(days=days)
        removed_total = 0
        
        try:
            # Nettoyage des données machine
            if os.path.exists(self.data_file):
                df = self.load_data()
                df_cleaned = df[df['timestamp'] >= cutoff_date]
                self.save_data(df_cleaned)
                removed_count = len(df) - len(df_cleaned)
                removed_total += removed_count
                print(f"✅ {removed_count} enregistrements machine supprimés")
            
            # Nettoyage des données d'arrêts manuels
            if os.path.exists(self.arrets_file):
                arrets_df = self.load_arrets()
                arrets_cleaned = arrets_df[arrets_df['timestamp'] >= cutoff_date]
                arrets_cleaned.to_csv(self.arrets_file, index=False)
                removed_arrets = len(arrets_df) - len(arrets_cleaned)
                removed_total += removed_arrets
                print(f"✅ {removed_arrets} enregistrements d'arrêts manuels supprimés")
            
            # Nettoyage des données d'arrêts automatiques
            if os.path.exists(self.arrets_auto_file):
                arrets_auto_df = self.load_arrets_auto()
                arrets_auto_cleaned = arrets_auto_df[arrets_auto_df['debut_arret'] >= cutoff_date]
                arrets_auto_cleaned.to_csv(self.arrets_auto_file, index=False)
                removed_auto = len(arrets_auto_df) - len(arrets_auto_cleaned)
                removed_total += removed_auto
                print(f"✅ {removed_auto} enregistrements d'arrêts automatiques supprimés")
            
            return removed_total
            
        except Exception as e:
            print(f"Erreur lors du nettoyage: {e}")
            return 0
    
    def get_system_stats(self):
        """Retourne les statistiques système"""
        try:
            stats = {}
            
            # Statistiques des fichiers
            if os.path.exists(self.data_file):
                stats['machine_data_size'] = round(os.path.getsize(self.data_file) / 1024 / 1024, 2)  # MB
                df = self.load_data()
                stats['machine_records'] = len(df)
                stats['data_quality'] = round((1 - df.isnull().sum().sum() / (len(df) * len(df.columns))) * 100, 1) if len(df) > 0 else 100
                stats['date_debut'] = df['timestamp'].min() if len(df) > 0 else None
                stats['date_fin'] = df['timestamp'].max() if len(df) > 0 else None
            else:
                stats['machine_data_size'] = 0
                stats['machine_records'] = 0
                stats['data_quality'] = 100
                stats['date_debut'] = None
                stats['date_fin'] = None
            
            # Statistiques des arrêts
            arrets_manuels = self.load_arrets()
            arrets_auto = self.load_arrets_auto()
            
            stats['arrets_manuels'] = len(arrets_manuels)
            stats['arrets_auto_total'] = len(arrets_auto)
            stats['arrets_auto_classifies'] = len(arrets_auto[arrets_auto.get('classifie', False) == True]) if len(arrets_auto) > 0 else 0
            stats['taux_classification'] = round((stats['arrets_auto_classifies'] / stats['arrets_auto_total']) * 100, 1) if stats['arrets_auto_total'] > 0 else 100
            
            return stats
            
        except Exception as e:
            print(f"Erreur lors du calcul des statistiques: {e}")
            return {}
    
    def backup_data(self, backup_dir='backup'):
        """Crée une sauvegarde des données"""
        try:
            if not os.path.exists(backup_dir):
                os.makedirs(backup_dir)
            
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            backup_files = []
            
            # Sauvegarde des fichiers de données
            for file_path in [self.data_file, self.arrets_file, self.arrets_auto_file, self.config_file]:
                if os.path.exists(file_path):
                    filename = os.path.basename(file_path)
                    backup_filename = f"{timestamp}_{filename}"
                    backup_path = os.path.join(backup_dir, backup_filename)
                    
                    # Copie du fichier
                    import shutil
                    shutil.copy2(file_path, backup_path)
                    backup_files.append(backup_path)
            
            return backup_files
            
        except Exception as e:
            print(f"Erreur lors de la sauvegarde: {e}")
            return []

if __name__ == "__main__":
    # Test du gestionnaire de données
    manager = DataManager()
    
    # Test de chargement des données
    df = manager.load_data()
    print(f"Données chargées: {len(df)} enregistrements")
    
    if len(df) > 0:
        # Test des KPIs
        kpis = manager.calculate_kpis(df)
        print("KPIs calculés:", kpis)
        
        # Test de détection d'anomalies
        anomalies = manager.detect_anomalies(df)
        print(f"Anomalies détectées: {len(anomalies)}")
        
        # Test de détection d'arrêts
        arrets = manager.detect_machine_stops(df)
        print(f"Arrêts détectés: {len(arrets)}")
        
        # Test des statistiques système
        stats = manager.get_system_stats()
        print("Statistiques système:", stats)
