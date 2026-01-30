
import pandas as pd
import os

# Define paths
base_dir = os.path.dirname(os.path.abspath(__file__)) # src/data
project_root = os.path.dirname(os.path.dirname(base_dir)) # ../../
csv_path = os.path.join(project_root, 'data', '02-preprocessed', 'aprobaciones_limpias.csv')

print(f"Loading data from: {csv_path}")
try:
    df = pd.read_csv(csv_path)
except FileNotFoundError:
    print("Error: File not found.")
    exit(1)

# Logic for Tipo de Socio / Tipo_Pais
def get_socio_category(pais):
    p = str(pais).strip()
    # Fundadores
    if p in ['Guatemala', 'El Salvador', 'Honduras', 'Nicaragua', 'Costa Rica']:
        return 'Países Fundadores'
    # Regionales No-Fundadores
    elif p in ['República Dominicana', 'Panamá', 'Belice']:
        return 'Regionales No-Fundadores'
    # Extrarregionales
    elif p in ['México', 'Argentina', 'Colombia', 'España', 'Cuba', 'República de Corea', 'Corea del Sur', 'Taiwán', 'Taiwan', 'República de China (Taiwán)']:
        return 'Extrarregionales'
    # Regional
    elif 'Regional' in p:
        return 'Regional'
    return 'Otros'

# Apply Logic
print("Updating 'Tipo_Pais' column...")
df['Tipo_Pais'] = df['Pais'].apply(get_socio_category)

# Save back
print("Saving updated CSV...")
df.to_csv(csv_path, index=False)
print("Done. 'Tipo_Pais' column has been corrected.")
print(df[['Pais', 'Tipo_Pais']].drop_duplicates())
