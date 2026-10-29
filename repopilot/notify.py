"The Fo MCP step reads out/call_trigger.json and places the owner call. The dial-out lives in Fo, not here, by design."
import json
from pathlib import Path


def read_trigger(outdir="out"):
    p = Path(outdir) / "call_trigger.json"
    return json.loads(p.read_text()) if p.exists() else None
