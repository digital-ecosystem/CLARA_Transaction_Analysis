"""
Datenmodelle für das CLARA Transaction Analysis System
"""

from pydantic import BaseModel, Field
from typing import List, Optional, Dict
from datetime import datetime
from enum import Enum


class PaymentMethod(str, Enum):
    """Zahlungsmethoden"""
    BAR = "Bar"
    SEPA = "SEPA"
    KREDITKARTE = "Kreditkarte"


class TransactionType(str, Enum):
    """Transaktionsarten"""
    INVESTMENT = "investment"
    AUSZAHLUNG = "auszahlung"


class RiskLevel(str, Enum):
    """Risiko-Level"""
    GREEN = "GREEN"      # 0-1.5
    YELLOW = "YELLOW"    # 1.5-2.5
    ORANGE = "ORANGE"    # 2.5-3.5
    RED = "RED"          # >3.5


class CustomerInfo(BaseModel):
    """Kunden-Informationen (Source of Funds, Economic Plausibility)"""
    customer_id: str = Field(..., description="Kunden-ID")
    source_of_funds: Optional[float] = Field(default=None, description="Source of Funds Betrag (EUR), None wenn nicht angegeben")
    monthly_income: Optional[float] = Field(default=None, description="Monatliches Einkommen (EUR) für Economic Plausibility")
    
    class Config:
        json_schema_extra = {
            "example": {
                "customer_id": "CUST001",
                "source_of_funds": 100000.0,
                "monthly_income": 3000.0
            }
        }


class Transaction(BaseModel):
    """Einzelne Transaktion"""
    customer_id: str = Field(..., description="Kunden-ID")
    transaction_id: str = Field(..., description="Transaktions-ID")
    customer_name: str = Field(..., description="Kundenname")
    transaction_amount: float = Field(..., ge=0, description="Betrag in EUR")
    payment_method: PaymentMethod = Field(..., description="Zahlungsmethode")
    transaction_type: TransactionType = Field(..., description="Transaktionsart")
    timestamp: Optional[datetime] = Field(default=None, description="Zeitstempel")

    class Config:
        json_schema_extra = {
            "example": {
                "customer_id": "CUST001",
                "transaction_id": "TXN001",
                "customer_name": "Max Mustermann",
                "transaction_amount": 1500.00,
                "payment_method": "Bar",
                "transaction_type": "investment",
                "timestamp": "2024-01-15T10:30:00"
            }
        }


class WeightAnalysis(BaseModel):
    """Ergebnis der Weight-Analyse (Anti-Smurfing)"""
    weight_7d: float = Field(..., description="Weight für 7 Tage")
    weight_30d: float = Field(..., description="Weight für 30 Tage")
    weight_90d: float = Field(..., description="Weight für 90 Tage")
    z_score_7d: float = Field(..., description="Z-Score für 7 Tage")
    z_score_30d: float = Field(..., description="Z-Score für 30 Tage")
    z_score_90d: float = Field(..., description="Z-Score für 90 Tage")
    is_suspicious: bool = Field(..., description="Smurfing-Verdacht")
    small_transaction_ratio: float = Field(..., description="Anteil Kleinbeträge (<2000 EUR)")
    threshold_avoidance_ratio: float = Field(..., description="Anteil Transaktionen nah unter Bar-Grenze (7000-9999 EUR)")
    cumulative_large_amount: float = Field(..., description="Kumulative Summe der Transaktionen nah unter Grenze")
    temporal_density_weeks: float = Field(..., description="Temporale Dichte (Transaktionen pro Woche)")
    source_of_funds_exceeded: bool = Field(..., description="Wurde Source of Funds überschritten?")
    economic_plausibility_issue: bool = Field(..., description="Economic Plausibility Problem erkannt?")


class EntropyAnalysis(BaseModel):
    """Ergebnis der Entropie-Analyse"""
    entropy_amount: float = Field(..., description="Entropie Betragsprofil")
    entropy_payment_method: float = Field(..., description="Entropie Zahlungsmethoden")
    entropy_transaction_type: float = Field(..., description="Entropie Transaktionstypen")
    entropy_time: float = Field(..., description="Entropie Zeitmuster")
    entropy_aggregate: float = Field(..., description="Aggregierte Entropie")
    z_score: float = Field(..., description="Z-Score der Entropie")
    is_complex: bool = Field(..., description="Ungewöhnliche Komplexität")


class TrustScoreAnalysis(BaseModel):
    """Trust Score Analyse"""
    current_score: float = Field(..., ge=0, le=1, description="Aktueller Trust Score (0-1)")
    predictability: float = Field(..., description="Vorhersagbarkeit")
    self_deviation: float = Field(..., description="Abweichung vom eigenen Muster")
    peer_deviation: float = Field(..., description="Abweichung von Peer-Gruppe")


class StatisticalAnalysis(BaseModel):
    """Zusätzliche statistische Analysen"""
    benford_score: float = Field(..., description="Benford's Law Abweichung")
    velocity_score: float = Field(..., description="Transaktionsgeschwindigkeit")
    time_anomaly_score: float = Field(..., description="Zeitliche Anomalien")
    clustering_score: float = Field(..., description="Verhaltenscluster-Abweichung")
    layering_score: float = Field(..., description="Cash-to-Bank Layering (Geldwäsche)")


class PredictabilityAnalysis(BaseModel):
    """Ergebnis der Predictability-Analyse (Verhaltensstabilität)"""
    temporal_stability: float = Field(..., description="Zeitliche Stabilität (0-1)")
    amount_consistency: float = Field(..., description="Betrags-Konsistenz (0-1)")
    channel_continuity: float = Field(..., description="Kanal-Kontinuität (0-1)")
    overall_predictability: float = Field(..., description="Gesamt-Predictability (0-1)")
    z_score: float = Field(..., description="Z-Score der Predictability")
    is_stable: bool = Field(..., description="Ist das Verhalten stabil? (Predictability >= 0.7)")


class ModulePoints(BaseModel):
    """Punkte pro Modul (TP/SP-System laut Dokumentation)"""
    trust_points: float = Field(default=0.0, description="Trust Points (positiv)")
    suspicion_points: float = Field(default=0.0, description="Suspicion Points (negativ)")
    multiplier: float = Field(default=1.0, description="Modul-Multiplikator (µ)")
    
    @property
    def net_points(self) -> float:
        """Netto-Punkte (TP - SP)"""
        return self.trust_points - self.suspicion_points


class CustomerRiskProfile(BaseModel):
    """Vollständiges Risikoprofil eines Kunden"""
    customer_id: str
    customer_name: str = Field(default="", description="Kundenname (leer wenn unbekannt)")
    total_transactions: int = Field(default=0, description="Anzahl Transaktionen")
    total_amount: float = Field(default=0.0, description="Gesamtbetrag")
    
    # Hauptanalysen (Optional für inaktive Kunden)
    weight_analysis: Optional[WeightAnalysis] = Field(default=None, description="Weight-Analyse")
    entropy_analysis: Optional[EntropyAnalysis] = Field(default=None, description="Entropie-Analyse")
    predictability_analysis: Optional[PredictabilityAnalysis] = Field(default=None, description="Predictability-Analyse")
    trust_score_analysis: Optional[TrustScoreAnalysis] = Field(default=None, description="Trust Score Analyse")
    statistical_analysis: Optional[StatisticalAnalysis] = Field(default=None, description="Statistische Analyse")
    
    # Gesamtbewertung
    suspicion_score: float = Field(..., description="Gesamtverdachts-Score (M)")
    risk_level: RiskLevel
    flags: List[str] = Field(default_factory=list, description="Spezifische Warnungen")
    recommendations: List[str] = Field(default_factory=list, description="Empfohlene Maßnahmen")
    
    analysis_timestamp: datetime = Field(default_factory=datetime.now)


class AnalysisResponse(BaseModel):
    """API Response für Analysen"""
    status: str
    message: str
    analyzed_customers: int
    flagged_customers: List[CustomerRiskProfile]
    summary: Dict[str, int] = Field(
        default_factory=lambda: {
            "green": 0,
            "yellow": 0,
            "orange": 0,
            "red": 0
        }
    )


class HealthResponse(BaseModel):
    """Health Check Response"""
    status: str
    version: str
    uptime_seconds: float

