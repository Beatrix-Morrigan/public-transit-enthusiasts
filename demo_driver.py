from datetime import datetime
from pathlib import Path

from src.PatrolRoutes.PatrolRoutes import PatrolRoutes

pr = PatrolRoutes(
	Path("examples/midcity_settings_20250806.json")
)

dt = datetime.now()
seed = int(f"{dt.strftime('%Y%m%d')}")
print(f"Seed={seed}")

pr.run_interactive_demo(
	rng_seed = seed + 2
)