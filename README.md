# RepoPilot

**Nebius x NVIDIA Global AI Hackathon entry.** RepoPilot is an autonomous repo
doctor: give it a GitHub repo and an issue number and it plans a fix with
NVIDIA **Nemotron**, applies the patch, runs the repo's own test suite in a
sandbox, and only when everything is green does it open a pull request. It
then hands a one-line summary to **Fo** (the operator's AI assistant), which
places the closing phone call to the repo owner.

```
issue --> clone --> read files --> Nemotron plans the diff --> patch applied
      --> pytest in sandbox --> green? -> branch + tested PR -> Fo calls the owner
```

## Quickstart

```bash
pip install -e .
export GITHUB_TOKEN=...            # repo access
export REPOPILOT_PROVIDER=nebius   # or openrouter | github_models
export NEBIUS_API_KEY=...          # Nebius Token Factory (OpenAI-compatible)
repopilot run https://github.com/owner/repo 42
```

Offline/dev mode: set `REPOPILOT_PLAN_FILE` to a pre-supplied plan JSON and the
LLM step is skipped.

## Providers

| provider        | model (default)                          | key                  |
|-----------------|------------------------------------------|----------------------|
| `nebius`        | `nvidia/nemotron-nano-9b-v2`             | `NEBIUS_API_KEY`     |
| `openrouter`    | `nvidia/nemotron-3.5-lightning:free`     | `OPENROUTER_API_KEY` |
| `github_models` | first `nemotron` model in the catalog    | `GITHUB_TOKEN`       |

Nemotron is the brain in every mode: the Nebius Token Factory endpoint and the
OpenRouter free tier both serve `nvidia/nemotron-*`; on GitHub Models the demo
workflow auto-selects the first Nemotron model the catalog offers.

## Live demo

`fo-builds/textstats` carries a deliberately buggy `median()` plus a failing
test, an issue, and a GitHub Actions workflow (`.github/workflows/demo.yml`)
that installs RepoPilot straight from this public repo and runs the whole
pipeline end to end, live, in CI:

1. the seeded issue is fetched,
2. Nemotron plans the patch,
3. the patch is applied and the repo's tests run in a sandbox,
4. a tested PR is opened on the demo repo.

The run log is the demo. `out/result_card.json` holds the machine-readable
summary.

## The closing call

When tests are green, RepoPilot writes `out/call_trigger.json`. Fo's MCP side
reads that card and places the call to the repo owner with a spoken summary of
the fix. The dial-out lives in Fo, not in RepoPilot, by design: an agent that
patches code should say so out loud before it does.

## Structure

```
repopilot/
  cli.py        argparse entry: repopilot run <repo> <issue>
  pipeline.py   orchestrates the whole loop
  gh.py         GitHub reads/writes: issue, branch, commit, PR
  llm.py        Nemotron providers (Nebius / OpenRouter free / GitHub Models)
  sandbox.py    apply patches + run the repo's own tests
  notify.py     out/call_trigger.json -> Fo MCP step
```
