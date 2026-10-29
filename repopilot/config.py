import os

PROVIDER = os.environ.get("REPOPILOT_PROVIDER", "nebius")  # "nebius" | "openrouter" | "github_models"
NEBIUS_BASE = os.environ.get("NEBIUS_BASE", "https://api.studio.nebius.com/v1")
NEBIUS_MODEL = os.environ.get("NEBIUS_MODEL", "nvidia/nemotron-nano-9b-v2")
NEBIUS_API_KEY = os.environ.get("NEBIUS_API_KEY", "")
OPENROUTER_BASE = os.environ.get("OPENROUTER_BASE", "https://openrouter.ai/api/v1")
OPENROUTER_MODEL = os.environ.get("OPENROUTER_MODEL", "nvidia/nemotron-3.5-lightning:free")
OPENROUTER_API_KEY = os.environ.get("OPENROUTER_API_KEY", "")
GITHUB_TOKEN = os.environ.get("GITHUB_TOKEN", "")
GITHUB_MODELS_BASE = os.environ.get("GITHUB_MODELS_BASE", "https://models.github.ai/inference")
GITHUB_MODELS_MODEL = os.environ.get("GITHUB_MODELS_MODEL", "openai/gpt-4.1-mini")
GITHUB_API = "https://api.github.com"
WORKDIR = os.environ.get("REPOPILOT_WORKDIR", "")
OUTDIR = os.environ.get("REPOPILOT_OUTDIR", "out")
PLAN_FILE = os.environ.get("REPOPILOT_PLAN_FILE", "")  # offline/dev: pre-supplied plan JSON

def require_keys():
    key = {"nebius": NEBIUS_API_KEY, "openrouter": OPENROUTER_API_KEY,
           "github_models": GITHUB_TOKEN}[PROVIDER]
    missing = [k for k, v in (("provider key", key), ("GITHUB_TOKEN", GITHUB_TOKEN)) if not v]
    if missing:
        raise SystemExit("missing env: " + ", ".join(missing))
