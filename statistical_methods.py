"""
Zusätzliche statistische Methoden zur Transaktionsanalyse

Implementiert:
1. Benford's Law - Erst-Ziffer-Analyse
2. Velocity Checks - Transaktionsgeschwindigkeit
3. Time-Series Anomaly Detection - Zeitreihen-Anomalien
4. Behavioral Clustering - Verhaltenscluster
5. Cash-to-Bank Layering - Geldwäsche durch Bar→SEPA Muster
"""

import numpy as np
import pandas as pd
from datetime import datetime, timedelta
from typing import List, Dict, Tuple
from collections import Counter
from models import Transaction, StatisticalAnalysis
from scipy import stats
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler


class StatisticalAnalyzer:
    """
    Erweiterte statistische Analysemethoden
    """
    
    def __init__(self):
        # Benford's Law erwartete Verteilung für Erst-Ziffern
        self.benford_expected = {
            1: 0.301, 2: 0.176, 3: 0.125, 4: 0.097, 5: 0.079,
            6: 0.067, 7: 0.058, 8: 0.051, 9: 0.046
        }
    
    def benford_analysis(self, transactions: List[Transaction]) -> float:
        """
        Benford's Law (Erst-Ziffer-Analyse)
        
        Natürliche Zahlen folgen einer logarithmischen Verteilung der Erst-Ziffern.
        Manipulierte oder konstruierte Zahlen weichen oft davon ab.
        
        Args:
            transactions: Liste von Transaktionen
            
        Returns:
            Abweichungs-Score (0-1, höher = verdächtiger)
        """
        if not transactions or len(transactions) < 20:
            return 0.0  # Zu wenig Daten für Benford's Law
        
        # Extrahiere Erst-Ziffern
        first_digits = []
        for t in transactions:
            amount_str = str(int(t.transaction_amount))
            if amount_str and amount_str[0] != '0':
                first_digits.append(int(amount_str[0]))
        
        if len(first_digits) < 20:
            return 0.0
        
        # Beobachtete Verteilung
        digit_counts = Counter(first_digits)
        total = len(first_digits)
        
        observed = {d: digit_counts.get(d, 0) / total for d in range(1, 10)}
        
        # Chi-Quadrat-Test gegen Benford's Law
        chi_squared = 0.0
        for digit in range(1, 10):
            expected = self.benford_expected[digit]
            obs = observed.get(digit, 0)
            
            if expected > 0:
                chi_squared += ((obs - expected) ** 2) / expected
        
        # Kritischer Wert für Chi-Quadrat (df=8, alpha=0.05) ≈ 15.5
        # Normalisiere zu 0-1 Score
        benford_score = min(chi_squared / 15.5, 1.0)
        
        return benford_score
    
    def velocity_analysis(
        self,
        transactions: List[Transaction],
        time_windows: List[int] = None
    ) -> float:
        """
        Velocity Check - Transaktionsgeschwindigkeit
        
        Misst:
        - Anzahl Transaktionen pro Zeiteinheit
        - Kumulative Beträge pro Zeiteinheit
        - Plötzliche Spitzen in Aktivität
        
        Args:
            transactions: Liste von Transaktionen
            time_windows: Zeitfenster in Stunden (Standard: [1, 24, 168])
            
        Returns:
            Velocity Score (0-1, höher = verdächtigere Geschwindigkeit)
        """
        if not transactions:
            return 0.0
        
        time_windows = time_windows or [1, 24, 168]  # 1h, 1d, 1w
        
        # Transaktionen mit Timestamp
        txns = sorted(
            [t for t in transactions if t.timestamp],
            key=lambda t: t.timestamp
        )
        
        if len(txns) < 3:
            return 0.0
        
        velocity_scores = []
        
        for window_hours in time_windows:
            window_td = timedelta(hours=window_hours)
            
            # Finde maximale Transaktionsdichte
            max_count = 0
            max_amount = 0.0
            
            for i, txn in enumerate(txns):
                window_start = txn.timestamp
                window_end = window_start + window_td
                
                # Zähle Transaktionen im Fenster
                count = sum(
                    1 for t in txns
                    if window_start <= t.timestamp < window_end
                )
                
                amount = sum(
                    t.transaction_amount for t in txns
                    if window_start <= t.timestamp < window_end
                )
                
                max_count = max(max_count, count)
                max_amount = max(max_amount, amount)
            
            # ==========================================
            # ABSOLUTE SCHWELLENWERTE (ohne historische Daten)
            # ==========================================
            # Diese Schwellenwerte funktionieren ohne historische Baseline
            
            # Normalisiere basierend auf Fenstergröße
            # ABSOLUTER SCHWELLENWERT: Mehr als 10 Transaktionen pro Tag ist ungewöhnlich
            expected_max_count = window_hours / 2.4  # ~10 pro 24h
            count_score = min(max_count / expected_max_count, 1.0)
            
            # ABSOLUTER SCHWELLENWERT: Mehr als 50k EUR pro Tag ist ungewöhnlich (für Privatkunden)
            expected_max_amount = (window_hours / 24.0) * 50000
            amount_score = min(max_amount / expected_max_amount, 1.0)
            
            velocity_scores.append((count_score + amount_score) / 2.0)
        
        # Durchschnitt über alle Fenster
        return np.mean(velocity_scores)
    
    def time_anomaly_detection(
        self,
        transactions: List[Transaction]
    ) -> float:
        """
        Zeitreihen-Anomalie-Detektion
        
        Erkennt:
        - Ungewöhnliche Uhrzeiten (z.B. 3 Uhr nachts)
        - Ungewöhnliche Wochentage (z.B. Sonntag)
        - Burst-Muster (viele Transaktionen in kurzer Zeit)
        
        Args:
            transactions: Liste von Transaktionen
            
        Returns:
            Anomalie-Score (0-1, höher = verdächtiger)
        """
        if not transactions:
            return 0.0
        
        txns = [t for t in transactions if t.timestamp]
        
        if len(txns) < 5:
            return 0.0
        
        anomaly_scores = []
        
        # ==========================================
        # ABSOLUTE SCHWELLENWERTE (ohne historische Daten)
        # ==========================================
        # Diese Schwellenwerte funktionieren ohne historische Baseline
        
        # 1. Ungewöhnliche Uhrzeiten (Off-Hours: 22:00 - 06:00)
        # ABSOLUTER SCHWELLENWERT: Nachts ist ungewöhnlich
        off_hours_count = sum(
            1 for t in txns
            if t.timestamp.hour < 6 or t.timestamp.hour >= 22
        )
        off_hours_ratio = off_hours_count / len(txns)
        anomaly_scores.append(off_hours_ratio)
        
        # 2. Wochenend-Transaktionen
        # ABSOLUTER SCHWELLENWERT: Mehr als 40% Wochenende ist ungewöhnlich
        weekend_count = sum(
            1 for t in txns
            if t.timestamp.weekday() >= 5  # Sa, So
        )
        weekend_ratio = weekend_count / len(txns)
        anomaly_scores.append(min(weekend_ratio / 0.4, 1.0))
        
        # 3. Burst-Detektion: mehrere Transaktionen innerhalb weniger Minuten
        # ABSOLUTER SCHWELLENWERT: 3 Transaktionen in 5 Minuten ist ungewöhnlich
        txns_sorted = sorted(txns, key=lambda t: t.timestamp)
        bursts = 0
        
        for i in range(len(txns_sorted) - 2):
            time_diff = (txns_sorted[i+2].timestamp - txns_sorted[i].timestamp).total_seconds() / 60.0
            if time_diff < 5:  # 3 Transaktionen in 5 Minuten
                bursts += 1
        
        burst_ratio = bursts / max(len(txns_sorted) - 2, 1)
        anomaly_scores.append(min(burst_ratio / 0.2, 1.0))
        
        return np.mean(anomaly_scores)
    
    def clustering_analysis(
        self,
        customer_transactions: List[Transaction],
        all_transactions: List[Transaction] = None,
        n_clusters: int = 5
    ) -> float:
        """
        Verhaltenscluster-Analyse
        
        Clustert Kunden basierend auf Transaktionsverhalten und
        misst, wie sehr ein Kunde vom Zentrum seines Clusters abweicht.
        
        Features:
        - Durchschnittlicher Betrag
        - Transaktionsfrequenz
        - Bevorzugte Zahlungsmethode
        - Investment vs. Auszahlung Ratio
        
        Args:
            customer_transactions: Transaktionen des Kunden
            all_transactions: Alle Transaktionen (für Clustering)
            n_clusters: Anzahl Cluster
            
        Returns:
            Clustering Score (0-1, höher = weiter vom Cluster-Zentrum)
        """
        if not customer_transactions:
            return 0.0
        
        # Wenn keine Vergleichsdaten, return neutral
        if not all_transactions or len(all_transactions) < 50:
            return 0.0
        
        # Extrahiere Features für Kunden
        customer_features = self._extract_features(customer_transactions)
        
        # Extrahiere Features für alle Kunden (grouped by customer_id)
        df = pd.DataFrame([
            {
                'customer_id': t.customer_id,
                'amount': t.transaction_amount,
                'payment_method': t.payment_method.value,
                'transaction_type': t.transaction_type.value
            }
            for t in all_transactions
        ])
        
        # Gruppiere nach Kunden
        all_features = []
        for cid, group in df.groupby('customer_id'):
            txns = [t for t in all_transactions if t.customer_id == cid]
            features = self._extract_features(txns)
            all_features.append(features)
        
        if len(all_features) < n_clusters:
            return 0.0
        
        # Clustering
        all_features_array = np.array(all_features)
        
        # Standardisiere
        scaler = StandardScaler()
        all_features_scaled = scaler.fit_transform(all_features_array)
        
        # K-Means
        kmeans = KMeans(n_clusters=n_clusters, random_state=42, n_init=10)
        kmeans.fit(all_features_scaled)
        
        # Transformiere Kunden-Features
        customer_features_array = np.array([customer_features])
        customer_features_scaled = scaler.transform(customer_features_array)
        
        # Finde nächstes Cluster
        distances = np.linalg.norm(
            kmeans.cluster_centers_ - customer_features_scaled[0],
            axis=1
        )
        min_distance = np.min(distances)
        
        # Normalisiere (typische Distanzen liegen bei 0-5)
        clustering_score = min(min_distance / 5.0, 1.0)
        
        return clustering_score
    
    def cash_to_bank_layering_detection(
        self,
        transactions: List[Transaction]
    ) -> float:
        """
        Erkennt Geldwäsche-Muster: Bar-Einzahlungen → SEPA/Kreditkarte-Auszahlungen
        
        Klassisches Layering-Muster:
        - Investments (Einzahlungen) hauptsächlich in Bar
        - Auszahlungen hauptsächlich in SEPA oder Kreditkarte
        - = Bargeld wird zu "sauberem" Bankgeld gewaschen
        
        Args:
            transactions: Liste von Transaktionen
            
        Returns:
            Layering Score (0-1, höher = verdächtiger)
        """
        if not transactions or len(transactions) < 3:
            return 0.0
        
        # Trenne nach Transaktionstyp
        investments = [t for t in transactions if t.transaction_type.value == "investment"]
        auszahlungen = [t for t in transactions if t.transaction_type.value == "auszahlung"]
        

        # WICHTIG: Auch wenn keine Auszahlungen vorhanden sind, kann es Layering sein
        # (wenn viele Bar-Investments vorhanden sind, aber keine Auszahlungen = verdächtig)
        if not investments:
            return 0.0  # Brauchen mindestens Investments
        
        # Wenn keine Auszahlungen, aber viele Bar-Investments, ist es auch verdächtig
        if not auszahlungen:
            # Prüfe ob viele Bar-Investments vorhanden sind
            bar_investments = [
                t for t in investments 
                if t.payment_method.value == "Bar"
            ]
            if len(bar_investments) >= 5:
                # Viele Bar-Investments ohne Auszahlungen = verdächtig (Geld wird "gehortet")
                bar_investment_ratio = len(bar_investments) / len(investments)
                return min(0.5, bar_investment_ratio * 0.7)  # Score 0-0.5 für "Geldhortung"
            return 0.0
        
        # 1. Bar-Ratio bei Investments
        bar_investments = [
            t for t in investments 
            if t.payment_method.value == "Bar"
        ]
        bar_investment_ratio = len(bar_investments) / len(investments)
        
        # 2. SEPA/Kreditkarte-Ratio bei Auszahlungen
        electronic_withdrawals = [
            t for t in auszahlungen
            if t.payment_method.value in ["SEPA", "Kreditkarte"]
        ]
        electronic_withdrawal_ratio = len(electronic_withdrawals) / len(auszahlungen)
        
        # 3. Volumen-Analyse: Sind die Beträge ähnlich?
        if bar_investments and electronic_withdrawals:
            bar_in_volume = sum(t.transaction_amount for t in bar_investments)
            electronic_out_volume = sum(t.transaction_amount for t in electronic_withdrawals)
            
            # Verhältnis sollte ähnlich sein (0.7 - 1.3)
            if bar_in_volume > 0:
                volume_ratio = electronic_out_volume / bar_in_volume
                # Perfektes Matching bei ~1.0 ist verdächtig
                volume_match_score = 1.0 - abs(1.0 - volume_ratio) if 0.5 < volume_ratio < 1.5 else 0.0
            else:
                volume_match_score = 0.0
        else:
            volume_match_score = 0.0
        
        # 4. Zeitliche Nähe: Werden Auszahlungen kurz nach Einzahlungen gemacht?
        # Verwende 90-Tage-Fenster für allgemeine Berechnung, aber 30-Tage für Schwellenwert
        if bar_investments and electronic_withdrawals:
            time_proximity_score = 0.0
            for withdrawal in electronic_withdrawals:
                if withdrawal.timestamp:
                    # Finde Bar-Einzahlungen in den letzten 90 Tagen vor dieser Auszahlung
                    recent_bar_investments = [
                        t for t in bar_investments
                        if t.timestamp and 
                        (withdrawal.timestamp - t.timestamp).days <= 90 and
                        (withdrawal.timestamp - t.timestamp).days >= 0
                    ]
                    if recent_bar_investments:
                        time_proximity_score += 1.0
            
            if len(electronic_withdrawals) > 0:
                time_proximity_score /= len(electronic_withdrawals)
        else:
            time_proximity_score = 0.0
        
        # ==========================================
        # ABSOLUTE SCHWELLENWERTE (Primär-Erkennung)
        # ==========================================
        # Wenn bestimmte absolute Kriterien erfüllt sind, ist es verdächtig
        # unabhängig vom gewichteten Score
        
        absolute_layering_indicators = 0
        
        # 1. Mindestens 3 Bar-Investments UND 2 SEPA-Auszahlungen (GELOCKERT: 5/3 -> 3/2)
        if len(bar_investments) >= 3 and len(electronic_withdrawals) >= 2:
            absolute_layering_indicators += 1
        
        # 2. Bar-Investment Ratio >= 50% (GELOCKERT: 70% -> 50%)
        if bar_investment_ratio >= 0.5:
            absolute_layering_indicators += 1
        
        # 3. Electronic Withdrawal Ratio >= 40% (GELOCKERT: 60% -> 40%)
        if electronic_withdrawal_ratio >= 0.4:
            absolute_layering_indicators += 1
        
        # 4. Mindestvolumen >= 5.000€ (GELOCKERT: 10.000€ -> 5.000€)
        if bar_investments and electronic_withdrawals:
            bar_in_volume = sum(t.transaction_amount for t in bar_investments)
            if bar_in_volume >= 5000:
                absolute_layering_indicators += 1
        
        # 5. Zeitliche Nähe: Mindestens 30% der Auszahlungen haben Bar-Investments in den letzten 90 Tagen (GELOCKERT: 50% -> 30%, 30 Tage -> 90 Tage)
        # Für historische Daten: längeres Zeitfenster
        if bar_investments and electronic_withdrawals:
            rapid_time_proximity = 0.0
            for withdrawal in electronic_withdrawals:
                if withdrawal.timestamp:
                    # Prüfe 90-Tage-Fenster (für historische Daten)
                    recent_bar_investments = [
                        t for t in bar_investments
                        if t.timestamp and 
                        (withdrawal.timestamp - t.timestamp).days <= 90 and
                        (withdrawal.timestamp - t.timestamp).days >= 0
                    ]
                    if recent_bar_investments:
                        rapid_time_proximity += 1.0
            
            if len(electronic_withdrawals) > 0:
                rapid_time_proximity /= len(electronic_withdrawals)
            
            if rapid_time_proximity >= 0.3:  # GELOCKERT: 0.5 -> 0.3
                absolute_layering_indicators += 1
        
        # Wenn 2+ absolute Indikatoren erfüllt sind, booste den Score (GELOCKERT: 3 -> 2)
        if absolute_layering_indicators >= 2:
            # Base Score mit absoluten Checks
            base_score = (
                0.35 * bar_investment_ratio +
                0.35 * electronic_withdrawal_ratio +
                0.15 * volume_match_score +
                0.15 * time_proximity_score
            )
            # Boost für absolute Indikatoren
            absolute_boost = min(0.3, absolute_layering_indicators * 0.1)
            layering_score = min(1.0, base_score + absolute_boost)
        else:
            # WICHTIG: Wenn weniger als 3 Indikatoren erfüllt sind, stark reduzieren
            # Dies verhindert False Positives bei normalen Sparern
            base_score = (
                0.35 * bar_investment_ratio +           # Bar-Einzahlungen
                0.35 * electronic_withdrawal_ratio +    # Elektronische Auszahlungen
                0.15 * volume_match_score +             # Volumen passt zusammen
                0.15 * time_proximity_score             # Zeitliche Nähe
            )
            # Reduziere Score drastisch, wenn nicht genug Indikatoren erfüllt sind
            # Nur echte Geldwäscher erfüllen 3+ Indikatoren
            layering_score = base_score * 0.3  # 70% Reduktion
        
        return min(layering_score, 1.0)
    
    def _extract_features(self, transactions: List[Transaction]) -> List[float]:
        """
        Extrahiert Feature-Vektor aus Transaktionen
        
        Returns:
            [avg_amount, frequency, bar_ratio, investment_ratio]
        """
        if not transactions:
            return [0.0, 0.0, 0.0, 0.0]
        
        amounts = [t.transaction_amount for t in transactions]
        avg_amount = np.mean(amounts)
        
        # Frequenz (Transaktionen pro Tag)
        if transactions[0].timestamp:
            txns_with_time = [t for t in transactions if t.timestamp]
            if len(txns_with_time) > 1:
                dates = [t.timestamp.date() for t in txns_with_time]
                date_range = (max(dates) - min(dates)).days + 1
                frequency = len(transactions) / max(date_range, 1)
            else:
                frequency = 0.0
        else:
            frequency = 0.0
        
        # Bar-Ratio
        bar_count = sum(1 for t in transactions if t.payment_method.value == "Bar")
        bar_ratio = bar_count / len(transactions)
        
        # Investment-Ratio
        investment_count = sum(
            1 for t in transactions if t.transaction_type.value == "investment"
        )
        investment_ratio = investment_count / len(transactions)
        
        return [avg_amount, frequency, bar_ratio, investment_ratio]
    
    def analyze(
        self,
        customer_transactions: List[Transaction],
        all_transactions: List[Transaction] = None
    ) -> StatisticalAnalysis:
        """
        Vollständige statistische Analyse
        
        Args:
            customer_transactions: Transaktionen des Kunden
            all_transactions: Alle Transaktionen (für Vergleiche)
            
        Returns:
            StatisticalAnalysis Objekt
        """
        benford_score = self.benford_analysis(customer_transactions)
        velocity_score = self.velocity_analysis(customer_transactions)
        time_anomaly_score = self.time_anomaly_detection(customer_transactions)
        layering_score = self.cash_to_bank_layering_detection(customer_transactions)
        
        if all_transactions:
            clustering_score = self.clustering_analysis(
                customer_transactions,
                all_transactions
            )
        else:
            clustering_score = 0.0
        
        return StatisticalAnalysis(
            benford_score=benford_score,
            velocity_score=velocity_score,
            time_anomaly_score=time_anomaly_score,
            clustering_score=clustering_score,
            layering_score=layering_score
        )

