from pathlib import Path
import os
import subprocess
import sys

root = Path(__file__).resolve().parents[3]
python = root / ".venv" / ("Scripts/python.exe" if os.name == "nt" else "bin/python")
if not python.is_file():
    raise SystemExit("Run the repository setup command before invoking this skill.")
env = dict(os.environ)
env.setdefault("RESEARCH_VALIDATOR_CACHE", str(root / ".build/validator"))
raise SystemExit(subprocess.call([str(python), "-m", "research_skills", *sys.argv[1:]], env=env))
