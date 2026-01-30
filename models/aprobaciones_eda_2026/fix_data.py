
import pandas as pd
from pathlib import Path

# Paths
base_dir = Path("D:/BCIE/Datos-Abiertos-BCIE/models/aprobaciones_eda_2026")
data_path = base_dir / "data/02-preprocessed/aprobaciones_limpias.csv"

def fix_data():
    print(f"Reading {data_path}...")
    df = pd.read_csv(data_path)
    
    # 1. Drop unused columns
    cols_to_drop = ['Monto_Banda', 'Frecuencia_Banda', 'Cuadrante_Estrategia']
    df.drop(columns=[c for c in cols_to_drop if c in df.columns], inplace=True)
    print("Dropped unused columns.")
    
    # 2. Fix Casing for Country
    # Ensure Title Case for "Pais" but handle special acronyms if needed.
    # User asked for "Nombre natura" e.g., "Costa Rica".
    if 'Pais' in df.columns:
        df['Pais'] = df['Pais'].astype(str).str.title().str.strip()
        print("Updated 'Pais' to Title Case.")
        
    # 3. Update 'Tipo_Pais' because it was derived from uppercase names
    # Founders: Guatemala, Honduras, El Salvador, Nicaragua, Costa Rica
    def categorize_pais(pais: str) -> str:
        founders = ['Guatemala', 'Honduras', 'El Salvador', 'Nicaragua', 'Costa Rica']
        if pais in founders: return 'Regional'
        # Check for multi-country
        if pais.upper() == 'REGIONAL' or pais == 'Regional': return 'Multi-country'
        return 'Extra-regional'

    if 'Pais' in df.columns:
        df['Tipo_Pais'] = df['Pais'].apply(categorize_pais)
        print("Re-calculated 'Tipo_Pais'.")

    # Save
    df.to_csv(data_path, index=False)
    print(f"Saved cleaned data to {data_path}")
    print(df[['Pais', 'Tipo_Pais']].drop_duplicates())

if __name__ == "__main__":
    fix_data()
