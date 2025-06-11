"""
Script de démonstration pour générer des données d'exemple
et tester les fonctionnalités du dashboard
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils.data_generator import DataGenerator
from utils.data_manager import DataManager
from datetime import datetime, timedelta
import pandas as pd

def main():
    print("🚀 Génération de données de démonstration")
    print("=" * 50)
    
    # Initialisation
    generator = DataGenerator()
    manager = DataManager()
    
    # 1. Génération des données initiales
    print("📊 Génération des données initiales (7 jours)...")
    df = generator.generate_initial_data(days=7)
    print(f"✅ {len(df)} enregistrements générés")
    
    # 2. Ajout d'anomalies pour la démonstration
    print("\n⚠️ Simulation d'anomalies...")
    generator.simulate_anomaly('vibration_spike')
    generator.simulate_anomaly('gradual_degradation')
    print("✅ Anomalies ajoutées")
    
    # 3. Génération de quelques arrêts d'exemple
    print("\n📝 Génération d'arrêts d'exemple...")
    
    arrets_exemple = [
        {
            'timestamp': datetime.now() - timedelta(hours=48),
            'type_arret': 'panne',
            'sous_categorie': 'Mécanique',
            'piece_concernee': 'Moteur principal',
            'duree_minutes': 45,
            'commentaire': 'Remplacement du roulement défaillant',
            'operateur':  'Jean Dupont'
        },
        {
            'timestamp': datetime.now() - timedelta(hours=36),
            'type_arret': 'changement_serie',
            'sous_categorie': 'Changement produit',
            'piece_concernee': '',
            'duree_minutes': 15,
            'commentaire': 'Changement de format standard',
            'operateur': 'Marie Martin'
        },
        {
            'timestamp': datetime.now() - timedelta(hours=24),
            'type_arret': 'micro_arret',
            'sous_categorie': '',
            'piece_concernee': 'Capteurs',
            'duree_minutes': 5,
            'commentaire': 'Recalibrage des capteurs',
            'operateur': 'Pierre Durand'
        },
        {
            'timestamp': datetime.now() - timedelta(hours=12),
            'type_arret': 'defaut_qualite',
            'sous_categorie': '',
            'piece_concernee': 'Lame de coupe',
            'duree_minutes': 30,
            'commentaire': 'Ajustement précision de coupe',
            'operateur': 'Sophie Bernard'
        },
        {
            'timestamp': datetime.now() - timedelta(hours=6),
            'type_arret': 'panne',
            'sous_categorie': 'Électrique',
            'piece_concernee': 'Système hydraulique',
            'duree_minutes': 60,
            'commentaire': 'Court-circuit dans le panneau de contrôle',
            'operateur': 'Jean Dupont'
        }
    ]
    
    for arret in arrets_exemple:
        manager.save_arret(arret)
    
    print(f"✅ {len(arrets_exemple)} arrêts d'exemple générés")
    
    # 4. Vérification des données
    print("\n🔍 Vérification des données...")
    df = manager.load_data()
    arrets = manager.load_arrets()
    
    print(f"• Données machine: {len(df)} enregistrements")
    print(f"• Données arrêts: {len(arrets)} enregistrements")
    
    # 5. Calcul des KPIs
    print("\n📊 Calcul des KPIs...")
    kpis = manager.calculate_kpis(df)
    print("• TBF (Temps Brut Fonctionnement):", kpis.get('TBF', 0), "%")
    print("• Disponibilité:", kpis.get('Disponibilite', 0), "%")
    print("• MTBF:", kpis.get('MTBF', 0), "heures")
    print("• MTTR:", kpis.get('MTTR', 0), "heures")
    
    print("\n✅ Données de démonstration générées avec succès!")
    print("Lancez l'application avec: streamlit run app.py")

if __name__ == "__main__":
    main()
