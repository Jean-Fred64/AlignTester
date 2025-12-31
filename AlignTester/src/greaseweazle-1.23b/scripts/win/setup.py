from cx_Freeze import setup, Executable

# Windows 32-bit build: We need to explicitly point at the 32-bit DLLs early.
import sys, os

# Forcer UTF-8 pour éviter les problèmes d'encodage
import io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

# Ajouter le chemin vers src/ au PYTHONPATH pour que cx_Freeze puisse trouver greaseweazle
# setup.py est dans scripts/win/, donc on remonte de 2 niveaux puis on va dans src/
script_dir = os.path.dirname(os.path.abspath(__file__))
src_dir = os.path.join(script_dir, '..', '..', 'src')
if src_dir not in sys.path:
    sys.path.insert(0, src_dir)

if sys.maxsize <= 2**32:
    new_paths = ['C:\\Windows\\SysWOW64\\downlevel']
    old_paths = os.environ['PATH'].split(os.pathsep)
    os.environ['PATH'] = os.pathsep.join(new_paths + old_paths)
    bin_path_includes = new_paths
else:
    bin_path_includes = []

buildOptions = dict(
    packages = ['greaseweazle', 'bitarray', 'crcmod'],
    includes = ['requests', 'serial', 'serial.tools.list_ports'],
    excludes = ['tkinter', 'test', 'distutils'],
    bin_path_includes = bin_path_includes,
    include_msvcr = True)

base = 'Console'

executables = [
    Executable('gw.py', base=base)
]

setup(name='Greaseweazle',
      options = dict(build_exe = buildOptions),
      executables = executables)
