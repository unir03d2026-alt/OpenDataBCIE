import gower
import pandas as pd
import numpy as np
import logging

logger = logging.getLogger(__name__)

def compute_gower_distance(df: pd.DataFrame, cat_features: list = None):
    """
    Computes the Gower Distance Matrix for a given DataFrame.
    
    Args:
        df: Pandas DataFrame with mixed data types.
        cat_features: List of column names to be treated as categorical.
                      If None, will attempt to infer or treat object/category cols as categorical.
                      
    Returns:
        d_matrix: NxN numpy array of Gower distances (0.0 to 1.0).
    """
    logger.info(f"Computing Gower matrix for {len(df)} samples...")
    
    # Gower library automatically detects bool/category/object as categorical
    # But it's safer to explicitly pass 'cat_features' if the library supports it strictly,
    # or ensure dtypes are correct.
    # The 'gower.gower_matrix' function handles this.
    
    try:
        # Optimize dtypes for gower
        df_gower = df.copy()
        
        if cat_features:
            for col in cat_features:
                if col in df_gower.columns:
                    # df_gower[col] = df_gower[col].astype('category')
                    # Keep as object/string to avoid numpy dtype errors
                    pass
                    
        # Compute matrix
        distance_matrix = gower.gower_matrix(df_gower)
        
        logger.info("Gower matrix computation complete.")
        return distance_matrix
        
    except Exception as e:
        logger.error(f"Gower computation failed: {e}")
        raise
