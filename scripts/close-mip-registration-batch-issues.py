# /// script
# requires-python = ">=3.11"
# dependencies = []
# ///
"""
Close the registration issues handled by a batch PR

Takes one of the batch PRs opened by `prepare-mip-registration-batch.py`
(either the CMIP7-CVs or the WCRP-universe one,
both carry the same machine-readable block),
checks that the batch PRs are merged,
then comments on and closes each registration issue,
pointing to the PRs that resolved it.

Issues whose bot PR is still open are skipped, because their registration isn't in yet.
Merge (or close) the bot PR first, then re-run.

The script is idempotent: issues that are already closed are skipped.

It only needs the standard library and an authenticated `gh` CLI. Run it with a project venv, e.g.

    .github/form-processor/.venv/bin/python scripts/close-mip-registration-batch-issues.py

or with `uv run scripts/close-mip-registration-batch-issues.py`.

Configuration is hard-coded in `main`.
By default it is a dry run: everything is read, nothing is written.
"""

from __future__ import annotations

import json
import subprocess
from typing import Any

BATCH_DATA_START = "<!-- registration-batch-data"
BATCH_DATA_END = "registration-batch-data -->"


def gh_api(path: str, method: str = "GET", body: dict[str, Any] | None = None) -> Any:
    cmd = ["gh", "api", "--method", method, path, "-H", "Accept: application/vnd.github+json"]
    if body is not None:
        cmd.extend(["--input", "-"])

    res = subprocess.run(
        cmd,
        input=None if body is None else json.dumps(body),
        capture_output=True,
        text=True,
        check=False,
    )
    if res.returncode != 0:
        msg = f"gh api {method} {path} failed:\n{res.stderr}\n{res.stdout}"
        raise RuntimeError(msg)

    return json.loads(res.stdout) if res.stdout.strip() else None


def pr_url(repo: str, number: int) -> str:
    return f"https://github.com/{repo}/pull/{number}"


def parse_batch_data(body: str) -> dict[str, Any]:
    if BATCH_DATA_START not in body or BATCH_DATA_END not in body:
        msg = "PR description has no registration batch block. Was it created by prepare-mip-registration-batch.py?"
        raise ValueError(msg)

    raw = body.split(BATCH_DATA_START, 1)[1].split(BATCH_DATA_END, 1)[0]
    return json.loads(raw)


def closing_comment(batch_prs: list[str], bot_pr: str | None, branch: str) -> str:
    lines = ["Registered via the following PRs, which have now been merged:", ""]
    lines.extend(f"- {url}" for url in batch_prs)
    if bot_pr:
        lines.append(f"- {bot_pr} (the automated registration PR, merged into `{branch}`)")
    lines.extend(["", f"Thanks, closing."])

    return "\n".join(lines)


def main() -> None:
    # The batch PR to process, in either repository
    repo = "WCRP-CMIP/CMIP7-CVs"
    pr_number = 0
    # Refuse to close anything unless every batch PR (CMIP7-CVs and universe) is merged
    require_all_merged = True
    # Set to False to actually comment on and close the issues
    dry_run = True

    if pr_number <= 0:
        raise ValueError("Set `pr_number` in `main`")

    print("DRY RUN, nothing will be written" if dry_run else "LIVE RUN")
    pr = gh_api(f"repos/{repo}/pulls/{pr_number}")
    data = parse_batch_data(pr.get("body") or "")
    issues_repo = data["issues_repo"]
    branch = data["branch"]

    batch_prs = dict(data["pull_requests"])
    batch_prs[repo] = pr_number

    unmerged = []
    for batch_repo, number in batch_prs.items():
        state = gh_api(f"repos/{batch_repo}/pulls/{number}")
        merged = bool(state.get("merged_at"))
        print(f"{batch_repo}#{number}: {'merged' if merged else state['state'] + ', not merged'}")
        if not merged:
            unmerged.append(f"{batch_repo}#{number}")

    if unmerged and require_all_merged:
        raise SystemExit(f"Not closing anything, these batch PRs aren't merged yet: {', '.join(unmerged)}")

    merged_batch_urls = [pr_url(r, n) for r, n in batch_prs.items() if f"{r}#{n}" not in unmerged]

    skipped = []
    for reg in data["registrations"]:
        number = reg["issue"]
        label = f"#{number} ({reg['kind']} `{reg['name']}`)"
        issue = gh_api(f"repos/{issues_repo}/issues/{number}")
        if issue["state"] == "closed":
            print(f"{label}: already closed, skipping")
            continue

        bot_pr_url = None
        if reg.get("bot_pr"):
            bot_pr = gh_api(f"repos/{issues_repo}/pulls/{reg['bot_pr']}")
            if bot_pr["state"] == "open":
                print(f"{label}: SKIPPING, bot PR #{reg['bot_pr']} is still open (merge or close it first)")
                skipped.append(label)
                continue
            if bot_pr.get("merged_at"):
                bot_pr_url = pr_url(issues_repo, reg["bot_pr"])

        comment = closing_comment(merged_batch_urls, bot_pr_url, branch)
        print(f"{label}: comment and close")
        print("    " + comment.replace("\n", "\n    "))
        if not dry_run:
            gh_api(f"repos/{issues_repo}/issues/{number}/comments", method="POST", body={"body": comment})
            gh_api(
                f"repos/{issues_repo}/issues/{number}",
                method="PATCH",
                body={"state": "closed", "state_reason": "completed"},
            )

    if skipped:
        print(f"\nSkipped {len(skipped)} issue(s): {', '.join(skipped)}")


if __name__ == "__main__":
    main()
