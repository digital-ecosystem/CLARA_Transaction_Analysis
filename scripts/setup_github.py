"""
Hilfsskript für GitHub Setup
"""
import subprocess
import sys

print("="*80)
print("GITHUB REPOSITORY SETUP")
print("="*80)

print("\n[1] Prüfe Git-Status...")
result = subprocess.run(["git", "status"], capture_output=True, text=True)
if result.returncode == 0:
    print("  [OK] Git Repository initialisiert")
else:
    print("  [FEHLER] Git nicht initialisiert")
    print("  Führe aus: git init")

print("\n[2] Prüfe Remote-URL...")
result = subprocess.run(["git", "remote", "-v"], capture_output=True, text=True)
if result.returncode == 0:
    print(result.stdout)
    if "digital-ecosystem/CLARA_Transaction_Analysis" in result.stdout:
        print("  [INFO] Remote-URL konfiguriert")
    else:
        print("  [WARNUNG] Remote-URL nicht gefunden")
else:
    print("  [FEHLER] Konnte Remote nicht prüfen")

print("\n" + "="*80)
print("NÄCHSTE SCHRITTE:")
print("="*80)
print("\n1. Repository auf GitHub erstellen:")
print("   - Gehe zu: https://github.com/organizations/digital-ecosystem/repositories/new")
print("   - Oder: https://github.com/new (für persönliches Repository)")
print("   - Name: CLARA_Transaction_Analysis")
print("   - Beschreibung: CLARA Transaction Analysis System - AML/KYC Compliance Tool")
print("   - Visibility: Private oder Public")
print("   - NICHT: README, .gitignore, License hinzufügen (bereits vorhanden)")
print("   - Klicke 'Create repository'")
print("\n2. Nach Repository-Erstellung:")
print("   - Führe aus: git push -u origin main")
print("   - Bei Authentifizierung: Verwende Personal Access Token")
print("\n3. Falls Repository bereits existiert aber Zugriff fehlt:")
print("   - Prüfe ob du Mitglied der 'digital-ecosystem' Organisation bist")
print("   - Oder ändere Remote-URL zu deinem persönlichen Account:")
print("     git remote set-url origin https://github.com/DEIN_USERNAME/CLARA_Transaction_Analysis.git")
print("\n4. Personal Access Token erstellen (falls nötig):")
print("   - Gehe zu: https://github.com/settings/tokens")
print("   - Klicke 'Generate new token (classic)'")
print("   - Scopes: repo (vollständiger Zugriff)")
print("   - Kopiere Token und verwende als Passwort beim Push")



