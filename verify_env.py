

libraries = [
    "pandas", "numpy", "scipy", "matplotlib", "seaborn", "plotly", "openpyxl",
    "requests", "yaml", "pytest", "sklearn", "prophet", "statsforecast",
    "neuralprophet", "xgboost", "hdbscan", "torch", "transformers", "accelerate", "utilsforecast"
]

print(f"{'LIBRARY':<20} | {'STATUS':<10}")
print("-" * 35)

for lib in libraries:
    try:
        __import__(lib)
        print(f"{lib:<20} | \033[92mINSTALLED\033[0m")
    except ImportError:
        print(f"{lib:<20} | \033[91mMISSING\033[0m")
    except Exception as e:
        print(f"{lib:<20} | \033[93mERROR: {e}\033[0m")
