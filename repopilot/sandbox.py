"Apply patches and run the repo's own tests in a scratch clone."
import shutil
import subprocess
from pathlib import Path


def _run(cmd, cwd):
    p = subprocess.run(cmd, cwd=cwd, capture_output=True, text=True, timeout=900)
    return {"cmd": " ".join(cmd), "code": p.returncode, "tail": (p.stdout + p.stderr)[-4000:]}


def apply_and_test(workdir, patches):
    "Overwrite files per patches, then run pytest/install if present. Returns report dict."
    root = Path(workdir)
    for rel, content in patches.items():
        target = root / rel
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(content)
    steps = []
    if (root / "requirements.txt").exists():
        steps.append(_run(["python3", "-m", "pip", "install", "-q", "-r", "requirements.txt"], root))
    if (root / "pyproject.toml").exists() or (root / "setup.py").exists():
        steps.append(_run(["python3", "-m", "pip", "install", "-q", "-e", "."], root))
    if (root / "tests").exists() or list(root.glob("test_*.py")):
        steps.append(_run(["python3", "-m", "pytest", "-q"], root))
    passed = all(s["code"] == 0 for s in steps) if steps else False
    return {"passed": passed, "steps": steps}


def cleanup(workdir):
    shutil.rmtree(workdir, ignore_errors=True)
