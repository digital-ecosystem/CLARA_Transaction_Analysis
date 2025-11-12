"""
Hilfsskript zum Ändern des Git-Accounts
"""
import subprocess
import sys

print("="*80)
print("GIT-ACCOUNT ÄNDERN")
print("="*80)

print("\n[1] Aktuelle Konfiguration:")
print("-" * 80)
result = subprocess.run(["git", "config", "--get", "user.name"], capture_output=True, text=True)
print(f"  User Name: {result.stdout.strip() if result.returncode == 0 else 'Nicht gesetzt'}")

result = subprocess.run(["git", "config", "--get", "user.email"], capture_output=True, text=True)
print(f"  User Email: {result.stdout.strip() if result.returncode == 0 else 'Nicht gesetzt'}")

result = subprocess.run(["git", "remote", "get-url", "origin"], capture_output=True, text=True)
print(f"  Remote URL: {result.stdout.strip() if result.returncode == 0 else 'Nicht gesetzt'}")

print("\n" + "="*80)
print("ANLEITUNG ZUM ÄNDERN:")
print("="*80)

print("\n[1] Git User Name & Email ändern (lokal für dieses Repository):")
print("-" * 80)
print("  git config user.name \"Dein Name\"")
print("  git config user.email \"deine.email@example.com\"")
print("\n  Oder global (für alle Repositories):")
print("  git config --global user.name \"Dein Name\"")
print("  git config --global user.email \"deine.email@example.com\"")

print("\n[2] Remote URL ändern (zu anderem GitHub-Account):")
print("-" * 80)
print("  git remote set-url origin https://github.com/DEIN_USERNAME/CLARA_Transaction_Analysis.git")
print("\n  Oder Remote entfernen und neu hinzufügen:")
print("  git remote remove origin")
print("  git remote add origin https://github.com/DEIN_USERNAME/CLARA_Transaction_Analysis.git")

print("\n[3] Beispiel-Kommandos:")
print("-" * 80)
print("  # Zu persönlichem Account ändern:")
print("  git remote set-url origin https://github.com/portohan/CLARA_Transaction_Analysis.git")
print("\n  # User Name ändern:")
print("  git config user.name \"Porto Han\"")
print("\n  # User Email ändern:")
print("  git config user.email \"kolesanton98@gmail.com\"")

print("\n" + "="*80)
print("WICHTIG:")
print("="*80)
print("  - User Name/Email beeinflussen nur die Commit-Autoren")
print("  - Remote URL bestimmt, wohin gepusht wird")
print("  - Stelle sicher, dass das Repository auf GitHub existiert")
print("  - Verwende Personal Access Token für Authentifizierung")



