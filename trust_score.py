"""
Dynamischer Trust Score

Misst die Vorhersagbarkeit und Vertrauenswürdigkeit des Kundenverhaltens:
- Vorhersagbarkeit durch Zeitreihen-Analyse
- Abweichung vom eigenen historischen Muster
- Abweichung von Peer-Gruppe
- Adaptive Response mit Recovery-Mechanismus
"""

import numpy as np
import pandas as pd
from datetime import datetime, timedelta
from typing import List, Dict, Tuple
from models import Transaction, TrustScoreAnalysis
from scipy import stats


class TrustScoreCalculator:
    """
    Berechnet dynamischen Trust Score basierend auf Verhaltensstabilität
    """
    
    def __init__(self, beta: float = 0.7):
        """
        Args:
            beta: Glättungsfaktor für Score-Updates (höher = träger)
        """
        self.beta = beta  # Glättungsfaktor
        self.previous_scores: Dict[str, float] = {}  # Cache für vorherige Scores
    
    def calculate_predictability(
        self,
        transactions: List[Transaction],
        window_days: int = 90
    ) -> float:
        """
        Misst Vorhersagbarkeit des Verhaltens durch Zeitreihen-Stabilität
        
        Verwendet:
        - Variationskoeffizient (CV) der täglichen Beträge
        - Regelmäßigkeit der Transaktionsintervalle
        - Trend-Stabilität
        
        Args:
            transactions: Liste von Transaktionen
            window_days: Betrachtungsfenster
            
        Returns:
            Predictability Score (0-1, höher = vorhersagbarer)
        """
        if not transactions or len(transactions) < 5:
            return 0.5  # Neutral bei zu wenig Daten
        
        # Transaktionen mit Timestamp
        txns = [t for t in transactions if t.timestamp]
        if not txns:
            return 0.5
        
        # Nach Datum sortieren
        txns = sorted(txns, key=lambda t: t.timestamp)
        
        # Tägliche Aggregate
        df = pd.DataFrame([
            {
                'date': t.timestamp.date(),
                'amount': t.transaction_amount
            }
            for t in txns
        ])
        
        daily = df.groupby('date').agg({
            'amount': ['sum', 'count']
        }).reset_index()
        
        daily.columns = ['date', 'amount_sum', 'count']
        
        if len(daily) < 3:
            return 0.5
        
        # 1. Variationskoeffizient der Beträge (niedriger = stabiler)
        cv_amount = daily['amount_sum'].std() / (daily['amount_sum'].mean() + 1e-6)
        cv_score = 1.0 / (1.0 + cv_amount)  # Normalisiert zu 0-1
        
        # 2. Regelmäßigkeit der Intervalle
        daily['date'] = pd.to_datetime(daily['date'])
        intervals = daily['date'].diff().dt.days.dropna()
        
        if len(intervals) > 1:
            cv_intervals = intervals.std() / (intervals.mean() + 1e-6)
            interval_score = 1.0 / (1.0 + cv_intervals)
        else:
            interval_score = 0.5
        
        # 3. Trend-Stabilität (niedrige Autokorrelation = stabil)
        if len(daily) > 10:
            amounts = daily['amount_sum'].values
            # Detrend
            z = np.polyfit(range(len(amounts)), amounts, 1)
            p = np.poly1d(z)
            detrended = amounts - p(range(len(amounts)))
            
            # Varianz des detrendierten Signals
            trend_variance = np.var(detrended)
            original_variance = np.var(amounts)
            
            trend_score = 1.0 - min(trend_variance / (original_variance + 1e-6), 1.0)
        else:
            trend_score = 0.5
        
        # Kombiniere Scores
        predictability = (cv_score * 0.4 + interval_score * 0.3 + trend_score * 0.3)
        
        return max(0.0, min(1.0, predictability))
    
    def calculate_self_deviation(
        self,
        recent_transactions: List[Transaction],
        historical_transactions: List[Transaction]
    ) -> float:
        """
        Misst Abweichung vom eigenen historischen Muster
        
        Vergleicht:
        - Durchschnittliche Transaktionshöhe
        - Transaktionsfrequenz
        - Verteilung der Zahlungsmethoden
        
        Args:
            recent_transactions: Aktuelle Transaktionen (z.B. 30 Tage)
            historical_transactions: Historische Transaktionen (z.B. 365 Tage)
            
        Returns:
            Deviation Score (0-1, höher = stärkere Abweichung)
        """
        if not historical_transactions or not recent_transactions:
            return 0.0
        
        # Historische Statistiken
        hist_amounts = [t.transaction_amount for t in historical_transactions]
        hist_mean = np.mean(hist_amounts)
        hist_std = np.std(hist_amounts)
        
        hist_payment_methods = [t.payment_method.value for t in historical_transactions]
        hist_method_dist = pd.Series(hist_payment_methods).value_counts(normalize=True)
        
        # Aktuelle Statistiken
        recent_amounts = [t.transaction_amount for t in recent_transactions]
        recent_mean = np.mean(recent_amounts)
        
        recent_payment_methods = [t.payment_method.value for t in recent_transactions]
        recent_method_dist = pd.Series(recent_payment_methods).value_counts(normalize=True)
        
        # 1. Abweichung der durchschnittlichen Beträge (Z-Score)
        # ANPASSUNG: Stärkere Bestrafung von Abweichungen
        if hist_std > 0:
            amount_z = abs((recent_mean - hist_mean) / hist_std)
        else:
            amount_z = 0.0
        
        # Stärkere Normalisierung: Z-Score > 2.0 wird als sehr verdächtig betrachtet
        amount_deviation = min(amount_z / 2.0, 1.0)  # Reduziert von 3.0 auf 2.0 (stärkere Bestrafung)
        
        # 2. Abweichung der Zahlungsmethoden-Verteilung (KL-Divergenz)
        # Stelle sicher, dass beide Verteilungen die gleichen Kategorien haben
        all_methods = set(hist_method_dist.index) | set(recent_method_dist.index)
        
        hist_probs = [hist_method_dist.get(m, 0.01) for m in all_methods]
        recent_probs = [recent_method_dist.get(m, 0.01) for m in all_methods]
        
        # Normalisiere
        hist_probs = np.array(hist_probs) / sum(hist_probs)
        recent_probs = np.array(recent_probs) / sum(recent_probs)
        
        # KL-Divergenz
        kl_div = np.sum(recent_probs * np.log((recent_probs + 1e-10) / (hist_probs + 1e-10)))
        # ANPASSUNG: Stärkere Bestrafung von Zahlungsmethoden-Abweichungen
        method_deviation = min(kl_div / 1.5, 1.0)  # Reduziert von 2.0 auf 1.5 (stärkere Bestrafung)
        
        # Kombiniere
        deviation = (amount_deviation * 0.6 + method_deviation * 0.4)
        
        return max(0.0, min(1.0, deviation))
    
    def calculate_peer_deviation(
        self,
        customer_transactions: List[Transaction],
        peer_transactions: List[Transaction]
    ) -> float:
        """
        Misst Abweichung von der Peer-Gruppe
        
        Vergleicht Kunde mit ähnlichen Kunden (z.B. gleiches Segment, ähnliche Größe)
        
        Args:
            customer_transactions: Transaktionen des Kunden
            peer_transactions: Transaktionen der Peer-Gruppe
            
        Returns:
            Peer Deviation Score (0-1, höher = stärkere Abweichung)
        """
        if not peer_transactions or not customer_transactions:
            return 0.0
        
        # Peer-Statistiken
        peer_amounts = [t.transaction_amount for t in peer_transactions]
        peer_mean = np.mean(peer_amounts)
        peer_std = np.std(peer_amounts)
        
        # Kunden-Statistiken
        customer_amounts = [t.transaction_amount for t in customer_transactions]
        customer_mean = np.mean(customer_amounts)
        
        # Z-Score gegen Peer-Gruppe
        # ANPASSUNG: Stärkere Bestrafung von Peer-Abweichungen
        if peer_std > 0:
            peer_z = abs((customer_mean - peer_mean) / peer_std)
        else:
            peer_z = 0.0
        
        # Stärkere Normalisierung: Z-Score > 2.0 wird als sehr verdächtig betrachtet
        peer_deviation = min(peer_z / 2.0, 1.0)  # Reduziert von 3.0 auf 2.0 (stärkere Bestrafung)
        
        return max(0.0, min(1.0, peer_deviation))
    
    def calculate_trust_score(
        self,
        predictability: float,
        self_deviation: float,
        peer_deviation: float,
        customer_id: str = None
    ) -> float:
        """
        Berechnet den finalen Trust Score
        
        T(t) = β × T(t-1) + (1-β) × T_neu
        
        T_neu basiert auf:
        - Hohe Vorhersagbarkeit → hoher Score
        - Niedrige Abweichungen → hoher Score
        
        Args:
            predictability: Vorhersagbarkeits-Score (0-1)
            self_deviation: Selbst-Abweichung (0-1)
            peer_deviation: Peer-Abweichung (0-1)
            customer_id: Kunden-ID für Score-History
            
        Returns:
            Trust Score (0-1, höher = vertrauenswürdiger)
        """
        # Berechne neuen Score
        # ANPASSUNG: Stärkere Bestrafung von Abweichungen für bessere Korrelation mit Risk_Level
        # Verdächtige Kunden (YELLOW/ORANGE/RED) sollten niedrigere Trust_Scores haben
        
        # Nicht-lineare Skalierung der Abweichungen (stärkere Bestrafung)
        # Abweichungen werden quadratisch bestraft, um verdächtiges Verhalten stärker zu erkennen
        self_deviation_penalty = self_deviation ** 2.0  # Stärkere Bestrafung (^2.0 statt ^1.5)
        
        # WICHTIG: Peer Deviation = 0.0 bedeutet oft "keine Peers" oder "keine Abweichung"
        # Wenn keine Peers vorhanden sind, sollte Peer Deviation neutral sein (nicht 1.0!)
        if peer_deviation > 0.0:
            peer_deviation_penalty = peer_deviation ** 2.0
            peer_component = 0.25 * (1.0 - peer_deviation_penalty)
        else:
            # Keine Peer-Abweichung = neutral (nicht automatisch vertrauenswürdig!)
            peer_component = 0.0  # Ignoriere Peer-Deviation wenn 0.0
        
        # Neue Gewichtung: Abweichungen stärker gewichten, Predictability weniger
        # Wenn Peer-Deviation = 0.0, erhöhe Self-Deviation Gewichtung
        if peer_deviation > 0.0:
            t_new = (
                0.25 * predictability +                      # 25%
                0.50 * (1.0 - self_deviation_penalty) +     # 50%
                0.25 * (1.0 - peer_deviation_penalty)        # 25%
            )
        else:
            # Keine Peer-Deviation: Self-Deviation stärker gewichten
            t_new = (
                0.20 * predictability +                      # 20% (reduziert)
                0.80 * (1.0 - self_deviation_penalty)        # 80% (erhöht!)
            )
        
        # Glättung mit vorherigem Score
        # ANPASSUNG: Stärkere Reaktion auf verdächtiges Verhalten
        # Bei hohen Abweichungen weniger glätten, damit verdächtiges Verhalten schneller erkannt wird
        if customer_id and customer_id in self.previous_scores:
            t_previous = self.previous_scores[customer_id]
            
            # Dynamische Glättung basierend auf Abweichungen (nicht nur T_neu)
            # Hohe Abweichungen = verdächtig = schneller reagieren
            max_deviation = max(self_deviation, peer_deviation)
            
            if max_deviation > 0.7 or t_new < 0.3:
                # Sehr verdächtig: sehr schnelle Reaktion
                beta_dynamic = 0.2  # Sehr wenig Glättung
            elif max_deviation > 0.5 or t_new < 0.4:
                # Verdächtig: schnelle Reaktion
                beta_dynamic = 0.3  # Wenig Glättung
            elif max_deviation > 0.3 or t_new < 0.6:
                # Leicht verdächtig: moderate Reaktion
                beta_dynamic = 0.5  # Moderate Glättung
            else:
                # Normal: normale Glättung
                beta_dynamic = self.beta  # Normale Glättung bei vertrauenswürdigem Verhalten
            
            t_current = beta_dynamic * t_previous + (1 - beta_dynamic) * t_new
        else:
            t_current = t_new
        
        # Speichere für nächstes Mal
        if customer_id:
            self.previous_scores[customer_id] = t_current
        
        return max(0.0, min(1.0, t_current))
    
    def analyze(
        self,
        customer_id: str,
        recent_transactions: List[Transaction],
        historical_transactions: List[Transaction],
        peer_transactions: List[Transaction] = None
    ) -> TrustScoreAnalysis:
        """
        Vollständige Trust Score Analyse
        
        Args:
            customer_id: Kunden-ID
            recent_transactions: Aktuelle Transaktionen
            historical_transactions: Historische Transaktionen
            peer_transactions: Peer-Transaktionen (optional)
            
        Returns:
            TrustScoreAnalysis Objekt
        """
        # Berechne Komponenten
        predictability = self.calculate_predictability(
            historical_transactions + recent_transactions
        )
        
        self_deviation = self.calculate_self_deviation(
            recent_transactions,
            historical_transactions
        )
        
        if peer_transactions:
            peer_deviation = self.calculate_peer_deviation(
                recent_transactions,
                peer_transactions
            )
        else:
            peer_deviation = 0.0
        
        # Finaler Score
        current_score = self.calculate_trust_score(
            predictability,
            self_deviation,
            peer_deviation,
            customer_id
        )
        
        # ==========================================
        # ABSOLUTE SCHWELLENWERTE (ohne historische Daten)
        # ==========================================
        # Unabhängig von historischen Daten können wir absolute Kriterien prüfen:
        
        # 1. Sehr niedrige Vorhersagbarkeit ist immer verdächtig
        #    (chaotisches Verhalten ohne Muster)
        absolute_low_trust = predictability < 0.2
        
        # 2. Extreme Selbst-Abweichung (wenn historische Daten vorhanden)
        #    aber mit absolutem Schwellenwert
        if self_deviation > 0.8:  # Extrem anders als vorher
            absolute_low_trust = True
        
        # 3. Kombinierter absoluter Trust Score
        #    Sehr niedriger Score (<0.3) ist absolut verdächtig
        if current_score < 0.3:
            absolute_low_trust = True
        
        # Hinweis: absolute_low_trust kann im Analyzer verwendet werden
        # für zusätzliche Flag-Generierung
        
        return TrustScoreAnalysis(
            current_score=current_score,
            predictability=predictability,
            self_deviation=self_deviation,
            peer_deviation=peer_deviation
        )

