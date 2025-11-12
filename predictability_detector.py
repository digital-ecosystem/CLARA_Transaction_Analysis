"""
Predictability-Analyse (Verhaltensstabilität)

Bewertet die zeitliche und strukturelle Verlässlichkeit des Transaktionsverhaltens.
Misst, wie beständig das Verhalten über längere Zeiträume bleibt und in welchem Maß
es planbar oder vorhersehbar ist.

Analysebereiche:
1. Zeitliche Stabilität - Konstanz der zeitlichen Abstände zwischen Transaktionen
2. Betrags-Konsistenz - Gleichbleibende Betragsmuster über Zeit
3. Kanal-Kontinuität - Wiederkehrende Nutzung etablierter Kanäle
4. Ziel-Stabilität - Konstanz der Empfänger und Gegenparteien (nicht verfügbar in aktuellen Daten)
"""

import numpy as np
from datetime import datetime, timedelta
from typing import List, Optional, Dict
from collections import Counter
from models import Transaction, PredictabilityAnalysis


class PredictabilityDetector:
    """
    Misst die Vorhersagbarkeit und Stabilität des Transaktionsverhaltens
    """
    
    def __init__(self):
        """Initialisiert den Predictability Detector"""
        pass
    
    def calculate_temporal_stability(
        self,
        recent_transactions: List[Transaction],
        historical_transactions: List[Transaction]
    ) -> float:
        """
        Berechnet zeitliche Stabilität (Konstanz der zeitlichen Abstände)
        
        Args:
            recent_transactions: Aktuelle Transaktionen (30 Tage)
            historical_transactions: Historische Transaktionen (Baseline)
            
        Returns:
            Stabilitäts-Score (0.0-1.0, höher = stabiler)
        """
        if not recent_transactions or len(recent_transactions) < 2:
            return 0.5  # Neutral wenn zu wenige Daten
        
        # Sortiere nach Timestamp
        recent_sorted = sorted(
            [t for t in recent_transactions if t.timestamp],
            key=lambda t: t.timestamp
        )
        
        if len(recent_sorted) < 2:
            return 0.5
        
        # Berechne Intervalle zwischen Transaktionen
        intervals = []
        for i in range(1, len(recent_sorted)):
            delta = recent_sorted[i].timestamp - recent_sorted[i-1].timestamp
            intervals.append(delta.total_seconds() / 86400.0)  # In Tagen
        
        if not intervals:
            return 0.5
        
        # Berechne Varianz der Intervalle (niedrige Varianz = hohe Stabilität)
        intervals_array = np.array(intervals)
        mean_interval = np.mean(intervals_array)
        
        if mean_interval == 0:
            return 0.0  # Alle Transaktionen gleichzeitig = instabil
        
        # Coefficient of Variation (CV) - niedrige CV = hohe Stabilität
        cv = np.std(intervals_array) / mean_interval if mean_interval > 0 else 1.0
        
        # Konvertiere CV zu Stabilitäts-Score (0-1)
        # CV < 0.3 = sehr stabil (Score > 0.8)
        # CV > 1.0 = instabil (Score < 0.3)
        if cv < 0.3:
            stability = 0.8 + 0.2 * (0.3 - cv) / 0.3  # 0.8-1.0
        elif cv < 0.6:
            stability = 0.5 + 0.3 * (0.6 - cv) / 0.3  # 0.5-0.8
        elif cv < 1.0:
            stability = 0.3 + 0.2 * (1.0 - cv) / 0.4  # 0.3-0.5
        else:
            stability = max(0.0, 0.3 - 0.3 * (cv - 1.0) / 2.0)  # 0.0-0.3
        
        return stability
    
    def calculate_amount_consistency(
        self,
        recent_transactions: List[Transaction],
        historical_transactions: List[Transaction]
    ) -> float:
        """
        Berechnet Betrags-Konsistenz (Gleichbleibende Betragsmuster)
        
        Args:
            recent_transactions: Aktuelle Transaktionen
            historical_transactions: Historische Transaktionen (Baseline)
            
        Returns:
            Konsistenz-Score (0.0-1.0, höher = konsistenter)
        """
        if not recent_transactions:
            return 0.5
        
        recent_amounts = [t.transaction_amount for t in recent_transactions]
        
        if len(recent_amounts) < 2:
            return 0.5
        
        # Berechne Varianz der Beträge
        amounts_array = np.array(recent_amounts)
        mean_amount = np.mean(amounts_array)
        
        if mean_amount == 0:
            return 0.0
        
        # Coefficient of Variation (CV)
        cv = np.std(amounts_array) / mean_amount if mean_amount > 0 else 1.0
        
        # Konvertiere CV zu Konsistenz-Score
        # Niedrige CV = hohe Konsistenz
        if cv < 0.2:
            consistency = 0.9 + 0.1 * (0.2 - cv) / 0.2  # 0.9-1.0
        elif cv < 0.5:
            consistency = 0.7 + 0.2 * (0.5 - cv) / 0.3  # 0.7-0.9
        elif cv < 1.0:
            consistency = 0.5 + 0.2 * (1.0 - cv) / 0.5  # 0.5-0.7
        elif cv < 2.0:
            consistency = 0.3 + 0.2 * (2.0 - cv) / 1.0  # 0.3-0.5
        else:
            consistency = max(0.0, 0.3 - 0.3 * (cv - 2.0) / 3.0)  # 0.0-0.3
        
        # Vergleiche mit historischer Baseline (falls verfügbar)
        if historical_transactions and len(historical_transactions) >= 5:
            historical_amounts = [t.transaction_amount for t in historical_transactions]
            hist_mean = np.mean(historical_amounts)
            hist_cv = np.std(historical_amounts) / hist_mean if hist_mean > 0 else 1.0
            
            # Wenn aktuelle CV deutlich höher als historische, reduziere Score
            if cv > hist_cv * 1.5:
                consistency *= 0.7  # Reduktion bei Abweichung von Baseline
        
        return consistency
    
    def calculate_channel_continuity(
        self,
        recent_transactions: List[Transaction],
        historical_transactions: List[Transaction]
    ) -> float:
        """
        Berechnet Kanal-Kontinuität (Wiederkehrende Nutzung etablierter Kanäle)
        
        Args:
            recent_transactions: Aktuelle Transaktionen
            historical_transactions: Historische Transaktionen (Baseline)
            
        Returns:
            Kontinuitäts-Score (0.0-1.0, höher = kontinuierlicher)
        """
        if not recent_transactions:
            return 0.5
        
        # Zähle Zahlungsmethoden in aktuellen Transaktionen
        recent_methods = Counter([t.payment_method.value for t in recent_transactions])
        total_recent = len(recent_transactions)
        
        if total_recent == 0:
            return 0.5
        
        # Dominante Zahlungsmethode (Anteil)
        dominant_ratio = max(recent_methods.values()) / total_recent
        
        # Hohe Kontinuität wenn eine Methode dominiert (>70%)
        if dominant_ratio >= 0.9:
            continuity = 1.0
        elif dominant_ratio >= 0.7:
            continuity = 0.8 + 0.2 * (dominant_ratio - 0.7) / 0.2  # 0.8-1.0
        elif dominant_ratio >= 0.5:
            continuity = 0.6 + 0.2 * (dominant_ratio - 0.5) / 0.2  # 0.6-0.8
        else:
            # Viele verschiedene Methoden = niedrige Kontinuität
            num_methods = len(recent_methods)
            if num_methods == 1:
                continuity = 0.6
            elif num_methods == 2:
                continuity = 0.4
            else:
                continuity = max(0.0, 0.4 - 0.1 * (num_methods - 2))
        
        # Vergleiche mit historischer Baseline
        if historical_transactions and len(historical_transactions) >= 5:
            historical_methods = Counter([t.payment_method.value for t in historical_transactions])
            total_historical = len(historical_transactions)
            
            # Finde dominante historische Methode
            if total_historical > 0:
                hist_dominant = max(historical_methods.values()) / total_historical
                hist_dominant_method = max(historical_methods.items(), key=lambda x: x[1])[0]
                
                # Wenn aktuelle dominante Methode = historische dominante Methode
                if recent_methods.get(hist_dominant_method, 0) / total_recent >= 0.5:
                    continuity = min(1.0, continuity + 0.2)  # Bonus für Kontinuität
                elif dominant_ratio < hist_dominant * 0.5:
                    continuity *= 0.7  # Reduktion bei Wechsel
        
        return continuity
    
    def calculate_overall_predictability(
        self,
        temporal_stability: float,
        amount_consistency: float,
        channel_continuity: float
    ) -> float:
        """
        Berechnet Gesamt-Predictability aus allen Dimensionen
        
        Args:
            temporal_stability: Zeitliche Stabilität (0-1)
            amount_consistency: Betrags-Konsistenz (0-1)
            channel_continuity: Kanal-Kontinuität (0-1)
            
        Returns:
            Gesamt-Predictability (0.0-1.0, höher = vorhersehbarer)
        """
        # Gewichtete Kombination
        # Zeitliche Stabilität ist am wichtigsten (40%)
        # Betrags-Konsistenz (35%)
        # Kanal-Kontinuität (25%)
        predictability = (
            0.40 * temporal_stability +
            0.35 * amount_consistency +
            0.25 * channel_continuity
        )
        
        return predictability
    
    def analyze(
        self,
        recent_transactions: List[Transaction],
        historical_transactions: List[Transaction]
    ) -> PredictabilityAnalysis:
        """
        Vollständige Predictability-Analyse
        
        Args:
            recent_transactions: Aktuelle Transaktionen (30 Tage)
            historical_transactions: Historische Transaktionen (Baseline)
            
        Returns:
            PredictabilityAnalysis Objekt
        """
        # 1. Zeitliche Stabilität
        temporal_stability = self.calculate_temporal_stability(
            recent_transactions,
            historical_transactions
        )
        
        # 2. Betrags-Konsistenz
        amount_consistency = self.calculate_amount_consistency(
            recent_transactions,
            historical_transactions
        )
        
        # 3. Kanal-Kontinuität
        channel_continuity = self.calculate_channel_continuity(
            recent_transactions,
            historical_transactions
        )
        
        # 4. Gesamt-Predictability
        overall_predictability = self.calculate_overall_predictability(
            temporal_stability,
            amount_consistency,
            channel_continuity
        )
        
        # 5. Z-Score (Abweichung von historischer Baseline)
        z_score = 0.0
        if historical_transactions and len(historical_transactions) >= 10:
            # Berechne historische Predictability als Baseline
            hist_temporal = self.calculate_temporal_stability(
                historical_transactions[-30:] if len(historical_transactions) >= 30 else historical_transactions,
                historical_transactions[:-30] if len(historical_transactions) >= 30 else []
            )
            hist_amount = self.calculate_amount_consistency(
                historical_transactions[-30:] if len(historical_transactions) >= 30 else historical_transactions,
                historical_transactions[:-30] if len(historical_transactions) >= 30 else []
            )
            hist_channel = self.calculate_channel_continuity(
                historical_transactions[-30:] if len(historical_transactions) >= 30 else historical_transactions,
                historical_transactions[:-30] if len(historical_transactions) >= 30 else []
            )
            hist_predictability = self.calculate_overall_predictability(
                hist_temporal,
                hist_amount,
                hist_channel
            )
            
            # Berechne Z-Score (wie stark weicht aktuelle Predictability ab?)
            # Annahme: Standardabweichung von Predictability ist ~0.15
            if hist_predictability > 0:
                deviation = overall_predictability - hist_predictability
                std_dev = 0.15  # Geschätzte Standardabweichung
                z_score = deviation / std_dev if std_dev > 0 else 0.0
            else:
                z_score = 0.0
        
        return PredictabilityAnalysis(
            temporal_stability=temporal_stability,
            amount_consistency=amount_consistency,
            channel_continuity=channel_continuity,
            overall_predictability=overall_predictability,
            z_score=z_score,
            is_stable=overall_predictability >= 0.7  # Stabilitätsschwelle
        )

