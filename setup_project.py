import os
from pathlib import Path

# --- CONFIGURACIÓN DEL PROYECTO ---
BASE_PATH = Path(r"D:\BCIE\Datos-Abiertos-BCIE")
PROJECT_NAME = "aprobaciones_prophet_2026"
PROJECT_DIR = BASE_PATH / PROJECT_NAME

def create_structure():
    # 1. Definición de directorios
    dirs = [
        PROJECT_DIR / "config",
        PROJECT_DIR / "data" / "01-raw",
        PROJECT_DIR / "data" / "02-preprocessed",
        PROJECT_DIR / "data" / "03-features",
        PROJECT_DIR / "data" / "04-predictions",
        PROJECT_DIR / "entrypoint",
        PROJECT_DIR / "notebooks",
        PROJECT_DIR / "src" / "pipelines",
        PROJECT_DIR / "tests",
        PROJECT_DIR / "logs"
    ]

    for d in dirs:
        os.makedirs(d, exist_ok=True)
        print(f"[OK] Directorio creado: {d}")

    # 2. Creación de archivos base
    files = {
        PROJECT_DIR / "README.md": f"# {PROJECT_NAME}\n\nProyecto de forecasting de aprobaciones usando Prophet (2026-2030).",
        
        PROJECT_DIR / ".gitignore": "data/\n__pycache__/\n.env\n.ipynb_checkpoints/\nlogs/\n",
        
        PROJECT_DIR / "requirements.txt": "pandas\nnumpy\nprophet\nscikit-learn\npyyaml\nmatplotlib\npytest\n",
        
        PROJECT_DIR / "config" / "local.yaml": """
model:
  name: "prophet_bcie_v1"
  seasonality_mode: "multiplicative"
  yearly_seasonality: true
data:
  raw_path: "data/01-raw/aprobaciones.csv"
  processed_path: "data/02-preprocessed/"
forecast:
  horizon_years: 5
""",
        
        PROJECT_DIR / "entrypoint" / "train.py": """
import argparse
import sys
from pathlib import Path
sys.path.append(str(Path(__file__).resolve().parents[1]))
from src.pipelines.training_pipeline import run_training

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--config", type=str, default="config/local.yaml")
    args = parser.parse_args()
    run_training(args.config)
""",
        
        PROJECT_DIR / "src" / "__init__.py": "",
        PROJECT_DIR / "src" / "utils.py": "import yaml\n\ndef load_config(path):\n    with open(path, 'r') as f:\n        return yaml.safe_load(f)",
        
        PROJECT_DIR / "src" / "pipelines" / "__init__.py": "",
        PROJECT_DIR / "src" / "pipelines" / "training_pipeline.py": "def run_training(config_path):\n    print(f'Iniciando entrenamiento con {config_path}')\n    # Logica de Prophet aqui\n    pass",
        PROJECT_DIR / "src" / "pipelines" / "inference_pipeline.py": "",
        PROJECT_DIR / "src" / "pipelines" / "feature_eng_pipeline.py": "",
        
        PROJECT_DIR / "tests" / "__init__.py": "",
        PROJECT_DIR / "tests" / "test_model.py": "def test_dummy():\n    assert True"
    }

    for path, content in files.items():
        if not path.exists():
            with open(path, "w", encoding="utf-8") as f:
                f.write(content.strip())
            print(f"[OK] Archivo creado: {path.name}")
        else:
            print(f"[SKIP] El archivo ya existe: {path.name}")

if __name__ == "__main__":
    print(f"--- Iniciando configuración en: {PROJECT_DIR} ---")
    create_structure()
    print("--- Estructura completada exitosamente ---")