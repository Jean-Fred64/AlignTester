# Installation de MinGW-w64 pour la compilation Windows

## 📋 Vue d'ensemble

Pour compiler la version Windows de Greaseweazle depuis Linux avec Nuitka, vous devez installer **MinGW-w64** (compilateur cross-compilation pour Windows).

## 🚀 Installation rapide

### Ubuntu/Debian

```bash
sudo apt update
sudo apt install -y mingw-w64
```

### Fedora

```bash
sudo dnf install -y mingw64-gcc
```

### Vérification

Après installation, vérifiez que MinGW est disponible :

```bash
x86_64-w64-mingw32-gcc --version
```

Vous devriez voir quelque chose comme :
```
x86_64-w64-mingw32-gcc (GCC) 12.x.x
```

## ✅ Une fois installé

Vous pouvez lancer la compilation :

```bash
cd /home/jean-fred/Aligntester/AlignTester
./scripts/build_windows_nuitka.sh
```

## 📝 Notes

- MinGW-w64 est nécessaire uniquement pour la cross-compilation Windows
- Pour la compilation Linux native, vous n'avez besoin que de GCC standard
- L'installation prend généralement quelques minutes

