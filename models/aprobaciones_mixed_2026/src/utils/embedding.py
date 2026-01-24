import numpy as np
import pandas as pd
from sklearn.manifold import MDS
import logging

logger = logging.getLogger(__name__)

def generate_embedding(distance_matrix, random_state=42):
    """
    Generates a 2D embedding from a precomputed distance matrix using MDS.
    
    Args:
        distance_matrix (np.array): NxN distance matrix (e.g. Gower).
        random_state (int): Seed for reproducibility.
        
    Returns:
        pd.DataFrame: DataFrame with 'x' and 'y' columns.
    """
    logger.info("Generating 2D embedding using MDS (Metric Multidimensional Scaling)...")
    
    try:
        mds = MDS(
            n_components=2, 
            metric=True, 
            dissimilarity='precomputed', 
            random_state=random_state,
            n_init=4,
            max_iter=300
        )
        
        embedding = mds.fit_transform(distance_matrix)
        
        df_embedding = pd.DataFrame(embedding, columns=['x', 'y'])
        
        stress = mds.stress_
        logger.info(f"Embedding generation complete. Stress: {stress:.4f}")
        
        return df_embedding, stress
        
    except Exception as e:
        logger.error(f"MDS Embedding failed: {e}")
        raise
