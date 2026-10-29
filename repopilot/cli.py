import argparse
import json
from .pipeline import run


def main():
    ap = argparse.ArgumentParser(prog="repopilot")
    ap.add_argument("repo")
    ap.add_argument("issue", type=int)
    ap.add_argument("--base", default=None)
    ap.add_argument("--no-call", action="store_true", help="skip the Fo call trigger")
    ap.add_argument("--dry-run", action="store_true", help="prove the plumbing: fetch issue, clone, size the prompt, no LLM/PR/call")
    a = ap.parse_args()
    card = run(a.repo, a.issue, base_branch=a.base, owner_call=not a.no_call, dry_run=a.dry_run)
    print(json.dumps(card, indent=2))
