import sys
from pathlib import Path

# Permite ejecutar el proyecto directamente sin haber instalado el paquete
ROOT = Path(__file__).resolve().parent
SRC = ROOT / "src"
if SRC.exists():
    sys.path.insert(0, str(SRC))

from gimnasio.app import main


if __name__ == "__main__":
    main()
