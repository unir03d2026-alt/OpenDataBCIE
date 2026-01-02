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