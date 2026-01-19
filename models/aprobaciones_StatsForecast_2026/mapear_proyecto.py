import os
from pathlib import Path

def generate_structure_file(startpath, output_filename="estructura_proyecto.txt"):
    # 1. Definir listas de ignorados (Basura y archivos innecesarios)
    IGNORE_DIRS = {
        '.git', '__pycache__', '.ipynb_checkpoints', '.vscode', '.idea', 
        'env', 'venv', 'node_modules', 'dist', 'build', '.pytest_cache'
    }
    
    IGNORE_FILES = {
        '.DS_Store', 'Thumbs.db', 'desktop.ini', '.gitignore', '.gitattributes'
    }
    
    IGNORE_EXTENSIONS = {
        '.pyc', '.pyo', '.pyd', '.log', '.tmp', '.bak', '.swp'
    }

    start_path_obj = Path(startpath)
    output_path = start_path_obj / output_filename

    print(f"Generando mapa en: {output_path} ...")

    with open(output_path, "w", encoding="utf-8") as f:
        f.write(f"📂 PROYECTO: {start_path_obj.name}\n")
        f.write(f"📍 RUTA: {startpath}\n")
        f.write("="*60 + "\n\n")

        for root, dirs, files in os.walk(startpath):
            # Filtrar directorios in-place (modifica la lista dirs mientras se recorre)
            dirs[:] = [d for d in dirs if d not in IGNORE_DIRS]
            
            # Calcular nivel de indentación
            level = root.replace(str(startpath), '').count(os.sep)
            indent = '    ' * level
            
            # Escribir nombre del directorio actual
            folder_name = os.path.basename(root)
            if root != str(startpath): # No imprimir la raiz como carpeta indentada
                f.write(f'{indent}📁 {folder_name}/\n')
            
            # Filtrar y escribir archivos
            subindent = '    ' * (level + 1)
            for file_name in sorted(files): # Ordenar alfabéticamente para orden visual
                # Lógica de filtrado de archivos
                if (file_name not in IGNORE_FILES and 
                    not any(file_name.endswith(ext) for ext in IGNORE_EXTENSIONS) and
                    file_name != output_filename): # No incluir el archivo que estamos creando
                    
                    f.write(f'{subindent}📄 {file_name}\n')

    print(f"✅ ¡Listo! Estructura guardada en: {output_filename}")

if __name__ == "__main__":
    # Usa el directorio donde está el script
    current_path = os.getcwd()
    generate_structure_file(current_path)