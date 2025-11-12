"""
Erstellt eine CSV mit allen Trades und Analyse-Ergebnissen
"""
import pandas as pd
import io
from datetime import datetime
from models import Transaction, PaymentMethod, TransactionType, RiskLevel
from analyzer import TransactionAnalyzer

def create_analyzed_csv(input_csv_path: str, output_csv_path: str = None):
    """
    Erstellt eine CSV mit allen Trades und Analyse-Ergebnissen
    
    Args:
        input_csv_path: Pfad zur ursprünglichen CSV
        output_csv_path: Pfad zur Ausgabe-CSV (optional)
    """
    print("="*80)
    print("ERSTELLE ANALYSIERTE CSV")
    print("="*80)
    
    # 1. Lese ursprüngliche CSV
    print(f"\n1. Lese CSV: {input_csv_path}")
    with open(input_csv_path, 'rb') as f:
        contents = f.read()
    df_original = pd.read_csv(io.StringIO(contents.decode('windows-1252')))
    
    print(f"   Gesamt Transaktionen: {len(df_original)}")
    
    # 2. Parse Transaktionen
    print("\n2. Parse Transaktionen für Analyse...")
    name_col = [col for col in df_original.columns if 'Name' in col][0]
    
    all_transactions = []
    for idx, row in df_original.iterrows():
        try:
            customer_id = str(row['Kundennummer'])
            transaction_id = str(row['Unique Transaktion ID'])
            customer_name = str(row[name_col])
            
            art = str(row['Art']).strip()
            if art == "Bar":
                payment_method = PaymentMethod.BAR
            elif art == "SEPA":
                payment_method = PaymentMethod.SEPA
            else:
                payment_method = PaymentMethod.KREDITKARTE
            
            in_out = str(row['In/Out']).strip()
            if in_out == "In":
                transaction_type = TransactionType.INVESTMENT
            elif in_out == "Out":
                transaction_type = TransactionType.AUSZAHLUNG
            else:
                transaction_type = TransactionType.INVESTMENT
            
            amount_str = str(row['Auftragsvolumen']).replace(',', '.')
            transaction_amount = float(amount_str)
            
            timestamp = None
            if 'Timestamp' in df_original.columns and pd.notna(row['Timestamp']):
                try:
                    date_str = str(row['Timestamp'])
                    timestamp = pd.to_datetime(date_str, format='%d.%m.%Y')
                except:
                    timestamp = None
            
            txn = Transaction(
                customer_id=customer_id,
                transaction_id=transaction_id,
                customer_name=customer_name,
                transaction_amount=transaction_amount,
                payment_method=payment_method,
                transaction_type=transaction_type,
                timestamp=timestamp
            )
            all_transactions.append(txn)
        except Exception as e:
            continue
    
    print(f"   Transaktionen geparst: {len(all_transactions)}")
    
    # 3. Analysiere alle Kunden
    print("\n3. Analysiere alle Kunden...")
    custom_analyzer = TransactionAnalyzer(alpha=0.6, beta=0.4, historical_days=1825)
    custom_analyzer.add_transactions(all_transactions)
    
    profiles = custom_analyzer.analyze_all_customers(recent_days=1825)
    
    print(f"   Kunden analysiert: {len(profiles)}")
    
    # 4. Erstelle Mapping von Customer ID zu Analyse-Ergebnis
    print("\n4. Erstelle Mapping...")
    customer_analysis = {}
    for profile in profiles:
        customer_id = int(profile.customer_id)
        
        # Erstelle Flag-String
        flags_str = "; ".join(profile.flags) if profile.flags else ""
        
        customer_analysis[customer_id] = {
            'Risk_Level': profile.risk_level.value,
            'Suspicion_Score': round(profile.suspicion_score, 2),
            'Flags': flags_str,
            'Threshold_Avoidance_Ratio': round(profile.weight_analysis.threshold_avoidance_ratio * 100, 1) if profile.weight_analysis else 0.0,
            'Cumulative_Large_Amount': round(profile.weight_analysis.cumulative_large_amount, 2) if profile.weight_analysis else 0.0,
            'Temporal_Density_Weeks': round(profile.weight_analysis.temporal_density_weeks, 2) if profile.weight_analysis else 0.0,
            'Layering_Score': round(profile.statistical_analysis.layering_score, 2) if profile.statistical_analysis else 0.0,
            'Entropy_Complex': 'Ja' if profile.entropy_analysis.is_complex else 'Nein',
            'Trust_Score': round(profile.trust_score_analysis.current_score, 2) if profile.trust_score_analysis else 0.0,
        }
    
    # 5. Füge Analyse-Ergebnisse zur ursprünglichen CSV hinzu
    print("\n5. Füge Analyse-Ergebnisse hinzu...")
    
    # Erstelle neue Spalten
    df_result = df_original.copy()
    
    df_result['Risk_Level'] = df_result['Kundennummer'].apply(
        lambda x: customer_analysis.get(x, {}).get('Risk_Level', 'UNKNOWN')
    )
    df_result['Suspicion_Score'] = df_result['Kundennummer'].apply(
        lambda x: customer_analysis.get(x, {}).get('Suspicion_Score', 0.0)
    )
    df_result['Flags'] = df_result['Kundennummer'].apply(
        lambda x: customer_analysis.get(x, {}).get('Flags', '')
    )
    df_result['Threshold_Avoidance_Ratio_%'] = df_result['Kundennummer'].apply(
        lambda x: customer_analysis.get(x, {}).get('Threshold_Avoidance_Ratio', 0.0)
    )
    df_result['Cumulative_Large_Amount'] = df_result['Kundennummer'].apply(
        lambda x: customer_analysis.get(x, {}).get('Cumulative_Large_Amount', 0.0)
    )
    df_result['Temporal_Density_Weeks'] = df_result['Kundennummer'].apply(
        lambda x: customer_analysis.get(x, {}).get('Temporal_Density_Weeks', 0.0)
    )
    df_result['Layering_Score'] = df_result['Kundennummer'].apply(
        lambda x: customer_analysis.get(x, {}).get('Layering_Score', 0.0)
    )
    df_result['Entropy_Complex'] = df_result['Kundennummer'].apply(
        lambda x: customer_analysis.get(x, {}).get('Entropy_Complex', 'Nein')
    )
    df_result['Trust_Score'] = df_result['Kundennummer'].apply(
        lambda x: customer_analysis.get(x, {}).get('Trust_Score', 0.0)
    )
    
    # 6. Speichere erweiterte CSV
    if output_csv_path is None:
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        output_csv_path = f"Analyzed_Trades_{timestamp}.csv"
    
    print(f"\n6. Speichere erweiterte CSV: {output_csv_path}")
    
    # Speichere mit UTF-8 BOM für bessere Excel-Kompatibilität
    df_result.to_csv(output_csv_path, index=False, encoding='utf-8-sig', sep=';')
    
    print(f"   Datei gespeichert: {output_csv_path}")
    print(f"   Zeilen: {len(df_result)}")
    print(f"   Spalten: {len(df_result.columns)}")
    
    # 7. Statistiken
    print("\n7. Statistiken:")
    risk_counts = df_result['Risk_Level'].value_counts()
    for risk_level, count in risk_counts.items():
        # Zähle eindeutige Kunden pro Risk Level
        unique_customers = df_result[df_result['Risk_Level'] == risk_level]['Kundennummer'].nunique()
        print(f"   {risk_level}: {unique_customers} Kunden ({count} Transaktionen)")
    
    print("\n" + "="*80)
    print("FERTIG!")
    print("="*80)
    print(f"\nDie analysierte CSV wurde erstellt: {output_csv_path}")
    print("\nNeue Spalten:")
    print("  - Risk_Level: GREEN/YELLOW/ORANGE/RED")
    print("  - Suspicion_Score: Verdachts-Score (0-5+)")
    print("  - Flags: Erkannte Probleme (Smurfing, Geldwäsche, etc.)")
    print("  - Threshold_Avoidance_Ratio_%: % Transaktionen nahe Grenze")
    print("  - Cumulative_Large_Amount: Kumulativer Betrag")
    print("  - Temporal_Density_Weeks: Transaktionen pro Woche")
    print("  - Layering_Score: Geldwäsche-Bewertung")
    print("  - Entropy_Complex: Hohe Komplexität (Ja/Nein)")
    print("  - Trust_Score: Vertrauens-Score")
    
    return output_csv_path


if __name__ == "__main__":
    # Standard-Pfad zur CSV
    input_csv = r"D:\My Progs\CLARA\Black Box\Trades_20251110_143922.csv"
    
    # Erstelle analysierte CSV
    output_csv = create_analyzed_csv(input_csv)
    
    print(f"\n\nÖffnen Sie die Datei in Excel:")
    print(f"  {output_csv}")

