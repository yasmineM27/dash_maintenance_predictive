import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import os
import random

class DataGenerator:
    def __init__(self):
        self.states = ['en_marche', 'panne', 'arret_production', 'probleme_qualite']
        self.state_probabilities = [0.7, 0.1, 0.15, 0.05]  # Probabilités de chaque état
        
        # Paramètres de vibration selon l'état
        self.vibration_params = {
            'en_marche': {'mean': 0.8, 'std': 0.3, 'min': 0.2, 'max': 1.5},
            'panne': {'mean': 3.0, 'std': 1.0, 'min': 2.0, 'max': 5.0},
            'arret_production': {'mean': 0.1, 'std': 0.05, 'min': 0.0, 'max': 0.3},
            'probleme_qualite': {'mean': 1.2, 'std': 0.4, 'min': 0.8, 'max': 2.0}
        }
    
    def generate_vibration(self, state):
        """Génère des valeurs de vibration réalistes selon l'état de la machine"""
        params = self.vibration_params[state]
        
        # Génération avec distribution normale tronquée
        vibration = np.random.normal(params['mean'], params['std'])
        vibration = np.clip(vibration, params['min'], params['max'])
        
        return round(vibration, 2)
    
    def generate_state_sequence(self, duration_hours):
        """Génère une séquence d'états réaliste avec transitions logiques"""
        total_minutes = duration_hours * 60
        states = []
        current_state = 'en_marche'
        
        i = 0
        while i < total_minutes:
            # Durée dans l'état actuel (variable selon l'état)
            if current_state == 'en_marche':
                duration = random.randint(30, 180)  # 30min à 3h
            elif current_state == 'panne':
                duration = random.randint(15, 60)   # 15min à 1h
            elif current_state == 'arret_production':
                duration = random.randint(10, 45)   # 10min à 45min
            else:  # probleme_qualite
                duration = random.randint(5, 30)    # 5min à 30min
            
            # Ajout de l'état pour la durée calculée
            for _ in range(min(duration, total_minutes - i)):
                states.append(current_state)
                i += 1
            
            # Transition vers le prochain état
            if current_state == 'en_marche':
                current_state = np.random.choice(
                    ['en_marche', 'panne', 'arret_production', 'probleme_qualite'],
                    p=[0.85, 0.05, 0.08, 0.02]
                )
            elif current_state == 'panne':
                current_state = np.random.choice(['en_marche', 'arret_production'], p=[0.7, 0.3])
            elif current_state == 'arret_production':
                current_state = np.random.choice(['en_marche', 'panne'], p=[0.9, 0.1])
            else:  # probleme_qualite
                current_state = np.random.choice(['en_marche', 'arret_production'], p=[0.8, 0.2])
        
        return states[:total_minutes]
    
    def generate_data(self, start_time, duration_hours):
        """Génère un dataset complet pour la période spécifiée"""
        states = self.generate_state_sequence(duration_hours)
        
        data = []
        current_time = start_time
        
        for state in states:
            # Génération des vibrations pour chaque axe
            vib_x = self.generate_vibration(state)
            vib_y = self.generate_vibration(state)
            vib_z = self.generate_vibration(state)
            
            # Ajout de corrélation entre les axes
            if state == 'panne':
                # En cas de panne, les vibrations sont corrélées
                correlation_factor = random.uniform(0.7, 0.9)
                vib_y = vib_x * correlation_factor + random.uniform(-0.2, 0.2)
                vib_z = vib_x * correlation_factor + random.uniform(-0.2, 0.2)
            
            # Ajout de bruit réaliste
            vib_x += random.uniform(-0.05, 0.05)
            vib_y += random.uniform(-0.05, 0.05)
            vib_z += random.uniform(-0.05, 0.05)
            
            # Contraintes physiques
            vib_x = max(0, round(vib_x, 2))
            vib_y = max(0, round(vib_y, 2))
            vib_z = max(0, round(vib_z, 2))
            
            data.append({
                'timestamp': current_time.strftime('%Y-%m-%d %H:%M:%S'),
                'etat_machine': state,
                'vibration_x': vib_x,
                'vibration_y': vib_y,
                'vibration_z': vib_z
            })
            
            current_time += timedelta(minutes=1)
        
        return pd.DataFrame(data)
    
    def generate_initial_data(self, days=7):
        """Génère les données initiales pour le dashboard"""
        if not os.path.exists('data'):
            os.makedirs('data')
        
        # Génération des données des 7 derniers jours
        end_time = datetime.now()
        start_time = end_time - timedelta(days=days)
        
        df = self.generate_data(start_time, days * 24)
        
        # Sauvegarde
        df.to_csv('data/machine_data.csv', index=False)
        print(f"✅ Données initiales générées: {len(df)} enregistrements")
        
        return df
    
    def generate_additional_data(self, hours=24):
        """Ajoute de nouvelles données au dataset existant"""
        # Chargement des données existantes
        if os.path.exists('data/machine_data.csv'):
            existing_df = pd.read_csv('data/machine_data.csv')
            last_timestamp = pd.to_datetime(existing_df['timestamp'].iloc[-1])
        else:
            existing_df = pd.DataFrame()
            last_timestamp = datetime.now() - timedelta(hours=hours)
        
        # Génération des nouvelles données
        start_time = last_timestamp + timedelta(minutes=1)
        new_df = self.generate_data(start_time, hours)
        
        # Fusion et sauvegarde
        if len(existing_df) > 0:
            combined_df = pd.concat([existing_df, new_df], ignore_index=True)
        else:
            combined_df = new_df
        
        combined_df.to_csv('data/machine_data.csv', index=False)
        print(f"✅ {len(new_df)} nouveaux enregistrements ajoutés")
        
        return new_df
    
    def simulate_anomaly(self, anomaly_type='vibration_spike'):
        """Simule une anomalie spécifique dans les données"""
        if not os.path.exists('data/machine_data.csv'):
            self.generate_initial_data()
        
        df = pd.read_csv('data/machine_data.csv')
        
        if anomaly_type == 'vibration_spike':
            # Ajout d'un pic de vibration
            anomaly_start = len(df) - random.randint(50, 200)
            anomaly_duration = random.randint(5, 15)
            
            for i in range(anomaly_start, min(anomaly_start + anomaly_duration, len(df))):
                df.loc[i, 'vibration_x'] = random.uniform(3.0, 5.0)
                df.loc[i, 'vibration_y'] = random.uniform(3.0, 5.0)
                df.loc[i, 'vibration_z'] = random.uniform(3.0, 5.0)
                df.loc[i, 'etat_machine'] = 'panne'
        
        elif anomaly_type == 'gradual_degradation':
            # Dégradation progressive
            degradation_start = len(df) - random.randint(200, 500)
            
            for i in range(degradation_start, len(df)):
                progress = (i - degradation_start) / (len(df) - degradation_start)
                degradation_factor = 1 + progress * 0.5  # Augmentation progressive
                
                df.loc[i, 'vibration_x'] *= degradation_factor
                df.loc[i, 'vibration_y'] *= degradation_factor
                df.loc[i, 'vibration_z'] *= degradation_factor
        
        df.to_csv('data/machine_data.csv', index=False)
        print(f"✅ Anomalie '{anomaly_type}' simulée")
        
        return df

if __name__ == "__main__":
    # Test du générateur
    generator = DataGenerator()
    generator.generate_initial_data()
    generator.simulate_anomaly('vibration_spike')
