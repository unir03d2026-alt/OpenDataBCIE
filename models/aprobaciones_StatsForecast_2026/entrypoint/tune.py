import argparse
import sys
from pathlib import Path

# Agregar raíz al path
sys.path.append(str(Path(__file__).resolve().parents[1]))

from src.pipelines.tuning_pipeline import run_tuning

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--config", type=str, default="config/local.yaml")
    args = parser.parse_args()
    
    print("⚠️  ATENCIÓN: Este proceso puede tardar varios minutos dependiendo de tu CPU.")
    run_tuning(args.config)