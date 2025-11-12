"""
Anti-Smurfing Weight-Detektor

Implementiert die Weight-Variable zur Erkennung von "Structuring":
- Kombiniert Transaktionshöhe und Häufigkeit
- Log-Transformation für diminishing returns
- Z-Score Normalisierung gegen historische Baseline
- Rollierende Zeitfenster (7, 30, 90 Tage)
"""

import numpy as np
import pandas as pd
from datetime import datetime, timedelta
from typing import Dict, List, Tuple, Optional
from models import Transaction, WeightAnalysis, CustomerInfo


class WeightDetector:
    """
    Erkennt Smurfing-Muster durch intelligente Gewichtung
    von Transaktionshöhe und -häufigkeit
    """
    
    def __init__(self, lambda_decay: float = 0.05):
        """
        Args:
            lambda_decay: Faktor für exponential decay (jüngere Tage stärker gewichten)
        """
        self.lambda_decay = lambda_decay
        self.small_transaction_threshold = 2000.0  # EUR - normale kleine Transaktionen
        self.bar_threshold = 10000.0  # EUR - Bar-Grenze für Meldepflicht
        self.threshold_avoidance_min = 7000.0  # EUR - Minimum für "nah unter Grenze"
        self.threshold_avoidance_max = 9999.0  # EUR - Maximum für "nah unter Grenze"
        self.smurfing_cumulative_min = 50000.0  # EUR - Minimum kumulative Summe für Smurfing-Verdacht (NEU: 50.000€)
        self.normal_saver_density_weeks = 0.25  # Transaktionen/Woche (1/Monat = normal)
        self.smurfer_density_weeks = 0.5  # Transaktionen/Woche (verdächtig)
        
    def calculate_weight(
        self,
        transactions: List[Transaction],
        window_days: int
    ) -> float:
        """
        Berechnet Weight für ein Zeitfenster
        
        Weight_W = Σ (Ã_tag × F̃_tag)
        - Ã_tag = log(1 + Summe der Beträge pro Tag)
        - F̃_tag = log(1 + Anzahl Transaktionen pro Tag)
        
        Args:
            transactions: Liste von Transaktionen
            window_days: Zeitfenster in Tagen
            
        Returns:
            Weight-Wert
        """
        if not transactions:
            return 0.0
        
        # Transaktionen nach Tag gruppieren
        df = self._transactions_to_dataframe(transactions)
        
        if df.empty:
            return 0.0
        
        # Gruppiere nach Tag
        daily = df.groupby(df['timestamp'].dt.date).agg({
            'transaction_amount': 'sum',
            'transaction_id': 'count'
        }).reset_index()
        
        daily.columns = ['date', 'amount_sum', 'count']
        
        # Log-Transformationen
        daily['A_tilde'] = np.log1p(daily['amount_sum'])  # log(1 + x)
        daily['F_tilde'] = np.log1p(daily['count'])
        
        # Erkenne Transaktionen nah unter der Bar-Grenze und gewichte sie stärker
        # Für jeden Tag: prüfe ob Transaktionen nah unter 10.000€ liegen
        daily['threshold_avoidance_factor'] = 1.0  # Standard-Faktor
        
        # Gruppiere Transaktionen nach Tag für detaillierte Analyse
        for date in daily['date']:
            day_txns = [
                t for t in transactions
                if t.timestamp and t.timestamp.date() == date
            ]
            
            # Prüfe ob Bar-Investments nah unter der Grenze liegen
            bar_investments = [
                t for t in day_txns
                if t.payment_method == "Bar" and t.transaction_type == "investment"
            ]
            
            if bar_investments:
                threshold_avoidance_count = sum(
                    1 for t in bar_investments
                    if self.threshold_avoidance_min <= t.transaction_amount < self.threshold_avoidance_max
                )
                
                # Wenn viele Transaktionen nah unter der Grenze: stärker gewichten
                if threshold_avoidance_count > 0:
                    ratio = threshold_avoidance_count / len(bar_investments)
                    # Faktor: 1.0 (normal) bis 2.5 (alle nah unter Grenze)
                    daily.loc[daily['date'] == date, 'threshold_avoidance_factor'] = 1.0 + (ratio * 1.5)
        
        # Weight pro Tag mit Threshold-Avoidance-Faktor
        daily['weight'] = daily['A_tilde'] * daily['F_tilde'] * daily['threshold_avoidance_factor']
        
        # Exponential Decay: jüngere Tage stärker gewichten
        daily['days_ago'] = daily['date'].apply(lambda x: (datetime.now().date() - x).days)
        daily['decay_factor'] = np.exp(-self.lambda_decay * daily['days_ago'])
        
        # Gesamt-Weight mit Decay
        total_weight = (daily['weight'] * daily['decay_factor']).sum()
        
        return total_weight
    
    def calculate_z_score(
        self,
        current_weight: float,
        historical_transactions: List[Transaction],
        window_days: int
    ) -> float:
        """
        Berechnet Z-Score gegen historische Baseline
        
        z_W = (Weight_W - μ_baseline) / σ_baseline
        
        Args:
            current_weight: Aktueller Weight-Wert
            historical_transactions: Historische Transaktionen (z.B. 12 Monate)
            window_days: Zeitfenster für rollierende Berechnung
            
        Returns:
            Z-Score
        """
        if not historical_transactions:
            return 0.0
        
        # Berechne rollierende Weights für historische Daten
        df = self._transactions_to_dataframe(historical_transactions)
        
        if df.empty:
            return 0.0
        
        # Sortiere nach Datum
        df = df.sort_values('timestamp')
        
        # Berechne Weight für jede mögliche Fensterposition
        historical_weights = []
        
        # Finde ersten und letzten Tag
        min_date = df['timestamp'].min()
        max_date = df['timestamp'].max()
        
        # Für wenige historische Transaktionen: Gruppiere nach Monat
        # Für viele: Erstelle rollierende Fenster
        
        if len(historical_transactions) < 20:
            # Wenige Transaktionen: Gruppiere nach Monat als Baseline
            df['month'] = df['timestamp'].dt.to_period('M')
            for month, group_df in df.groupby('month'):
                # Konvertiere month (Period) zu String für Vergleich
                month_str = str(month)
                month_txns = [
                    t for t in historical_transactions
                    if t.timestamp and pd.to_datetime(t.timestamp).to_period('M') == month
                ]
                if len(month_txns) >= 1:
                    weight = self.calculate_weight(month_txns, window_days)
                    historical_weights.append(weight)
        else:
            # Viele Transaktionen: Rollierende Fenster
            current_date = min_date + timedelta(days=window_days)
            
            while current_date <= max_date:
                window_start = current_date - timedelta(days=window_days)
                window_end = current_date
                
                window_txns = [
                    t for t in historical_transactions
                    if t.timestamp and window_start <= t.timestamp < window_end
                ]
                
                if len(window_txns) >= 2:
                    weight = self.calculate_weight(window_txns, window_days)
                    historical_weights.append(weight)
                
                # Nächstes Fenster (7 Tage später)
                current_date += timedelta(days=7)
        
        if not historical_weights or len(historical_weights) < 2:
            return 0.0
        
        # Berechne Baseline-Statistiken
        mu_baseline = np.mean(historical_weights)
        sigma_baseline = np.std(historical_weights)
        
        # Verhindere Division durch Null
        if sigma_baseline < 0.01:
            sigma_baseline = 0.01
        
        # Z-Score
        z_score = (current_weight - mu_baseline) / sigma_baseline
        
        return z_score
    
    def calculate_small_transaction_ratio(
        self,
        transactions: List[Transaction]
    ) -> float:
        """
        Berechnet Anteil der Kleinbeträge
        
        Args:
            transactions: Liste von Transaktionen
            
        Returns:
            Ratio zwischen 0 und 1
        """
        if not transactions:
            return 0.0
        
        small_count = sum(
            1 for t in transactions
            if t.transaction_amount < self.small_transaction_threshold
        )
        
        return small_count / len(transactions)
    
    def detect_threshold_avoidance(
        self,
        transactions: List[Transaction]
    ) -> Tuple[float, float]:
        """
        Erkennt Transaktionen nah unter der Bar-Grenze (7.000€ - 9.999€)
        
        Args:
            transactions: Liste von Transaktionen (nur Investments)
            
        Returns:
            Tuple (ratio, cumulative_amount)
            - ratio: Anteil der Transaktionen nah unter Grenze
            - cumulative_amount: Kumulative Summe dieser Transaktionen
        """
        if not transactions:
            return 0.0, 0.0
        
        # Nur Bar-Investments betrachten
        bar_investments = [
            t for t in transactions
            if t.payment_method == "Bar" and t.transaction_type == "investment"
        ]
        
        if not bar_investments:
            return 0.0, 0.0
        
        # Transaktionen nah unter der Grenze
        threshold_avoidance_txns = [
            t for t in bar_investments
            if self.threshold_avoidance_min <= t.transaction_amount < self.threshold_avoidance_max
        ]
        
        ratio = len(threshold_avoidance_txns) / len(bar_investments) if bar_investments else 0.0
        cumulative_amount = sum(t.transaction_amount for t in threshold_avoidance_txns)
        
        return ratio, cumulative_amount
    
    def calculate_temporal_density_weeks(
        self,
        transactions: List[Transaction],
        window_days: int
    ) -> float:
        """
        Berechnet temporale Dichte (Transaktionen pro Woche)
        
        NEU: Bezug auf Wochen statt Tage!
        - 0.25 Transaktionen/Woche = 1 Transaktion/Monat (normal)
        - >0.5 Transaktionen/Woche = verdächtig (mehr als 2/Monat)
        - Über 3 Monate verteilt = auch Smurfing möglich
        
        Args:
            transactions: Liste von Transaktionen
            window_days: Zeitfenster in Tagen
            
        Returns:
            Transaktionen pro Woche
        """
        if not transactions or window_days <= 0:
            return 0.0
        
        # Nur Transaktionen mit Timestamp
        txns_with_time = [t for t in transactions if t.timestamp]
        if not txns_with_time:
            return 0.0
        
        # Berechne tatsächliche Zeitspanne
        timestamps = [t.timestamp for t in txns_with_time]
        min_time = min(timestamps)
        max_time = max(timestamps)
        
        actual_days = (max_time - min_time).days + 1  # +1 um Division durch 0 zu vermeiden
        actual_days = max(actual_days, 1)  # Mindestens 1 Tag
        
        # Konvertiere zu Wochen
        actual_weeks = actual_days / 7.0
        
        # Transaktionen pro Woche
        density_weeks = len(txns_with_time) / actual_weeks
        
        return density_weeks
    
    def check_source_of_funds(
        self,
        transactions: List[Transaction],
        customer_info: Optional[CustomerInfo] = None
    ) -> Tuple[bool, float]:
        """
        Prüft ob Source of Funds überschritten wurde
        
        Logik:
        - Wenn SoF definiert: Kumulative Summe aller Investments
        - Wenn kumulative Summe > SoF: überschritten = True
        - Wenn kein SoF: immer False (keine Überschreitung möglich)
        
        Args:
            transactions: Liste von Transaktionen
            customer_info: Kunden-Informationen (Source of Funds)
            
        Returns:
            Tuple (exceeded, cumulative_investments)
        """
        if not customer_info or customer_info.source_of_funds is None:
            return False, 0.0
        
        # Berechne kumulative Summe aller Investments
        investments = [
            t for t in transactions
            if t.transaction_type.value == "investment"
        ]
        cumulative_investments = sum(t.transaction_amount for t in investments)
        
        exceeded = cumulative_investments > customer_info.source_of_funds
        
        return exceeded, cumulative_investments
    
    def check_economic_plausibility(
        self,
        transactions: List[Transaction],
        customer_info: Optional[CustomerInfo] = None
    ) -> bool:
        """
        Prüft Economic Plausibility
        
        Logik:
        - Wenn monatliches Einkommen bekannt ist
        - Und mehrere Transaktionen nah unter der Grenze (7.000€ - 9.999€)
        - Dann: Ist das realistisch durch Ersparnisse erklärbar?
        
        Beispiel:
        - Einkommen: 2.500€/Monat
        - 3× 9.900€ Einzahlungen = 29.700€
        - Das entspricht ~12 Monatsgehältern
        - Unrealistisch ohne SoF!
        
        Args:
            transactions: Liste von Transaktionen
            customer_info: Kunden-Informationen (Monthly Income)
            
        Returns:
            True wenn Economic Plausibility Problem erkannt
        """
        if not customer_info or customer_info.monthly_income is None:
            return False
        
        # Prüfe nur Bar-Investments nah unter der Grenze
        bar_investments = [
            t for t in transactions
            if t.payment_method.value == "Bar" and t.transaction_type.value == "investment"
        ]
        
        threshold_avoidance_txns = [
            t for t in bar_investments
            if self.threshold_avoidance_min <= t.transaction_amount < self.threshold_avoidance_max
        ]
        
        if len(threshold_avoidance_txns) < 3:
            return False  # Zu wenige Transaktionen
        
        # Kumulative Summe der Transaktionen nah unter Grenze
        cumulative_threshold_amount = sum(t.transaction_amount for t in threshold_avoidance_txns)
        
        # Prüfe: Ist das realistisch durch Ersparnisse erklärbar?
        # Regel: Mehr als 6 Monatsgehälter ohne SoF = unrealistisch
        monthly_income = customer_info.monthly_income
        max_plausible_savings = monthly_income * 6  # 6 Monate Ersparnisse
        
        if cumulative_threshold_amount > max_plausible_savings:
            # Unrealistisch: Mehr als 6 Monatsgehälter ohne SoF
            return True
        
        return False
    
    def analyze(
        self,
        recent_transactions: List[Transaction],
        historical_transactions: List[Transaction],
        customer_info: Optional[CustomerInfo] = None
    ) -> WeightAnalysis:
        """
        Vollständige Weight-Analyse mit verbesserter Smurfing-Erkennung
        
        Args:
            recent_transactions: Aktuelle Transaktionen
            historical_transactions: Historische Transaktionen für Baseline
            
        Returns:
            WeightAnalysis Objekt
        """
        # Berechne Weights für verschiedene Zeitfenster
        weight_7d = self.calculate_weight(recent_transactions, 7)
        weight_30d = self.calculate_weight(recent_transactions, 30)
        weight_90d = self.calculate_weight(recent_transactions, 90)
        
        # Berechne Z-Scores
        z_score_7d = self.calculate_z_score(weight_7d, historical_transactions, 7)
        z_score_30d = self.calculate_z_score(weight_30d, historical_transactions, 30)
        z_score_90d = self.calculate_z_score(weight_90d, historical_transactions, 90)
        
        # Berechne Kleinbetrags-Ratio
        small_ratio = self.calculate_small_transaction_ratio(recent_transactions)
        
        # NEUE METRIKEN: Threshold-Avoidance (nah unter Bar-Grenze)
        threshold_avoidance_ratio, cumulative_large_amount = self.detect_threshold_avoidance(recent_transactions)
        
        # NEUE METRIK: Temporale Dichte auf Wochen (statt Tage!)
        temporal_density_weeks = self.calculate_temporal_density_weeks(recent_transactions, 90)  # 90 Tage = ~13 Wochen
        
        # Source of Funds Prüfung
        source_of_funds_exceeded, cumulative_investments = self.check_source_of_funds(recent_transactions, customer_info)
        
        # Economic Plausibility Prüfung
        economic_plausibility_issue = self.check_economic_plausibility(recent_transactions, customer_info)
        
        # VERBESSERTE SMURFING-ERKENNUNG mit Source of Funds Integration:
        # 
        # WICHTIG: Source of Funds Logik
        # - Wenn SoF definiert UND kumulative Summe < SoF: Weight-System greift NICHT (nur andere Systeme)
        # - Wenn SoF definiert UND kumulative Summe > SoF: verdächtig!
        # - Wenn kein SoF: einzelne Transaktionen OK, aber mehrere über Jahr = verdächtig
        #
        # Smurfer: 
        # 1. Viele Transaktionen nah unter der Bar-Grenze (7.000€ - 9.999€)
        # 2. Große kumulative Summe (> 50.000€) - NEU: 50.000€ statt 20.000€
        # 3. Hohe temporale Dichte (> 0.25 Transaktionen/Woche) - NEU: auf Wochen bezogen
        # 4. Über 3 Monate verteilt = auch Smurfing möglich
        # 5. Source of Funds überschritten ODER kein SoF + Economic Plausibility Problem
        #
        # Normale Sparer:
        # - Niedrige temporale Dichte (< 0.25 Transaktionen/Woche = 1/Monat)
        # - Kleine Beträge über lange Zeit
        # - KEINE Transaktionen nah unter der Grenze
        # - SoF nicht überschritten (wenn definiert)
        
        is_suspicious = False
        
        # WICHTIG: Wenn SoF definiert UND unterhalb: Weight-System greift NICHT
        if customer_info and customer_info.source_of_funds is not None:
            if not source_of_funds_exceeded:
                # Unterhalb SoF: Weight-System greift NICHT
                # Nur andere Systeme (Entropie, Trust Score, etc.) greifen
                is_suspicious = False
            else:
                # Oberhalb SoF: verdächtig!
                is_suspicious = True
        
        # Wenn kein SoF oder SoF überschritten: normale Smurfing-Erkennung
        if customer_info is None or customer_info.source_of_funds is None or source_of_funds_exceeded:
            # ==========================================
            # ABSOLUTE SCHWELLENWERTE (Primär-Erkennung)
            # ==========================================
            # Diese funktionieren IMMER, auch ohne historische Daten
            # und erkennen auch "chronische" Smurfer
            
            # PRIORITÄT 1: Threshold-Avoidance (nah unter Bar-Grenze) - STARKER INDIKATOR
            # Absolute Schwellenwerte: funktioniert ohne historische Baseline
            # GELOCKERT: threshold_avoidance_ratio von 0.5 auf 0.3, cumulative von 50k auf 30k
            if threshold_avoidance_ratio >= 0.3:  # Mindestens 30% der Bar-Investments nah unter Grenze (war 50%)
                if cumulative_large_amount >= 30000:  # Kumulative Summe > 30.000€ (war 50.000€)
                    if temporal_density_weeks > self.normal_saver_density_weeks:  # > 0.25 Transaktionen/Woche
                        is_suspicious = True
            
            # PRIORITÄT 2: Viele Transaktionen nah unter Grenze + hohe Dichte
            # Absolute Schwellenwerte: funktioniert ohne historische Baseline
            # GELOCKERT: threshold_avoidance_ratio von 0.7 auf 0.5
            if threshold_avoidance_ratio >= 0.5 and temporal_density_weeks > self.smurfer_density_weeks:  # war 0.7
                is_suspicious = True
            
            # PRIORITÄT 3: Economic Plausibility Problem
            # Absolute Schwellenwerte: funktioniert ohne historische Baseline
            if economic_plausibility_issue:
                # Unrealistisch: Mehr als 6 Monatsgehälter ohne SoF
                is_suspicious = True
            
            # PRIORITÄT 4: Mehrere Transaktionen über Jahr verteilt ohne SoF
            # Absolute Schwellenwerte: funktioniert ohne historische Baseline
            # GELOCKERT: threshold_avoidance_ratio von 0.5 auf 0.3, cumulative von 50k auf 30k
            if customer_info is None or customer_info.source_of_funds is None:
                # Kein SoF abgegeben
                if len(recent_transactions) >= 12:  # Über Jahr verteilt
                    if threshold_avoidance_ratio >= 0.3 and cumulative_large_amount >= 30000:  # war 0.5 und 50k
                        # Mehrere Transaktionen nah unter Grenze über Jahr = verdächtig
                        is_suspicious = True
            
            # ==========================================
            # RELATIVE SCHWELLENWERTE (Sekundär-Erkennung)
            # ==========================================
            # Diese erkennen ÄNDERUNGEN im Verhalten (nur wenn historische Daten vorhanden)
            
            # PRIORITÄT 5: Sehr hoher Z-Score (plötzliche massive Änderung)
            if z_score_30d >= 3.5:  # Erhöht von 3.0 auf 3.5 (nur extreme Änderungen)
                # Sehr hoher Z-Score - plötzliche massive Änderung
                is_suspicious = True
            elif z_score_30d >= 2.5:  # Erhöht von 2.0 auf 2.5
                # Moderater Z-Score - nur verdächtig wenn auch absolute Indikatoren vorhanden
                if threshold_avoidance_ratio >= 0.3 or cumulative_large_amount >= self.smurfing_cumulative_min:
                    is_suspicious = True
            
            # AUSSCHLUSS: Normale Sparer - niedrige Dichte + kleine Beträge + KEINE Threshold-Avoidance
            # Absolute Schwellenwerte: funktioniert ohne historische Baseline
            if not is_suspicious:  # Nur prüfen wenn noch nicht verdächtig
                if temporal_density_weeks < self.normal_saver_density_weeks and small_ratio > 0.8:
                    # Normales Sparverhalten - weniger verdächtig
                    if threshold_avoidance_ratio < 0.3:  # Wenige oder keine Transaktionen nah unter Grenze
                        # Reduziere Verdacht wenn keine Threshold-Avoidance
                        if cumulative_large_amount < self.smurfing_cumulative_min:
                            # Keine große kumulative Summe nah unter Grenze
                            # Normale Sparer: niedrige Dichte + kleine Beträge = unverdächtig
                            is_suspicious = False
        
        return WeightAnalysis(
            weight_7d=weight_7d,
            weight_30d=weight_30d,
            weight_90d=weight_90d,
            z_score_7d=z_score_7d,
            z_score_30d=z_score_30d,
            z_score_90d=z_score_90d,
            is_suspicious=is_suspicious,
            small_transaction_ratio=small_ratio,
            threshold_avoidance_ratio=threshold_avoidance_ratio,
            cumulative_large_amount=cumulative_large_amount,
            temporal_density_weeks=temporal_density_weeks,
            source_of_funds_exceeded=source_of_funds_exceeded,
            economic_plausibility_issue=economic_plausibility_issue
        )
    
    def _transactions_to_dataframe(self, transactions: List[Transaction]) -> pd.DataFrame:
        """Konvertiert Transaktionsliste zu DataFrame"""
        if not transactions:
            return pd.DataFrame()
        
        data = []
        for t in transactions:
            # Wenn kein Timestamp, setze aktuelles Datum
            ts = t.timestamp if t.timestamp else datetime.now()
            data.append({
                'transaction_id': t.transaction_id,
                'transaction_amount': t.transaction_amount,
                'timestamp': ts
            })
        
        df = pd.DataFrame(data)
        df['timestamp'] = pd.to_datetime(df['timestamp'])
        
        return df

