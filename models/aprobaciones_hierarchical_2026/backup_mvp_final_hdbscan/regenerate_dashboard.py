
from src.dashboard.generate_dashboard import generate_dashboard
import shutil
from pathlib import Path

run_id = "run_20260121_151227_05f783"
print(f"Regenerating dashboard for {run_id}...")
generate_dashboard(run_id=run_id)

# Copy to src/dashboard for easy access
src = Path(f"data/04-predictions/runs/{run_id}/dashboard_clustering.html")
dst = Path("src/dashboard/dashboard_clustering.html")
if src.exists():
    shutil.copy(src, dst)
    print(f"Copied to {dst}")
else:
    print("Source generation failed.")
