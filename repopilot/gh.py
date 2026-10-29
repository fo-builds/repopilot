"GitHub reads and writes: issue, clone url, branch, commit, PR."
import base64
import requests
from .config import GITHUB_API, GITHUB_TOKEN


def _h():
    h = {"Accept": "application/vnd.github+json"}
    if GITHUB_TOKEN:
        h["Authorization"] = f"Bearer {GITHUB_TOKEN}"
    return h


def parse_repo(url):
    "Accept a repo URL or owner/name and return (owner, name)."
    path = url.rstrip("/").removesuffix(".git")
    if "github.com" in path:
        path = path.split("github.com/")[1]
    parts = path.split("/")
    if len(parts) < 2:
        raise ValueError(f"cannot parse repo from {url}")
    return parts[0], parts[1]


def clone_url(owner, name):
    if GITHUB_TOKEN:
        return f"https://x-access-token:{GITHUB_TOKEN}@github.com/{owner}/{name}.git"
    return f"https://github.com/{owner}/{name}.git"


def get_issue(owner, name, number):
    r = requests.get(f"{GITHUB_API}/repos/{owner}/{name}/issues/{number}", headers=_h(), timeout=30)
    r.raise_for_status()
    return r.json()


def default_branch(owner, name):
    r = requests.get(f"{GITHUB_API}/repos/{owner}/{name}", headers=_h(), timeout=30)
    r.raise_for_status()
    return r.json()["default_branch"]


def create_branch(owner, name, branch, from_ref):
    r = requests.get(f"{GITHUB_API}/repos/{owner}/{name}/git/ref/heads/{from_ref}", headers=_h(), timeout=30)
    r.raise_for_status()
    sha = r.json()["object"]["sha"]
    r = requests.post(f"{GITHUB_API}/repos/{owner}/{name}/git/refs", headers=_h(),
                      json={"ref": f"refs/heads/{branch}", "sha": sha}, timeout=30)
    r.raise_for_status()
    return sha


def commit_file(owner, name, branch, path, content, message):
    q = requests.get(f"{GITHUB_API}/repos/{owner}/{name}/contents/{path}", headers=_h(), params={"ref": branch}, timeout=30)
    sha = q.json().get("sha") if q.status_code == 200 else None
    r = requests.put(f"{GITHUB_API}/repos/{owner}/{name}/contents/{path}", headers=_h(),
                     json={"message": message, "content": base64.b64encode(content.encode()).decode(),
                           "branch": branch, **({"sha": sha} if sha else {})}, timeout=30)
    r.raise_for_status()
    return r.json()


def open_pr(owner, name, branch, base, title, body):
    r = requests.post(f"{GITHUB_API}/repos/{owner}/{name}/pulls", headers=_h(),
                      json={"title": title, "head": branch, "base": base, "body": body}, timeout=30)
    if r.status_code == 422 and "already exists" in r.text:
        return {"html_url": "(existing PR)", "already": True}
    r.raise_for_status()
    return r.json()
