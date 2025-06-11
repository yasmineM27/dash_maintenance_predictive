import pandas as pd
import numpy as np
import os
import json
from datetime import datetime, timedelta

class DataManager:
    def __init__(self):
        self.data_file = 'data/machine_data.csv'
        self.arrets_file = 'data/arrets_data.csv'
        
        # Création du dossier data si nécessaire
        if not os.path.exists('data'):
            os.makedirs('data')
    
    def load_data(self):
        """Charge les données de la machine"""
        if os.path.exists(self.data_file):
            df = pd.read_csv(self.data_file)
            df['timestamp'] = pd.to_datetime(df['timestamp'])
            return df
        else:
            # Retourne un DataFrame vide avec la structure attendue
            return pd.DataFrame(columns=['timestamp', 'etat_machine', 'vibration_x', 'vibration_y', 'vibration_z'])
    
    def save_data(self, df):
        """Sauvegarde les données de la machine"""
        df.to_csv(self.data_file, index=False)
    
    def load_arrets(self):
        """Charge les données des arrêts"""
        if os.path.exists(self.arrets_file):
            df = pd.read_csv(self.arrets_file)
            df['timestamp'] = pd.to_datetime(df['timestamp'])
            return df.sort_values('timestamp', ascending=False)
        else:
            return pd.DataFrame(columns=[
                'timestamp', 'type_arret', 'sous_categorie', 'piece_concernee',
                'duree_minutes', 'commentaire', 'operateur'
            ])
    
    def save_arret(self, arret_data):
        """Sauvegarde un nouvel arrêt"""
        # Chargement des arrêts existants
        arrets_df = self.load_arrets()
        
        # Ajout du nouvel arrêt
        new_arret = pd.DataFrame([arret_data])
        arrets_df = pd.concat([new_arret, arrets_df], ignore_index=True)
        
        # Sauvegarde
        arrets_df.to_csv(self.arrets_file, index=False)
    
    def get_machine_status_summary(self, df, hours=24):
        """Calcule un résumé du statut de la machine"""
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
        cutoff_time = datetime.now() - timedelta(hours=hours)
        recent_data = df[df['timestamp'] >= cutoff_time]
        
        if len(recent_data) == 0:
            return {}
        
        stats = {}
        for axis in ['vibration_x', 'vibration_y', 'vibration_z']:
            stats[axis] = {
                'mean': round(recent_data[axis].mean(), 2),
                'std': round(recent_data[axis].std(), 2),
                'min': round(recent_data[axis].min(), 2),
                'max': round(recent_data[axis].max(), 2),
                'current': round(recent_data[axis].iloc[-1], 2)
            }
        
        return stats
    
    def detect_anomalies(self, df, threshold_multiplier=2.5):
        """Détecte les anomalies dans les données de vibration"""
        anomalies = []
        
        for axis in ['vibration_x', 'vibration_y', 'vibration_z']:
            mean_val = df[axis].mean()
            std_val = df[axis].std()
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
        if start_date:
            df = df[df['timestamp'] >= pd.to_datetime(start_date)]
        if end_date:
            df = df[df['timestamp'] <= pd.to_datetime(end_date)]
        
        if len(df) == 0:
            return {}
        
        total_points = len(df)
        
        # Calcul des temps
        temps_marche = len(df[df['etat_machine'] == 'en_marche'])
        temps_panne = len(df[df['etat_machine'] == 'panne'])
        temps_arret_prod = len(df[df['etat_machine'] == 'arret_production'])
        temps_qualite = len(df[df['etat_machine'] == 'probleme_qualite'])
        
        # KPIs principaux
        kpis = {
            'TBF': round((temps_marche / total_points) * 100, 1),  # Temps Brut de Fonctionnement
            'TFN': round(((temps_marche + temps_arret_prod) / total_points) * 100, 1),  # Temps de Fonctionnement Net
            'Disponibilite': round(((total_points - temps_panne) / total_points) * 100, 1),
            'Taux_Panne': round((temps_panne / total_points) * 100, 1),
            'Taux_Qualite': round((temps_qualite / total_points) * 100, 1),
            'MTBF': self.calculate_mtbf(df),  # Mean Time Between Failures
            'MTTR': self.calculate_mttr(df)   # Mean Time To Repair
        }
        
        return kpis
    
    def calculate_mtbf(self, df):
        """Calcule le MTBF (Mean Time Between Failures)"""
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
        
        if format == 'csv':
            filepath = f'data/{filename}.csv'
            df.to_csv(filepath, index=False)
        elif format == 'json':
            filepath = f'data/{filename}.json'
            df.to_json(filepath, orient='records', date_format='iso')
        elif format == 'excel':
            filepath = f'data/{filename}.xlsx'
            df.to_excel(filepath, index=False)
        
        return filepath
    
    def generate_report(self, df, start_date, end_date):
        """Génère un rapport de synthèse"""
        kpis = self.calculate_kpis(df, start_date, end_date)
        anomalies = self.detect_anomalies(df)
        vibration_stats = self.get_vibration_statistics(df, hours=24*7)  # 7 jours
        
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

STATISTIQUES DE VIBRATION
-------------------------
• Vibration X - Moyenne: {vibration_stats.get('vibration_x', {}).get('mean', 0)} mm/s
• Vibration Y - Moyenne: {vibration_stats.get('vibration_y', {}).get('mean', 0)} mm/s
• Vibration Z - Moyenne: {vibration_stats.get('vibration_z', {}).get('mean', 0)} mm/s

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
        
        report += "\n" + "="*50 + "\n"
        
        return report
    
    def cleanup_old_data(self, days=30):
        """Nettoie les données anciennes"""
        cutoff_date = datetime.now() - timedelta(days=days)
        
        # Nettoyage des données machine
        if os.path.exists(self.data_file):
            df = self.load_data()
            df_cleaned = df[df['timestamp'] >= cutoff_date]
            self.save_data(df_cleaned)
            removed_count = len(df) - len(df_cleaned)
            print(f"✅ {removed_count} enregistrements machine supprimés")
        
        # Nettoyage des données d'arrêts
        if os.path.exists(self.arrets_file):
            arrets_df = self.load_arrets()
            arrets_cleaned = arrets_df[arrets_df['timestamp'] >= cutoff_date]
            arrets_cleaned.to_csv(self.arrets_file, index=False)
            removed_arrets = len(arrets_df) - len(arrets_cleaned)
            print(f"✅ {removed_arrets} enregistrements d'arrêts supprimés")

if __name__ == "__main__":
    # Test du gestionnaire de données
    manager = DataManager()
    df = manager.load_data()
    print(f"Données chargées: {len(df)} enregistrements")
    
    if len(df) > 0:
        kpis = manager.calculate_kpis(df)
        print("KPIs calculés:", kpis)
        
        anomalies = manager.detect_anomalies(df)
        print(f"Anomalies détectées: {len(anomalies)}")
