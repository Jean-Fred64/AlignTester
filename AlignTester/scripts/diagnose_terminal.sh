#!/bin/bash
# Script de diagnostic du terminal - Comparaison avec projet fonctionnel
# Basé sur RAPPORT_DIAGNOSTIC_TERMINAL.md

echo "🔍 Diagnostic Terminal Cursor - Projet Aligntester"
echo "=================================================="
echo ""

# 1. Informations système de base
echo "=== 1. Informations système ==="
uname -a
echo ""
whoami
echo ""
id
echo ""
pwd
echo ""

# 2. Vérification du shell
echo "=== 2. Vérification shell ==="
echo "SHELL=$SHELL"
if [ -n "$SHELL" ]; then
    which $SHELL 2>/dev/null || echo "⚠️  SHELL ($SHELL) non trouvé dans PATH"
else
    echo "⚠️  SHELL non défini"
fi
which bash 2>/dev/null || echo "⚠️  bash non trouvé"
if command -v bash &> /dev/null; then
    bash --version | head -1
    test -x $(which bash) && echo "✅ bash est exécutable" || echo "❌ bash NON exécutable"
else
    echo "❌ bash non disponible"
fi
echo ""

# 3. Variables d'environnement
echo "=== 3. Variables d'environnement ==="
echo "HOME=$HOME"
echo "USER=$USER"
echo "PATH=$PATH"
echo "TERM=$TERM"
echo ""

# 4. Permissions du répertoire
echo "=== 4. Permissions répertoire ==="
ls -ld .
test -r . && echo "✅ Lecture OK" || echo "❌ Lecture ÉCHEC"
test -w . && echo "✅ Écriture OK" || echo "❌ Écriture ÉCHEC"
test -x . && echo "✅ Exécution OK" || echo "❌ Exécution ÉCHEC"
echo ""

# 5. Test de commandes simples
echo "=== 5. Tests de commandes ==="
pwd
ls -la | head -5
echo "Test $(date)"
echo ""

# 6. Vérifications spécifiques Cursor
echo "=== 6. Vérifications Cursor ==="
echo "Chemins Cursor dans PATH:"
echo $PATH | grep -o '/home/[^:]*cursor[^:]*' || echo "⚠️  Aucun chemin Cursor trouvé dans PATH"
echo ""

if [ -d ~/.cursor-server ]; then
    echo "✅ Répertoire .cursor-server existe"
    ls -ld ~/.cursor-server 2>/dev/null | head -1
else
    echo "⚠️  Répertoire .cursor-server non trouvé"
fi
echo ""

# 7. Vérifications WSL
echo "=== 7. Vérifications WSL ==="
if [ -f /proc/version ]; then
    echo "Version du kernel:"
    cat /proc/version
    echo ""
fi

if [ -d /mnt/c ]; then
    echo "✅ Montage Windows accessible:"
    ls /mnt/c | head -5
else
    echo "⚠️  Montage Windows non accessible"
fi
echo ""

# 8. Configuration .vscode
echo "=== 8. Configuration projet ==="
if [ -f .vscode/settings.json ]; then
    echo "✅ Fichier .vscode/settings.json existe"
    echo "Contenu (extrait terminal):"
    grep -E "(terminal|defaultProfile|automationProfile)" .vscode/settings.json || echo "Aucune config terminal trouvée"
else
    echo "⚠️  Fichier .vscode/settings.json non trouvé"
fi
echo ""

# 9. Comparaison avec projet fonctionnel
echo "=== 9. Comparaison avec projet Pauline (fonctionnel) ==="
echo "Répertoire actuel: $(pwd)"
echo "Répertoire attendu fonctionnel: /home/jean-fred/Pauline"
echo ""
echo "Chemin du workspace:"
echo "  Actuel: $(pwd)"
echo "  Format: $(echo $(pwd) | grep -q '^/' && echo 'Chemin Linux normal' || echo 'Autre format')"
echo ""

# 10. Résumé
echo "=== 10. Résumé ==="
echo "✅ Points OK:"
[ -n "$HOME" ] && echo "  - HOME défini"
[ -n "$USER" ] && echo "  - USER défini"
command -v bash &> /dev/null && echo "  - bash disponible"
[ -r . ] && echo "  - Répertoire lisible"
[ -w . ] && echo "  - Répertoire accessible en écriture"
echo ""
echo "⚠️  Points à vérifier:"
[ -z "$SHELL" ] && echo "  - SHELL non défini"
[ ! -x "$(which bash 2>/dev/null)" ] && echo "  - bash non exécutable"
echo ""
echo "📋 Pour comparer avec le projet fonctionnel (Pauline):"
echo "   Voir: RAPPORT_DIAGNOSTIC_TERMINAL.md"
echo ""

