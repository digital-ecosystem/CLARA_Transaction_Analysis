"""
Hauptanalyse-Engine für CLARA Transaction Analysis System

Koordiniert alle Analyse-Komponenten:
- Weight Detector (Anti-Smurfing)
- Entropy Detector (Komplexität)
- Trust Score Calculator
- Statistical Analyzer

Berechnet finalen Suspicion Score und Risiko-Level
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import List, Dict, Tuple, Optional
from models import (
    Transaction, CustomerRiskProfile, RiskLevel, CustomerInfo,
    WeightAnalysis, EntropyAnalysis, PredictabilityAnalysis, TrustScoreAnalysis, StatisticalAnalysis,
    ModulePoints
)
from weight_detector import WeightDetector
from entropy_detector import EntropyDetector
from predictability_detector import PredictabilityDetector
from trust_score import TrustScoreCalculator
from statistical_methods import StatisticalAnalyzer


class TransactionAnalyzer:
    """
    Hauptanalyse-Engine - koordiniert alle Detektoren
    """
    
    def __init__(
        self,
        alpha: float = 0.6,
        beta: float = 0.4,
        historical_days: int = 365,
        use_tp_sp_system: bool = True
    ):
        """
        Args:
            alpha: Gewicht für Weight-Z-Score im Suspicion Score
            beta: Gewicht für Entropy-Z-Score im Suspicion Score
            historical_days: Anzahl Tage für historische Baseline
            use_tp_sp_system: Verwende neues TP/SP-System (True) oder alte Berechnung (False)
        """
        self.alpha = alpha
        self.beta = beta
        self.historical_days = historical_days
        self.use_tp_sp_system = use_tp_sp_system
        
        # Initialisiere Detektoren
        self.weight_detector = WeightDetector()
        self.entropy_detector = EntropyDetector()
        self.predictability_detector = PredictabilityDetector()
        self.trust_calculator = TrustScoreCalculator()
        self.statistical_analyzer = StatisticalAnalyzer()
        
        # WICHTIG: Cache zurücksetzen bei jeder neuen Analyse-Session
        # Damit Trust_Score-Anpassungen sofort wirksam werden
        self.trust_calculator.previous_scores = {}
        
        # In-Memory Datenspeicher (in Produktion: Datenbank)
        self.transaction_history: Dict[str, List[Transaction]] = {}
        self.customer_info: Dict[str, CustomerInfo] = {}  # CustomerInfo Cache
    
    def add_transactions(self, transactions: List[Transaction]):
        """
        Fügt Transaktionen zum History-Store hinzu
        
        Args:
            transactions: Liste von Transaktionen
        """
        for txn in transactions:
            if txn.customer_id not in self.transaction_history:
                self.transaction_history[txn.customer_id] = []
            
            self.transaction_history[txn.customer_id].append(txn)
    
    def get_latest_timestamp(self) -> Optional[datetime]:
        """
        Findet den neuesten Timestamp in allen Transaktionen
        
        Returns:
            Neuester Timestamp oder None
        """
        latest = None
        for txns in self.transaction_history.values():
            for txn in txns:
                if txn.timestamp:
                    if latest is None or txn.timestamp > latest:
                        latest = txn.timestamp
        return latest
    
    def is_historical_data(self, threshold_days: int = 90) -> bool:
        """
        Prüft, ob die Daten historisch sind (neueste Transaktion > threshold_days alt)
        
        Args:
            threshold_days: Schwelle in Tagen
            
        Returns:
            True wenn historische Daten, False wenn aktuelle Daten
        """
        latest = self.get_latest_timestamp()
        if latest is None:
            return False
        
        days_ago = (datetime.now() - latest).days
        return days_ago > threshold_days
    
    def get_customer_transactions(
        self,
        customer_id: str,
        days: int = None,
        exclude_recent_days: int = 0,
        use_data_end_as_reference: bool = False
    ) -> List[Transaction]:
        """
        Holt Transaktionen eines Kunden
        
        Args:
            customer_id: Kunden-ID
            days: Optional - nur letzte N Tage
            exclude_recent_days: Optional - schließe die letzten N Tage aus (für Baseline)
            use_data_end_as_reference: Wenn True, nutze das Ende der Daten als Referenz statt "jetzt"
                                      (nützlich für historische Daten)
            
        Returns:
            Liste von Transaktionen
        """
        if customer_id not in self.transaction_history:
            return []
        
        txns = self.transaction_history[customer_id]
        
        # Bestimme Referenzpunkt: "jetzt" oder Ende der Daten
        if use_data_end_as_reference:
            reference_time = self.get_latest_timestamp()
            if reference_time is None:
                reference_time = datetime.now()
        else:
            reference_time = datetime.now()
        
        if days:
            cutoff = reference_time - timedelta(days=days)
            txns = [
                t for t in txns
                if t.timestamp and t.timestamp >= cutoff
            ]
        
        if exclude_recent_days > 0:
            exclude_cutoff = reference_time - timedelta(days=exclude_recent_days)
            txns = [
                t for t in txns
                if t.timestamp and t.timestamp < exclude_cutoff
            ]
        
        return txns
    
    def calculate_suspicion_score(
        self,
        weight_analysis: WeightAnalysis,
        entropy_analysis: EntropyAnalysis,
        predictability_analysis: PredictabilityAnalysis,
        trust_analysis: TrustScoreAnalysis,
        statistical_analysis: StatisticalAnalysis
    ) -> float:
        """
        Berechnet den finalen Merkwürdigkeits-Index (Suspicion Score)
        
        Unterstützt zwei Modi:
        1. TP/SP-System (use_tp_sp_system=True): Dokumentations-konform
        2. Legacy-System (use_tp_sp_system=False): Alte Berechnung
        
        M = ABSOLUTE_SCORE + RELATIVE_SCORE
        
        Args:
            weight_analysis: Weight-Analyse
            entropy_analysis: Entropie-Analyse
            predictability_analysis: Predictability-Analyse
            trust_analysis: Trust Score Analyse
            statistical_analysis: Statistische Analyse
            
        Returns:
            Suspicion Score (0-10+)
        """
        if self.use_tp_sp_system:
            return self._calculate_suspicion_score_tp_sp(
                weight_analysis,
                entropy_analysis,
                predictability_analysis,
                trust_analysis,
                statistical_analysis
            )
        else:
            return self._calculate_suspicion_score_legacy(
                weight_analysis,
                entropy_analysis,
                trust_analysis,
                statistical_analysis
            )
    
    def _calculate_suspicion_score_tp_sp(
        self,
        weight_analysis: WeightAnalysis,
        entropy_analysis: EntropyAnalysis,
        predictability_analysis: PredictabilityAnalysis,
        trust_analysis: TrustScoreAnalysis,
        statistical_analysis: StatisticalAnalysis
    ) -> float:
        """
        Berechnet Suspicion Score mit TP/SP-System (laut Dokumentation)
        
        Returns:
            Suspicion Score (0-10+)
        """
        # 1. Berechne Module-Punkte (TP/SP)
        module_points = self.calculate_module_points(
            weight_analysis,
            entropy_analysis,
            predictability_analysis,
            trust_analysis,
            statistical_analysis
        )
        
        # 2. Berechne gewichtete Summe mit Multiplikatoren (40/25/25/10)
        # Laut Dokumentation: Weight 40%, Entropie 25%, Predictability 25%, Statistik 10%
        weighted_points = 0.0
        for name, points in module_points.items():
            # Überspringe Trust_Score - nicht mehr verwendet
            if name == 'trust':
                continue
            
            # Netto für Suspicion: SP - TP (nicht net_points!)
            suspicion_net = (points.suspicion_points - points.trust_points) * points.multiplier
            
            # Gewichtung nach Modul (laut Dokumentation)
            if name == 'weight':
                weighted_points += 0.40 * suspicion_net  # 40%
            elif name == 'entropy':
                weighted_points += 0.25 * suspicion_net  # 25%
            elif name == 'predictability':
                weighted_points += 0.25 * suspicion_net  # 25%
            elif name == 'statistics':
                weighted_points += 0.10 * suspicion_net  # 10%
        
        # 3. Verstärkungslogik anwenden
        amplification_factor = self.apply_amplification_logic(module_points)
        
        # 4. Kombiniere: 70% absolute (mit Verstärkung), 30% relative
        # WICHTIG: Laut Dokumentation werden Suspicion Points direkt verwendet (0-1000+)
        # Die Gewichtung 40/30/30 ist bereits in weighted_points angewendet (ohne Trust_Score)
        # Die 0.7/0.3 Aufteilung bezieht sich auf absolute vs. relative Komponenten
        absolute_score = weighted_points * amplification_factor * 0.7
        
        # Relative Komponenten (Z-Scores) - konvertiere zu SP-Einheiten
        # Z-Scores (0-5) müssen zu SP skaliert werden
        # Laut Dokumentation: max Z-Score 5.0 sollte etwa 150 SP entsprechen (30 SP pro Z-Score)
        z_w = max(0, min(weight_analysis.z_score_30d, 5)) if weight_analysis.z_score_30d > 0 else 0
        z_h = max(0, min(abs(entropy_analysis.z_score), 5)) if entropy_analysis.z_score != 0 else 0
        
        # Skaliere Z-Scores zu SP: max 5.0 Z-Score = 150 SP (30 SP pro Z-Score)
        relative_score_sp = (
            self.alpha * z_w * 30.0 +  # 0-5 Z-Score → 0-90 SP
            self.beta * z_h * 30.0      # 0-5 Z-Score → 0-60 SP
        )
        
        # 5. Kombiniere absolute (70%) und relative (30%)
        # WICHTIG: Die 0.7/0.3 Aufteilung wird hier angewendet
        total_points = absolute_score + relative_score_sp * 0.3
        
        # 6. Nichtlineare Skalierung
        scaled_points = self.apply_nonlinear_scaling(total_points)
        
        # 7. Suspicion Score = Suspicion Points direkt (laut Dokumentation)
        # Laut Dokumentation: Suspicion Points werden direkt verwendet (0-1000+)
        # Keine Division - die Punkte sind bereits in SP-Einheiten
        # Thresholds: GREEN < 150, YELLOW < 300, ORANGE < 500, RED >= 500
        suspicion_score = scaled_points
        
        return max(0.0, suspicion_score)
    
    def _calculate_suspicion_score_legacy(
        self,
        weight_analysis: WeightAnalysis,
        entropy_analysis: EntropyAnalysis,
        trust_analysis: TrustScoreAnalysis,
        statistical_analysis: StatisticalAnalysis
    ) -> float:
        """
        Legacy-Berechnung (alte Methode für Rückwärtskompatibilität)
        
        Returns:
            Suspicion Score (0-10+)
        """
        # ==========================================
        # ABSOLUTE KOMPONENTEN (Primär, Gewicht: 70%)
        # ==========================================
        # Diese funktionieren IMMER, auch ohne historische Daten
        
        # 1. Smurfing (absolute Indikatoren)
        smurfing_score = 0.0
        if weight_analysis.is_suspicious:
            if weight_analysis.threshold_avoidance_ratio >= 0.5:
                smurfing_score += 2.0
            if weight_analysis.cumulative_large_amount >= 50000:
                smurfing_score += 1.5
            if weight_analysis.temporal_density_weeks > 5.0:
                smurfing_score += 4.0
            elif weight_analysis.temporal_density_weeks > 2.0:
                smurfing_score += 3.0
            elif weight_analysis.temporal_density_weeks > 1.0:
                smurfing_score += 2.0
            elif weight_analysis.temporal_density_weeks > 0.5:
                smurfing_score += 1.0
            if weight_analysis.economic_plausibility_issue:
                smurfing_score += 1.5
            if weight_analysis.source_of_funds_exceeded:
                smurfing_score += 2.0
        
        # 2. Entropie (absolute Indikatoren)
        entropy_score = 0.0
        if entropy_analysis.entropy_aggregate < 0.3:
            entropy_score += 1.5
        elif entropy_analysis.entropy_aggregate > 2.0:
            entropy_score += 1.5
        if entropy_analysis.entropy_payment_method < 0.1:
            entropy_score += 0.5
        
        # 3. Trust Score ENTFERNT - nicht mehr verwendet
        # Suspicion_Score zeigt bereits, ob dem Kunden vertraut werden soll
        
        # 4. Statistische Methoden
        stats_score = (
            0.10 * statistical_analysis.benford_score * 5 +
            0.10 * statistical_analysis.velocity_score * 5 +
            0.10 * statistical_analysis.time_anomaly_score * 5 +
            0.10 * statistical_analysis.clustering_score * 5 +
            0.60 * statistical_analysis.layering_score * 5
        )
        
        # Kombiniere absolute Komponenten (70% Gewicht)
        # GEWICHTUNG ANGEPASST: 40% Weight, 30% Entropy, 30% Statistics (Trust_Score entfernt)
        absolute_score = (
            0.40 * smurfing_score +
            0.30 * entropy_score +
            0.30 * stats_score
        ) * 0.7
        
        # ==========================================
        # RELATIVE KOMPONENTEN (Sekundär, Gewicht: 30%)
        # ==========================================
        z_w = max(0, min(weight_analysis.z_score_30d, 5)) if weight_analysis.z_score_30d > 0 else 0
        z_h = max(0, min(abs(entropy_analysis.z_score), 5)) if entropy_analysis.z_score != 0 else 0
        
        relative_score = (
            self.alpha * z_w +
            self.beta * z_h
        ) * 0.3
        
        # Finaler Score = Absolute (70%) + Relative (30%)
        M = absolute_score + relative_score
        
        return M
    
    def calculate_module_points(
        self,
        weight_analysis: WeightAnalysis,
        entropy_analysis: EntropyAnalysis,
        predictability_analysis: PredictabilityAnalysis,
        trust_analysis: TrustScoreAnalysis,
        statistical_analysis: StatisticalAnalysis
    ) -> Dict[str, ModulePoints]:
        """
        Berechnet Trust Points (TP) und Suspicion Points (SP) pro Modul
        mit Multiplikatoren (µ) laut Dokumentation
        
        Returns:
            Dict mit ModulePoints für jedes Modul
        """
        points = {}
        
        # 1. Weight-Analyse (µ = 2.0, Suspicion-dominant)
        # WICHTIG: Auch ohne is_suspicious können hohe Temporal Density oder andere Indikatoren SP geben
        weight_tp = 0.0
        weight_sp = 0.0
        
        # Temporal Density ist ein starker Indikator - auch ohne is_suspicious
        if weight_analysis.temporal_density_weeks > 5.0:
            weight_sp += 400  # Sehr hohe Dichte
        elif weight_analysis.temporal_density_weeks > 2.0:
            weight_sp += 300  # Hohe Dichte
        elif weight_analysis.temporal_density_weeks > 1.0:
            weight_sp += 200  # Erhöhte Dichte
        elif weight_analysis.temporal_density_weeks > 0.5:
            weight_sp += 100  # Leicht erhöhte Dichte
        
        # Weitere Indikatoren (nur wenn is_suspicious)
        if weight_analysis.is_suspicious:
            if weight_analysis.threshold_avoidance_ratio >= 0.5:
                weight_sp += 300  # Starker Indikator
            if weight_analysis.cumulative_large_amount >= 50000:
                weight_sp += 150
            if weight_analysis.economic_plausibility_issue:
                weight_sp += 150
            if weight_analysis.source_of_funds_exceeded:
                weight_sp += 200
        
        points['weight'] = ModulePoints(
            trust_points=weight_tp,
            suspicion_points=weight_sp,
            multiplier=2.0  # µ = 2.0 laut Dokumentation
        )
        
        # 2. Entropie-Analyse (µ = 1.2, bidirektional)
        entropy_tp = 0.0
        entropy_sp = 0.0
        
        if entropy_analysis.entropy_aggregate < 0.3:
            entropy_sp += 150  # Extreme Konzentration
        elif entropy_analysis.entropy_aggregate > 2.0:
            entropy_sp += 150  # Extreme Streuung
        
        if entropy_analysis.entropy_payment_method < 0.1:
            entropy_sp += 50
        
        points['entropy'] = ModulePoints(
            trust_points=entropy_tp,
            suspicion_points=entropy_sp,
            multiplier=1.2  # µ = 1.2 laut Dokumentation
        )
        
        # 3. Predictability-Analyse (µ = 1.0, Trust-dominant)
        # Laut Dokumentation: Hohe Predictability → +150 TP, Instabilität → -150 SP
        predictability_tp = 0.0
        predictability_sp = 0.0
        
        if predictability_analysis.overall_predictability >= 0.8:
            predictability_tp += 150  # Hohe Predictability (T ≥ 0.8) → +150 TP
        elif predictability_analysis.overall_predictability >= 0.6:
            predictability_tp += 80  # Mittlere Predictability → +80 TP
        
        # Instabilität führt zu Suspicion Points
        if predictability_analysis.overall_predictability < 0.3:
            predictability_sp += 150  # Sehr instabil → -150 SP
        elif predictability_analysis.overall_predictability < 0.5:
            predictability_sp += 75  # Instabil → -75 SP
        
        # Z-Score Abweichung (wenn stark negativ)
        if predictability_analysis.z_score < -2.0:
            predictability_sp += 50  # Starke negative Abweichung von Baseline
        
        points['predictability'] = ModulePoints(
            trust_points=predictability_tp,
            suspicion_points=predictability_sp,
            multiplier=1.0  # µ = 1.0 laut Dokumentation
        )
        
        # 4. Trust_Score ENTFERNT - nicht mehr verwendet
        # Suspicion_Score zeigt bereits, ob dem Kunden vertraut werden soll
        # Keine Trust Points mehr berechnen
        
        # 5. Statistische Methoden (µ = 1.5, Suspicion-dominant)
        stats_tp = 0.0
        stats_sp = 0.0
        
        # Konvertiere Scores (0-1) zu Punkten (0-500)
        if statistical_analysis.benford_score > 0.6:
            stats_sp += 200
        if statistical_analysis.velocity_score > 0.7:
            stats_sp += 150
        if statistical_analysis.time_anomaly_score > 0.6:
            stats_sp += 100
        if statistical_analysis.layering_score > 0.9:
            stats_sp += 500  # Layering ist sehr kritisch
        elif statistical_analysis.layering_score > 0.7:
            stats_sp += 300
        elif statistical_analysis.layering_score > 0.5:
            stats_sp += 150
        
        points['statistics'] = ModulePoints(
            trust_points=stats_tp,
            suspicion_points=stats_sp,
            multiplier=1.5  # µ = 1.5 laut Dokumentation
        )
        
        return points
    
    def apply_amplification_logic(
        self,
        module_points: Dict[str, ModulePoints]
    ) -> float:
        """
        Wendet Verstärkungslogik an:
        - Kombinatorische Hochstufung
        - Verstärkungsfaktor: v = 1 + 0.1 × (n_Module - 1)
        - Synergieerkennung
        
        Returns:
            Verstärkungsfaktor
        """
        # Zähle auffällige Module (SP > 0)
        suspicious_modules = [
            name for name, points in module_points.items()
            if points.suspicion_points > 0
        ]
        n_modules = len(suspicious_modules)
        
        # Basis-Verstärkungsfaktor
        if n_modules > 1:
            v = 1.0 + 0.1 * (n_modules - 1)
            # Maximal 30% Verstärkung
            v = min(v, 1.3)
        else:
            v = 1.0
        
        # Synergieerkennung
        # Weight + Velocity = Verstärkung 1.2x
        if 'weight' in suspicious_modules and 'statistics' in suspicious_modules:
            # Prüfe ob Velocity auch auffällig
            if module_points['statistics'].suspicion_points > 100:
                v *= 1.2
        
        # Layering + Entropie = Direkte Hochstufung
        if 'statistics' in suspicious_modules and 'entropy' in suspicious_modules:
            layering_sp = module_points['statistics'].suspicion_points
            if layering_sp > 300:  # Starker Layering-Indikator
                v *= 1.3  # Zusätzliche Verstärkung
        
        # Trust_Score wurde entfernt - keine Dämpfung mehr basierend auf Trust
        
        return v
    
    def apply_nonlinear_scaling(self, points: float) -> float:
        """
        Nichtlineare Skalierung laut Dokumentation:
        - Kleine Punktmengen (0-150 SP): nahezu linear
        - Ab 300 SP: progressiv (1.2x bis 1.5x)
        - Ab 500 SP: Dämpfungskoeffizient
        
        Returns:
            Skalierter Punktewert
        """
        abs_points = abs(points)
        sign = 1.0 if points >= 0 else -1.0
        
        if abs_points <= 150:
            # Linear
            scaled = abs_points
        elif abs_points <= 300:
            # Progressiv: 1.2x
            scaled = 150 + (abs_points - 150) * 1.2
        elif abs_points <= 500:
            # Progressiv: 1.5x
            scaled = 150 + 150 * 1.2 + (abs_points - 300) * 1.5
        else:
            # Dämpfung: logarithmisch abflachen
            excess = abs_points - 500
            scaled = 150 + 150 * 1.2 + 200 * 1.5 + excess * 0.8
        
        return sign * scaled
    
    def determine_risk_level(self, suspicion_score: float) -> RiskLevel:
        """
        Bestimmt Risiko-Level basierend auf Suspicion Score
        
        Args:
            suspicion_score: Merkwürdigkeits-Index
            
        Returns:
            RiskLevel Enum
            
        Angepasste Thresholds für absolute Schwellenwerte:
        - GREEN: Normales Verhalten, keine Auffälligkeiten
        - YELLOW: Leichte Auffälligkeiten, Monitoring empfohlen
        - ORANGE: Deutliche Verdachtsmomente, Überprüfung erforderlich
        - RED: Starker Verdacht, sofortige Aktion nötig
        """
        # Thresholds laut Dokumentation (Suspicion Points direkt):
        # - GREEN: 0-150 SP (Unauffällig)
        # - YELLOW: 150-300 SP (Leichte Auffälligkeit)
        # - ORANGE: 300-500 SP (Erhöhtes Risiko)
        # - RED: 500-1000+ SP (Hoher Verdacht)
        if suspicion_score < 150:  # GREEN: Unauffällig
            return RiskLevel.GREEN
        elif suspicion_score < 300:  # YELLOW: Leichte Auffälligkeit
            return RiskLevel.YELLOW
        elif suspicion_score < 500:  # ORANGE: Erhöhtes Risiko
            return RiskLevel.ORANGE
        else:  # RED: Hoher Verdacht (>= 500 SP)
            return RiskLevel.RED
    
    def generate_flags(
        self,
        weight_analysis: WeightAnalysis,
        entropy_analysis: EntropyAnalysis,
        predictability_analysis: PredictabilityAnalysis,
        trust_analysis: TrustScoreAnalysis,
        statistical_analysis: StatisticalAnalysis
    ) -> List[str]:
        """
        Generiert spezifische Warnungen
        
        Args:
            weight_analysis: Weight-Analyse
            entropy_analysis: Entropie-Analyse
            trust_analysis: Trust Score Analyse
            statistical_analysis: Statistische Analyse
            
        Returns:
            Liste von Warnmeldungen
        """
        flags = []
        
        # Weight/Smurfing Flags
        if weight_analysis.is_suspicious:
            # Prüfe auf Threshold-Avoidance (nah unter Bar-Grenze)
            if weight_analysis.threshold_avoidance_ratio >= 0.5:
                flags.append("🚨 SMURFING-VERDACHT: Bar-Investments nah unter 10.000€ Grenze")
                if weight_analysis.cumulative_large_amount >= 50000.0:
                    flags.append(f"💰 GROSSE KUMULATIVE SUMME: {weight_analysis.cumulative_large_amount:,.0f}€ nah unter Grenze")
            else:
                flags.append("⚠️ SMURFING-VERDACHT: Viele kleine Transaktionen")
        
        if weight_analysis.z_score_30d >= 3.0:
            flags.append("🔴 HOHE TRANSAKTIONSAKTIVITÄT: Z-Score >= 3")
        
        if weight_analysis.small_transaction_ratio >= 0.8:
            flags.append("💰 KLEINBETRAGS-MUSTER: >80% Transaktionen <2000 EUR")
        
        # NEUE FLAGS: Threshold-Avoidance Details
        if weight_analysis.threshold_avoidance_ratio >= 0.7:
            flags.append(f"🎯 THRESHOLD-AVOIDANCE: {weight_analysis.threshold_avoidance_ratio*100:.0f}% der Bar-Investments nah unter Grenze")
        
        if weight_analysis.temporal_density_weeks > 0.5:
            flags.append(f"⏱️ HOHE TEMPORALE DICHTE: {weight_analysis.temporal_density_weeks:.2f} Transaktionen/Woche")
        
        # Source of Funds Flags
        if weight_analysis.source_of_funds_exceeded:
            flags.append("🚨 SOURCE OF FUNDS ÜBERSCHRITTEN: Kumulative Summe > angegebener SoF")
        
        # Economic Plausibility Flags
        if weight_analysis.economic_plausibility_issue:
            flags.append("⚠️ ECONOMIC PLAUSIBILITY: Unrealistisch hohe Beträge im Verhältnis zum Einkommen")
        
        # Entropie Flags
        # ABSOLUTE SCHWELLENWERTE (funktionieren auch ohne historische Daten)
        if entropy_analysis.entropy_aggregate < 0.3:
            flags.append("📍 ENTROPIE-KANALISATION: Extreme Konzentration auf wenige Muster")
        elif entropy_analysis.entropy_aggregate > 2.0:
            flags.append("🔀 ENTROPIE-VERSCHLEIERUNG: Extreme Streuung (jeder Betrag unterschiedlich)")
        
        # ENTFERNT: "EINZIGE ZAHLUNGSMETHODE" ist nicht verdächtig an sich
        # Viele normale Kunden verwenden nur eine Zahlungsmethode (z.B. nur SEPA)
        # Dieses Flag wird nur in Kombination mit anderen verdächtigen Indikatoren verwendet
        # (z.B. wenn zusätzlich extreme Entropie-Kanalisation vorliegt)
        
        # RELATIVE SCHWELLENWERTE (nur wenn Z-Score vorhanden)
        if entropy_analysis.is_complex and entropy_analysis.z_score != 0:
            if entropy_analysis.z_score > 2.0:
                flags.append("🔀 UNGEWÖHNLICHE STREUUNG: Erhöhte Komplexität vs. Historie")
            elif entropy_analysis.z_score < -2.0:
                flags.append("📍 KANALISATION: Konzentration auf wenige Muster vs. Historie")
        
        # Predictability Flags
        if not predictability_analysis.is_stable:
            if predictability_analysis.overall_predictability < 0.3:
                flags.append("⚠️ INSTABILES VERHALTEN: Sehr niedrige Predictability (< 0.3)")
            elif predictability_analysis.overall_predictability < 0.5:
                flags.append("📊 UNVORHERSAGBARES VERHALTEN: Niedrige Predictability (< 0.5)")
        
        if predictability_analysis.z_score < -2.0:
            flags.append("📉 PREDICTABILITY-ABWEICHUNG: Starke negative Abweichung von historischer Baseline")
        
        # Trust Score Flags
        if trust_analysis.current_score < 0.3:
            flags.append("📉 NIEDRIGER TRUST SCORE: Unvorhersagbares Verhalten")
        
        if trust_analysis.self_deviation > 0.7:
            flags.append("⚡ VERHALTENSÄNDERUNG: Starke Abweichung vom eigenen Profil")
        
        # Statistische Flags
        if statistical_analysis.benford_score > 0.6:
            flags.append("📊 BENFORD-ABWEICHUNG: Unnatürliche Zahlenverteilung")
        
        if statistical_analysis.velocity_score > 0.7:
            flags.append("⏱️ HOHE VELOCITY: Ungewöhnliche Transaktionsgeschwindigkeit")
        
        if statistical_analysis.time_anomaly_score > 0.6:
            flags.append("🕐 ZEITANOMALIEN: Ungewöhnliche Uhrzeiten/Tage")
        
        if statistical_analysis.clustering_score > 0.7:
            flags.append("👥 PEER-ABWEICHUNG: Untypisch für Kundengruppe")
        
        # Geldwäsche-Muster (Layering)
        # NIEDRIGERE SCHWELLENWERTE für bessere Erkennung
        if statistical_analysis.layering_score > 0.5:
            flags.append("🚨 GELDWÄSCHE-VERDACHT: Bar-Einzahlung → SEPA-Auszahlung")
        elif statistical_analysis.layering_score > 0.3:
            flags.append("⚠️ LAYERING-MUSTER: Auffällige Bar/SEPA-Kombination")
        
        return flags
    
    def generate_recommendations(
        self,
        risk_level: RiskLevel,
        flags: List[str]
    ) -> List[str]:
        """
        Generiert Handlungsempfehlungen
        
        Args:
            risk_level: Risiko-Level
            flags: Warnmeldungen
            
        Returns:
            Liste von Empfehlungen
        """
        recommendations = []
        
        if risk_level == RiskLevel.GREEN:
            recommendations.append("✅ Keine Maßnahmen erforderlich")
        
        elif risk_level == RiskLevel.YELLOW:
            recommendations.append("👁️ Monitoring intensivieren")
            recommendations.append("📝 Transaktionsmuster dokumentieren")
        
        elif risk_level == RiskLevel.ORANGE:
            recommendations.append("📄 Nachweise anfordern (z.B. Source of Funds)")
            recommendations.append("🔍 Enhanced Due Diligence prüfen")
            recommendations.append("📞 Kundenkontakt aufnehmen")
        
        elif risk_level == RiskLevel.RED:
            recommendations.append("🚨 DRINGEND: Nachweise erforderlich")
            recommendations.append("⚠️ Enhanced Due Diligence durchführen")
            recommendations.append("📋 Compliance-Team informieren")
            recommendations.append("🔒 Ggf. temporäre Limits setzen")
        
        # Spezifische Empfehlungen basierend auf Flags
        if any("SMURFING" in flag for flag in flags):
            recommendations.append("💡 Prüfen: Geschäftliche Begründung für Zahlungsstruktur")
        
        if any("BENFORD" in flag for flag in flags):
            recommendations.append("💡 Prüfen: Belege und Rechnungen auf Authentizität")
        
        if any("VELOCITY" in flag for flag in flags):
            recommendations.append("💡 Prüfen: Plausibilität der Transaktionsfrequenz")
        
        if any("GELDWÄSCHE" in flag or "LAYERING" in flag for flag in flags):
            recommendations.append("🚨 GELDWÄSCHE-VERDACHT: Source of Funds für Bar-Einzahlungen")
            recommendations.append("🔍 Prüfen: Zusammenhang zwischen Ein- und Auszahlungen")
            recommendations.append("⚠️ Ggf. SAR (Suspicious Activity Report) erwägen")
        
        return recommendations
    
    def set_customer_info(self, customer_info: CustomerInfo):
        """
        Setzt CustomerInfo für einen Kunden
        
        Args:
            customer_info: CustomerInfo Objekt
        """
        self.customer_info[customer_info.customer_id] = customer_info
    
    def analyze_customer(
        self,
        customer_id: str,
        recent_days: int = 30,
        all_transactions: List[Transaction] = None
    ) -> CustomerRiskProfile:
        """
        Vollständige Analyse eines Kunden
        
        Args:
            customer_id: Kunden-ID
            recent_days: Zeitfenster für aktuelle Analyse
            all_transactions: Alle Transaktionen (für Peer-Vergleiche)
            
        Returns:
            CustomerRiskProfile
        """
        # Erkenne ob historische Daten
        use_historical_mode = self.is_historical_data()
        
        # Hole Transaktionen
        recent_txns = self.get_customer_transactions(
            customer_id,
            days=recent_days,
            use_data_end_as_reference=use_historical_mode
        )
        
        # Historische Transaktionen OHNE die aktuellen (für saubere Baseline)
        # Wenn recent_days >= historical_days, verwende die erste Hälfte als historisch
        if recent_days >= self.historical_days:
            # Verwende alle Transaktionen, aber teile sie in historisch/recent
            all_customer_txns = self.get_customer_transactions(
                customer_id,
                days=self.historical_days,
                use_data_end_as_reference=use_historical_mode
            )
            # Sortiere nach Datum
            all_customer_txns = sorted([t for t in all_customer_txns if t.timestamp], key=lambda t: t.timestamp)
            
            if len(all_customer_txns) > 1:
                # Erste Hälfte = historisch, zweite Hälfte = recent
                split_idx = len(all_customer_txns) // 2
                historical_txns = all_customer_txns[:split_idx]
                # Aktualisiere recent_txns mit der zweiten Hälfte
                recent_txns = all_customer_txns[split_idx:]
            else:
                historical_txns = []
        else:
            # Normale Logik: historische Transaktionen OHNE die aktuellen
            historical_txns = self.get_customer_transactions(
                customer_id,
                days=self.historical_days,
                exclude_recent_days=recent_days,
                use_data_end_as_reference=use_historical_mode
            )
        
        if not recent_txns:
            # Kunde ohne aktuelle Transaktionen
            raise ValueError(f"Keine Transaktionen für Kunde {customer_id}")
        
        # Kunden-Info
        customer_name = recent_txns[0].customer_name
        total_transactions = len(recent_txns)
        total_amount = sum(t.transaction_amount for t in recent_txns)
        
        # Hole CustomerInfo (falls vorhanden)
        customer_info = self.customer_info.get(customer_id, None)
        
        # 1. Weight-Analyse (Anti-Smurfing)
        weight_analysis = self.weight_detector.analyze(
            recent_txns,
            historical_txns,
            customer_info
        )
        
        # 2. Entropie-Analyse
        entropy_analysis = self.entropy_detector.analyze(
            recent_txns,
            historical_txns
        )
        
        # 3. Predictability-Analyse
        predictability_analysis = self.predictability_detector.analyze(
            recent_txns,
            historical_txns
        )
        
        # 4. Trust Score
        # Peer-Abweichung: Verwende nur ähnliche Kunden (nicht alle)
        # Ähnliche Kunden = ähnliche durchschnittliche Transaktionsgröße (±50%)
        customer_mean = np.mean([t.transaction_amount for t in recent_txns]) if recent_txns else 0
        peer_transactions = []
        if customer_mean > 0:
            for txn in all_transactions:
                # Nur Transaktionen von anderen Kunden mit ähnlicher Größe
                if txn.customer_id != customer_id:
                    # Grobe Filterung: ähnliche Transaktionsgröße (±50%)
                    if 0.5 * customer_mean <= txn.transaction_amount <= 2.0 * customer_mean:
                        peer_transactions.append(txn)
        
        # Wenn zu wenige Peers, verwende keine Peer-Abweichung
        if len(peer_transactions) < 10:
            peer_transactions = None  # Deaktiviere Peer-Abweichung
        
        trust_analysis = self.trust_calculator.analyze(
            customer_id,
            recent_txns,
            historical_txns,
            peer_transactions=peer_transactions
        )
        
        # 4. Statistische Analysen
        statistical_analysis = self.statistical_analyzer.analyze(
            recent_txns,
            all_transactions
        )
        
        # ==========================================
        # TRUST_SCORE ANPASSUNG: Direkte Verknüpfung mit verdächtigen Indikatoren
        # ==========================================
        # Wenn verdächtige Indikatoren erkannt werden, Trust_Score direkt reduzieren
        # Dies stellt sicher, dass Trust_Score mit Risk_Level korreliert
        trust_penalty = 0.0
        
        # 1. Smurfing erkannt → Trust_Score reduzieren
        if weight_analysis.is_suspicious:
            if weight_analysis.threshold_avoidance_ratio >= 0.5:
                trust_penalty += 0.3  # Starker Smurfing-Indikator
            elif weight_analysis.threshold_avoidance_ratio >= 0.3:
                trust_penalty += 0.2  # Leichter Smurfing-Indikator
            if weight_analysis.cumulative_large_amount >= 50000:
                trust_penalty += 0.2  # Große kumulative Summe
            if weight_analysis.temporal_density_weeks > 1.0:
                trust_penalty += 0.2  # Hohe temporale Dichte
        
        # 2. Layering (Geldwäsche) erkannt → Trust_Score stark reduzieren
        if statistical_analysis.layering_score > 0.7:
            trust_penalty += 0.4  # Starker Layering-Verdacht
        elif statistical_analysis.layering_score > 0.5:
            trust_penalty += 0.3  # Moderater Layering-Verdacht
        elif statistical_analysis.layering_score > 0.3:
            trust_penalty += 0.2  # Leichter Layering-Verdacht
        
        # 3. Entropie-Anomalie erkannt → Trust_Score reduzieren
        if entropy_analysis.is_complex:
            if entropy_analysis.entropy_aggregate < 0.3 or entropy_analysis.entropy_aggregate > 2.0:
                trust_penalty += 0.2  # Extreme Entropie
        
        # 4. Wende Penalty an (maximal 70% Reduktion)
        trust_penalty = min(trust_penalty, 0.7)
        adjusted_trust_score = trust_analysis.current_score * (1.0 - trust_penalty)
        
        # Aktualisiere Trust_Score im Analysis-Objekt
        trust_analysis.current_score = max(0.0, min(1.0, adjusted_trust_score))
        
        # 5. Suspicion Score
        suspicion_score = self.calculate_suspicion_score(
            weight_analysis,
            entropy_analysis,
            predictability_analysis,
            trust_analysis,
            statistical_analysis
        )
        
        # 6. Risiko-Level
        risk_level = self.determine_risk_level(suspicion_score)
        
        # 7. Flags und Empfehlungen
        flags = self.generate_flags(
            weight_analysis,
            entropy_analysis,
            predictability_analysis,
            trust_analysis,
            statistical_analysis
        )
        
        recommendations = self.generate_recommendations(risk_level, flags)
        
        # Erstelle Profil
        profile = CustomerRiskProfile(
            customer_id=customer_id,
            customer_name=customer_name,
            total_transactions=total_transactions,
            total_amount=total_amount,
            weight_analysis=weight_analysis,
            entropy_analysis=entropy_analysis,
            trust_score_analysis=trust_analysis,
            statistical_analysis=statistical_analysis,
            suspicion_score=suspicion_score,
            risk_level=risk_level,
            flags=flags,
            recommendations=recommendations,
            analysis_timestamp=datetime.now()
        )
        
        return profile
    
    def analyze_all_customers(
        self,
        recent_days: int = 30
    ) -> List[CustomerRiskProfile]:
        """
        Analysiert alle Kunden
        
        Args:
            recent_days: Zeitfenster für aktuelle Analyse
            
        Returns:
            Liste von CustomerRiskProfile
        """
        profiles = []
        
        # Alle Transaktionen für Peer-Vergleiche
        all_txns = []
        for txns in self.transaction_history.values():
            all_txns.extend(txns)
        
        # Analysiere jeden Kunden
        for customer_id in self.transaction_history.keys():
            try:
                profile = self.analyze_customer(
                    customer_id,
                    recent_days=recent_days,
                    all_transactions=all_txns
                )
                profiles.append(profile)
            except Exception as e:
                # Wenn Kunde keine Transaktionen im Zeitfenster hat, erstelle Default-Profil
                if "Keine Transaktionen" in str(e):
                    # Erstelle ein Basis-Profil (GREEN, Score 0)
                    default_profile = CustomerRiskProfile(
                        customer_id=customer_id,
                        risk_level=RiskLevel.GREEN,
                        suspicion_score=0.0,
                        flags=[],
                        weight_analysis=None,
                        entropy_analysis=None,
                        trust_score_analysis=None,
                        statistical_analysis=None,
                        analysis_timestamp=datetime.now()
                    )
                    profiles.append(default_profile)
                else:
                    print(f"Fehler bei Analyse von {customer_id}: {e}")
                continue
        
        # Sortiere nach Suspicion Score (höchste zuerst)
        profiles.sort(key=lambda p: p.suspicion_score, reverse=True)
        
        return profiles

