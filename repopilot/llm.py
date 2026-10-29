"NVIDIA Nemotron. Primary: Nebius Token Factory (OpenAI-compatible). Fallback: OpenRouter free tier."
import json
import os
import requests
from .config import (GITHUB_MODELS_BASE, GITHUB_MODELS_MODEL, NEBIUS_API_KEY, NEBIUS_BASE,
                     NEBIUS_MODEL, OPENROUTER_API_KEY, OPENROUTER_BASE, OPENROUTER_MODEL,
                     PLAN_FILE, PROVIDER, GITHUB_TOKEN)


def chat(messages, temperature=0.2, max_tokens=4000):
    if PROVIDER == "openrouter":
        base, key, model = OPENROUTER_BASE, OPENROUTER_API_KEY, OPENROUTER_MODEL
        headers = {"Authorization": f"Bearer {key}", "HTTP-Referer": "https://github.com/fo-builds/repopilot",
                   "X-Title": "RepoPilot"}
    elif PROVIDER == "github_models":
        base, key, model = GITHUB_MODELS_BASE, GITHUB_TOKEN, GITHUB_MODELS_MODEL
        headers = {"Authorization": f"Bearer {key}"}
    else:
        base, key, model = NEBIUS_BASE, NEBIUS_API_KEY, NEBIUS_MODEL
        headers = {"Authorization": f"Bearer {key}"}
    r = requests.post(f"{base}/chat/completions", headers=headers,
                      json={"model": model, "messages": messages,
                            "temperature": temperature, "max_tokens": max_tokens},
                      timeout=180)
    r.raise_for_status()
    return r.json()["choices"][0]["message"]["content"]


def _parse(raw):
    raw = raw.strip()
    if raw.startswith("```"):
        raw = raw.split("\n", 1)[1].rsplit("```", 1)[0].strip()
    data = json.loads(raw)
    return {"summary": data.get("summary", ""), "patches": data.get("patches", {})}


def plan_patch(issue_title, issue_body, files):
    "Return {'summary': str, 'patches': {path: new_content}} using the issue and file contents."
    if PLAN_FILE and os.path.exists(PLAN_FILE):
        return json.loads(open(PLAN_FILE).read())
    file_block = "\n\n".join(f"### FILE: {p}\n```\n{c}\n```" for p, c in files.items())
    sys = ("You are a careful senior engineer. Given a GitHub issue and the current contents of the "
           "files likely involved, produce the minimal correct fix.\n"
           'Reply with ONLY a JSON object: {"summary": one-sentence human summary of the fix, '
           '"patches": {"path": full new file content, ...}}. Never truncate files; always emit complete files.')
    user = f"ISSUE TITLE: {issue_title}\n\nISSUE BODY:\n{issue_body or '(empty)'}\n\n{file_block}"
    return _parse(chat([{"role": "system", "content": sys}, {"role": "user", "content": user}], temperature=0.1))
