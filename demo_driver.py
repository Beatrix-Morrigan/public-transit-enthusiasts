from pathlib import Path

from src.PatrolRoutes.PatrolRoutes import PatrolRoutes

pr = PatrolRoutes(
	Path("examples/midcity_settings_20250806.json")
)

pr.run_interactive_demo()