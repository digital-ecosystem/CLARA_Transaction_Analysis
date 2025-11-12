"""
Shannon-Entropie Komplexitätsmessung

Erkennt ungewöhnliche Verteilungen und Verschleierungsversuche durch:
- Mehrdimensionale Entropie-Analyse
- Betragsprofil (Binning)
- Zahlungsmethoden-Verteilung
- Transaktionsarten-Verteilung
- Zeitmuster
"""

import numpy as np
import pandas as pd
from datetime import datetime, timedelta
from typing import List, Dict, Tuple
from collections import Counter
from models import Transaction, EntropyAnalysis


class EntropyDetector:
    """
    Misst Komplexität und Merkwürdigkeit des Transaktionsverhaltens
    mittels Shannon-Entropie
    """
    
    def __init__(
        self,
        amount_bins: List[float] = None,
        weights: Dict[str, float] = None
    ):
        """
        Args:
            amount_bins: Betrags-Bins für Diskretisierung
            weights: Gewichte für verschiedene Entropie-Dimensionen
        """
        # Standard-Bins (in EUR)
        self.amount_bins = amount_bins or [0, 500, 2000, 10000, float('inf')]
        
        # Gewichte für aggregierte Entropie
        self.weights = weights or {
            'amount': 0.25,
            'payment_method': 0.30,
            'transaction_type': 0.20,
            'time': 0.25
        }
    
    def calculate_shannon_entropy(self, probabilities: List[float]) -> float:
        """
        Berechnet Shannon-Entropie
        
        H = -Σ p_i log(p_i)
        
        Args:
            probabilities: Liste von Wahrscheinlichkeiten (müssen zu 1 summieren)
            
        Returns:
            Entropie-Wert
        """
        # Filtere Nullen (log(0) ist undefiniert)
        p = np.array([p for p in probabilities if p > 0])
        
        if len(p) == 0:
            return 0.0
        
        # Shannon-Entropie
        entropy = -np.sum(p * np.log2(p))
        
        return entropy
    
    def calculate_amount_entropy(self, transactions: List[Transaction]) -> float:
        """
        Entropie des Betragsprofils
        
        Diskretisiert Beträge in Bins und berechnet Verteilungs-Entropie
        
        Args:
            transactions: Liste von Transaktionen
            
        Returns:
            Entropie-Wert
        """
        if not transactions:
            return 0.0
        
        # Beträge in Bins einordnen
        amounts = [t.transaction_amount for t in transactions]
        bin_counts = np.histogram(amounts, bins=self.amount_bins)[0]
        
        # Wahrscheinlichkeiten
        total = sum(bin_counts)
        if total == 0:
            return 0.0
        
        probabilities = bin_counts / total
        
        return self.calculate_shannon_entropy(probabilities)
    
    def calculate_payment_method_entropy(
        self,
        transactions: List[Transaction]
    ) -> float:
        """
        Entropie der Zahlungsmethoden-Verteilung
        
        Args:
            transactions: Liste von Transaktionen
            
        Returns:
            Entropie-Wert
        """
        if not transactions:
            return 0.0
        
        # Zähle Zahlungsmethoden
        methods = [t.payment_method.value for t in transactions]
        counts = Counter(methods)
        
        # Wahrscheinlichkeiten
        total = len(methods)
        probabilities = [count / total for count in counts.values()]
        
        return self.calculate_shannon_entropy(probabilities)
    
    def calculate_transaction_type_entropy(
        self,
        transactions: List[Transaction]
    ) -> float:
        """
        Entropie der Transaktionsarten-Verteilung
        
        Args:
            transactions: Liste von Transaktionen
            
        Returns:
            Entropie-Wert
        """
        if not transactions:
            return 0.0
        
        # Zähle Transaktionstypen
        types = [t.transaction_type.value for t in transactions]
        counts = Counter(types)
        
        # Wahrscheinlichkeiten
        total = len(types)
        probabilities = [count / total for count in counts.values()]
        
        return self.calculate_shannon_entropy(probabilities)
    
    def calculate_time_entropy(self, transactions: List[Transaction]) -> float:
        """
        Entropie der zeitlichen Verteilung
        
        Analysiert Verteilung über:
        - Wochentage
        - Tageszeiten (in 6 Blöcken: 0-4, 4-8, 8-12, 12-16, 16-20, 20-24)
        
        Args:
            transactions: Liste von Transaktionen
            
        Returns:
            Entropie-Wert (Durchschnitt aus Wochentag- und Tageszeitentropie)
        """
        if not transactions:
            return 0.0
        
        # Filtere Transaktionen mit Timestamp
        txns_with_time = [t for t in transactions if t.timestamp]
        
        if not txns_with_time:
            return 0.0
        
        # Wochentag-Entropie
        weekdays = [t.timestamp.weekday() for t in txns_with_time]
        weekday_counts = Counter(weekdays)
        weekday_probs = [count / len(weekdays) for count in weekday_counts.values()]
        weekday_entropy = self.calculate_shannon_entropy(weekday_probs)
        
        # Tageszeit-Entropie (4-Stunden-Blöcke)
        hour_blocks = [t.timestamp.hour // 4 for t in txns_with_time]
        hour_counts = Counter(hour_blocks)
        hour_probs = [count / len(hour_blocks) for count in hour_counts.values()]
        hour_entropy = self.calculate_shannon_entropy(hour_probs)
        
        # Durchschnitt
        return (weekday_entropy + hour_entropy) / 2.0
    
    def calculate_aggregate_entropy(
        self,
        entropy_amount: float,
        entropy_payment: float,
        entropy_type: float,
        entropy_time: float
    ) -> float:
        """
        Berechnet gewichtete aggregierte Entropie
        
        H_agg = w_a * H_amount + w_p * H_payment + w_t * H_type + w_time * H_time
        
        Args:
            entropy_amount: Betrags-Entropie
            entropy_payment: Zahlungsmethoden-Entropie
            entropy_type: Transaktionstyp-Entropie
            entropy_time: Zeit-Entropie
            
        Returns:
            Aggregierte Entropie
        """
        h_agg = (
            self.weights['amount'] * entropy_amount +
            self.weights['payment_method'] * entropy_payment +
            self.weights['transaction_type'] * entropy_type +
            self.weights['time'] * entropy_time
        )
        
        return h_agg
    
    def calculate_z_score(
        self,
        current_entropy: float,
        historical_entropies: List[float]
    ) -> float:
        """
        Berechnet Z-Score der Entropie gegen historische Baseline
        
        z_H = (H_agg - μ_H) / σ_H
        
        Beachte: CLARA betrachtet |z_H| (absolute Abweichung),
        da sowohl sehr hohe als auch sehr niedrige Entropie verdächtig sein kann.
        
        Args:
            current_entropy: Aktuelle Entropie
            historical_entropies: Historische Entropie-Werte
            
        Returns:
            Z-Score
        """
        if not historical_entropies or len(historical_entropies) < 2:
            return 0.0
        
        mu = np.mean(historical_entropies)
        sigma = np.std(historical_entropies)
        
        # Verhindere Division durch Null
        if sigma < 0.01:
            sigma = 0.01
        
        z_score = (current_entropy - mu) / sigma
        
        return z_score
    
    def analyze(
        self,
        recent_transactions: List[Transaction],
        historical_transactions: List[Transaction] = None
    ) -> EntropyAnalysis:
        """
        Vollständige Entropie-Analyse
        
        Args:
            recent_transactions: Aktuelle Transaktionen
            historical_transactions: Historische Transaktionen für Baseline
            
        Returns:
            EntropyAnalysis Objekt
        """
        # Berechne einzelne Entropien
        entropy_amount = self.calculate_amount_entropy(recent_transactions)
        entropy_payment = self.calculate_payment_method_entropy(recent_transactions)
        entropy_type = self.calculate_transaction_type_entropy(recent_transactions)
        entropy_time = self.calculate_time_entropy(recent_transactions)
        
        # Aggregierte Entropie
        entropy_agg = self.calculate_aggregate_entropy(
            entropy_amount,
            entropy_payment,
            entropy_type,
            entropy_time
        )
        
        # ==========================================
        # ABSOLUTE SCHWELLENWERTE (Primär-Erkennung)
        # ==========================================
        # Extrem hohe oder niedrige Entropie ist verdächtig (unabhängig von Historie)
        
        # Absolute Schwellenwerte für aggregierte Entropie:
        # - Sehr niedrig (< 0.3): Kanalisation (alles auf einen Punkt konzentriert)
        # - Sehr hoch (> 2.0): Verschleierung (zu gleichmäßig verteilt)
        absolute_suspicious = False
        
        if entropy_agg < 0.3:  # Extreme Konzentration
            absolute_suspicious = True
        elif entropy_agg > 2.0:  # Extreme Streuung
            absolute_suspicious = True
        
        # Zusätzlich: Payment Method Entropie sehr niedrig (nur eine Methode)
        if entropy_payment < 0.1 and len(recent_transactions) > 10:
            # Nur eine Zahlungsmethode bei vielen Transaktionen
            absolute_suspicious = True
        
        # NEU: Hohe Betrags-Diversität (viele unterschiedliche Beträge)
        # Prüfe Anzahl unique Beträge relativ zur Gesamtzahl
        if len(recent_transactions) >= 10:
            amounts = [t.transaction_amount for t in recent_transactions]
            unique_amounts = len(set(amounts))
            unique_ratio = unique_amounts / len(recent_transactions)
            
            # Wenn >= 80% der Beträge unique sind, ist es verdächtig (Verschleierung)
            if unique_ratio >= 0.8:
                absolute_suspicious = True
            
            # Oder wenn Entropy Amount >= 1.0 bei >= 10 Transaktionen (gelockert von 2.0 auf 1.0)
            if entropy_amount >= 1.0:
                absolute_suspicious = True
        
        # ==========================================
        # RELATIVE SCHWELLENWERTE (Sekundär-Erkennung)
        # ==========================================
        # Z-Score berechnen (wenn historische Daten vorhanden)
        z_score = 0.0
        relative_suspicious = False
        
        if historical_transactions and len(historical_transactions) > 0:
            # Berechne historische Entropien (rollierende Fenster)
            historical_entropies = self._calculate_historical_entropies(
                historical_transactions
            )
            z_score = self.calculate_z_score(entropy_agg, historical_entropies)
            
            # Relative Schwellenwerte (nur bei Änderungen)
            # |z_H| >= 2.5 → Hinweis (erhöht von 2.0)
            # |z_H| >= 3.5 → stark auffällig (erhöht von 3.0)
            relative_suspicious = abs(z_score) >= 2.5
        
        # Kombiniere absolute und relative Erkennung
        is_complex = absolute_suspicious or relative_suspicious
        
        return EntropyAnalysis(
            entropy_amount=entropy_amount,
            entropy_payment_method=entropy_payment,
            entropy_transaction_type=entropy_type,
            entropy_time=entropy_time,
            entropy_aggregate=entropy_agg,
            z_score=z_score,
            is_complex=is_complex
        )
    
    def _calculate_historical_entropies(
        self,
        historical_transactions: List[Transaction],
        window_size: int = 30
    ) -> List[float]:
        """
        Berechnet rollierende historische Entropien
        
        Args:
            historical_transactions: Historische Transaktionen
            window_size: Fenstergröße in Tagen
            
        Returns:
            Liste von Entropie-Werten
        """
        if not historical_transactions:
            return []
        
        # Sortiere nach Datum
        txns = sorted(
            [t for t in historical_transactions if t.timestamp],
            key=lambda t: t.timestamp
        )
        
        if not txns:
            return []
        
        entropies = []
        
        # Finde ersten und letzten Zeitpunkt
        min_time = txns[0].timestamp
        max_time = txns[-1].timestamp
        
        # Erstelle rollierende Fenster (alle 7 Tage ein neues Fenster)
        current_time = min_time + timedelta(days=window_size)
        
        while current_time <= max_time:
            window_start = current_time - timedelta(days=window_size)
            window_end = current_time
            
            window_txns = [
                t for t in txns
                if window_start <= t.timestamp < window_end
            ]
            
            if len(window_txns) > 5:  # Mindestanzahl für sinnvolle Entropie
                # Berechne Entropien
                e_amount = self.calculate_amount_entropy(window_txns)
                e_payment = self.calculate_payment_method_entropy(window_txns)
                e_type = self.calculate_transaction_type_entropy(window_txns)
                e_time = self.calculate_time_entropy(window_txns)
                
                e_agg = self.calculate_aggregate_entropy(
                    e_amount, e_payment, e_type, e_time
                )
                
                entropies.append(e_agg)
            
            # Nächstes Fenster (7 Tage später)
            current_time += timedelta(days=7)
        
        return entropies

