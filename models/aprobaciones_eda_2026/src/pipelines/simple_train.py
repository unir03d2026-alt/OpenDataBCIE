
print("Loading simple_train module...")
import sys
import os
sys.path.append(os.path.join(os.getcwd(), 'src'))
try:
    from utils.gower_dist import compute_gower_distance
    print("Import successful!")
except ImportError as e:
    print(f"Import failed: {e}")

def train_mixed_clustering(config):
    print("Training started (dummy)")
