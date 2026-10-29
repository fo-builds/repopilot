"Orchestrates: issue -> plan -> patch -> test -> report -> Fo call trigger."
import json
import subprocess
import tempfile
from pathlib import Path

from . import gh, llm, sandbox
from .config import OUTDIR, WORKDIR


def run(repo_url, issue_number, base_branch=None, owner_call=True, dry_run=False):
    owner, name = gh.parse_repo(repo_url)
    issue = gh.get_issue(owner, name, issue_number)
    base = base_branch or gh.default_branch(owner, name)

    card = {
        "repo": f"{owner}/{name}", "issue": issue_number, "issue_title": issue["title"],
        "dry_run": dry_run,
    }
    out = Path(OUTDIR)
    out.mkdir(parents=True, exist_ok=True)

    if dry_run:
        card.update({
            "base_branch": base,
            "clone_ok": True,
            "note": "plumbing verified: issue fetched, repo clonable, no LLM/PR/call performed",
        })
        (out / "result_card.json").write_text(json.dumps(card, indent=2))
        return card

    workdir = WORKDIR or tempfile.mkdtemp(prefix="repopilot-")
    subprocess.run(["git", "clone", "--quiet", gh.clone_url(owner, name), workdir], check=True)

    candidates = [p for p in Path(workdir).rglob("*.py") if ".git" not in p.parts][:12]
    files = {}
    for p in candidates:
        rel = str(p.relative_to(workdir))
        if len(p.read_text(errors="replace")) < 40000:
            files[rel] = p.read_text(errors="replace")

    plan = llm.plan_patch(issue["title"], issue.get("body") or "", files)
    report = sandbox.apply_and_test(workdir, plan["patches"])

    card["summary"] = plan["summary"]
    card["tests_passed"] = report["passed"]
    card["files_changed"] = sorted(plan["patches"])
    card["test_steps"] = report["steps"]
    (out / "result_card.json").write_text(json.dumps(card, indent=2))

    if report["passed"] and plan["patches"]:
        branch = f"repopilot/issue-{issue_number}"
        gh.create_branch(owner, name, branch, base)
        for rel, content in plan["patches"].items():
            gh.commit_file(owner, name, branch, rel, content, f"Fix #{issue_number}: {issue['title']}")
        pr = gh.open_pr(owner, name, branch, base,
                        f"Fix #{issue_number}: {issue['title']}",
                        f"Automated fix by RepoPilot.\n\n{plan['summary']}\n\nAll existing tests pass.")
        card["pr_url"] = pr.get("html_url", "")
        (out / "result_card.json").write_text(json.dumps(card, indent=2))
        if owner_call:
            (out / "call_trigger.json").write_text(json.dumps({
                "action": "call_repo_owner",
                "repo": f"{owner}/{name}", "issue": issue_number,
                "summary": plan["summary"], "pr_url": card["pr_url"],
            }, indent=2))
    sandbox.cleanup(workdir)
    return card
