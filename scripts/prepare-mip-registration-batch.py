# /// script
# requires-python = ">=3.11"
# dependencies = []
# ///
"""
Gather the registration issues for one or more MIPs into a batch for review

For each batch (a branch name plus the MIPs it covers), this script

1. creates the batch branch from the base branch in CMIP7-CVs and WCRP-universe,
   if it doesn't already exist (an existing branch that is strictly behind the
   base branch is fast-forwarded)
1. finds every open experiment registration issue in CMIP7-CVs
   whose activity is one of the batch's MIPs,
   plus any open activity registration issue for those MIPs
1. for each issue
    - if the automated processing worked (there is an open bot PR for it,
      or one already merged into the batch branch, and the latest bot comment
      isn't a validation failure),
      retargets the bot PR at the batch branch and merges it there
    - otherwise, adds a note to the universe experiment generator script
      (on the batch branch) that the registration has to be added by hand
1. opens (or updates) a batch branch -> base branch PR in both repositories.
   The descriptions list every issue the batch closes,
   and carry a machine-readable block that
   `close-mip-registration-batch-issues.py` uses to close the issues
   once the PRs are merged.
   Nobody is tagged. Instead, each PR gets a comment listing the handles to tag for review
   (the issue creators plus `extra_mentions`), to copy out once the batch has been checked.

The script is idempotent, so it can be re-run
(e.g. after an issue is fixed or a new registration arrives)
to update the batch.

It only needs the standard library and an authenticated `gh` CLI
(`gh auth status`). Run it with a project venv, e.g.

    .github/form-processor/.venv/bin/python scripts/prepare-mip-registration-batch.py

or with `uv run scripts/prepare-mip-registration-batch.py`.

Configuration is hard-coded in `main`.
By default it is a dry run: everything is read, nothing is written.
"""

from __future__ import annotations

import base64
import json
import re
import subprocess
import time
import urllib.parse
from dataclasses import asdict, dataclass, field
from typing import Any

BATCH_DATA_START = "<!-- registration-batch-data"
BATCH_DATA_END = "registration-batch-data -->"
GENERATOR_NOTE_START = "# BEGIN registrations to add by hand (batch `{branch}`)"
GENERATOR_NOTE_END = "# END registrations to add by hand (batch `{branch}`)"
REVIEW_HANDLES_PREFIX = "Tag these people for review:"


@dataclass(frozen=True)
class Batch:
    """A batch of registrations, handled on one branch"""

    branch: str
    """Branch to create in both repositories"""

    mips: tuple[str, ...]
    """Activity IDs whose registrations belong in this batch (case-insensitive)"""

    label: str
    """Human-readable name, used in PR titles"""


@dataclass(frozen=True)
class Config:
    cvs_repo: str
    universe_repo: str
    base_branch: str
    generator_path: str
    extra_mentions: tuple[str, ...]
    dry_run: bool
    draft: bool


@dataclass
class Registration:
    """A registration issue and what happened to its automated processing"""

    issue: int
    kind: str
    name: str
    activity: str
    author: str
    automated: bool
    bot_pr: int | None = None
    bot_pr_state: str | None = None
    """`open` or `merged` when `automated`; otherwise whatever was found, if anything"""
    reason: str = ""
    """Why the automated processing is considered to have failed"""
    bot_notes: list[str] = field(default_factory=list)


# --------------------------------------------------------------------------- #
# GitHub helpers (via the `gh` CLI)
# --------------------------------------------------------------------------- #
class GitHubNotFound(Exception):
    pass


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
        if "HTTP 404" in res.stderr or '"Not Found"' in res.stdout:
            raise GitHubNotFound(path)
        msg = f"gh api {method} {path} failed:\n{res.stderr}\n{res.stdout}"
        raise RuntimeError(msg)

    return json.loads(res.stdout) if res.stdout.strip() else None


def gh_api_paginated(path: str) -> list[Any]:
    sep = "&" if "?" in path else "?"
    out: list[Any] = []
    page = 1
    while True:
        chunk = gh_api(f"{path}{sep}per_page=100&page={page}")
        out.extend(chunk)
        if len(chunk) < 100:
            return out
        page += 1


def get_branch_sha(repo: str, branch: str) -> str | None:
    try:
        ref = gh_api(f"repos/{repo}/git/ref/heads/{urllib.parse.quote(branch)}")
    except GitHubNotFound:
        return None

    return ref["object"]["sha"]


def compare(repo: str, base: str, head: str) -> dict[str, Any]:
    return gh_api(f"repos/{repo}/compare/{base}...{head}")


def find_open_pr(repo: str, head_branch: str, base_branch: str) -> dict[str, Any] | None:
    owner = repo.split("/")[0]
    head = urllib.parse.quote(f"{owner}:{head_branch}")
    pulls = gh_api(f"repos/{repo}/pulls?state=open&head={head}&base={base_branch}")

    return pulls[0] if pulls else None


# --------------------------------------------------------------------------- #
# Step 1: branches
# --------------------------------------------------------------------------- #
def ensure_branch(repo: str, branch: str, base_branch: str, dry_run: bool) -> None:
    base_sha = get_branch_sha(repo, base_branch)
    if base_sha is None:
        raise RuntimeError(f"Base branch {base_branch} not found in {repo}")

    sha = get_branch_sha(repo, branch)
    if sha is None:
        print(f"  {repo}: create branch `{branch}` from `{base_branch}` ({base_sha[:8]})")
        if not dry_run:
            gh_api(
                f"repos/{repo}/git/refs",
                method="POST",
                body={"ref": f"refs/heads/{branch}", "sha": base_sha},
            )
        return

    status = compare(repo, base_branch, branch)["status"]
    if status == "behind":
        # E.g. a branch from an earlier batch for the same MIP that has since been merged.
        # Fast-forwarding loses nothing and stops PRs into it showing unrelated changes.
        print(f"  {repo}: branch `{branch}` exists but is behind `{base_branch}`, fast-forwarding it")
        if not dry_run:
            gh_api(
                f"repos/{repo}/git/refs/heads/{urllib.parse.quote(branch)}",
                method="PATCH",
                body={"sha": base_sha, "force": False},
            )
    else:
        print(f"  {repo}: branch `{branch}` already exists ({status} relative to `{base_branch}`)")


def ensure_branch_has_commit(repo: str, branch: str, base_branch: str, dry_run: bool) -> None:
    """
    GitHub refuses to open a PR for a branch with no commits ahead of its base,
    so add an empty commit to start the batch if needed.
    """
    sha = get_branch_sha(repo, branch)
    if sha is None:
        # Only possible in a dry run, the branch would have been created
        print(f"  {repo}: add an empty commit to `{branch}` so the PR can be opened")
        return

    if compare(repo, base_branch, branch)["ahead_by"] > 0:
        return

    print(f"  {repo}: add an empty commit to `{branch}` so the PR can be opened")
    if dry_run:
        return

    tree = gh_api(f"repos/{repo}/git/commits/{sha}")["tree"]["sha"]
    commit = gh_api(
        f"repos/{repo}/git/commits",
        method="POST",
        body={"message": f"Start the `{branch}` registration batch", "tree": tree, "parents": [sha]},
    )
    gh_api(
        f"repos/{repo}/git/refs/heads/{urllib.parse.quote(branch)}",
        method="PATCH",
        body={"sha": commit["sha"], "force": False},
    )


# --------------------------------------------------------------------------- #
# Step 2: find and classify the registration issues
# --------------------------------------------------------------------------- #
def parse_issue_form_body(body: str) -> dict[str, str]:
    """Same parsing as `github_form_processor.issue_body.parse_issue_form_body`"""
    matches = list(re.finditer(r"^### (?P<label>.+?)\s*$", body, re.MULTILINE))
    fields: dict[str, str] = {}
    for i, match in enumerate(matches):
        end = matches[i + 1].start() if i + 1 < len(matches) else len(body)
        value = body[match.end() : end].strip()
        fields[match.group("label").strip()] = "" if value in {"_No response_", "No response"} else value

    return fields


def detect_kind(issue: dict[str, Any], fields: dict[str, str]) -> str | None:
    """Mirrors `github_form_processor.processor.detect_form_kind` for the kinds we handle"""
    title = (issue.get("title") or "").lower()
    if title.startswith("[experiment registration]") or "Experiment name" in fields:
        return "experiment"
    if title.startswith("[activity registration]") or "Activity name" in fields:
        return "activity"

    return None


def is_bot(user: dict[str, Any]) -> bool:
    return user.get("type") == "Bot" or user.get("login", "").endswith("[bot]")


def latest_bot_comment(repo: str, issue: int) -> str | None:
    comments = gh_api_paginated(f"repos/{repo}/issues/{issue}/comments")
    bot_comments = [
        c["body"]
        for c in comments
        if is_bot(c["user"])
        and (c["body"].startswith("### Registration form") or re.match(r"(Created|Updated) \[pull request", c["body"]))
    ]

    return bot_comments[-1] if bot_comments else None


def bullet_points_after(heading: str, text: str) -> list[str]:
    if heading not in text:
        return []

    after = text.split(heading, 1)[1]
    return [line[2:].strip() for line in after.splitlines() if line.startswith("- ")]


def classify(
    issue: dict[str, Any],
    kind: str,
    fields: dict[str, str],
    activity: str,
    all_pulls: list[dict[str, Any]],
    cfg: Config,
    batch: Batch,
) -> Registration:
    number = issue["number"]
    name = fields.get("Experiment name" if kind == "experiment" else "Activity name", "").strip()
    reg = Registration(
        issue=number,
        kind=kind,
        name=name,
        activity=activity,
        author=issue["user"]["login"],
        automated=False,
    )

    # Bot PR branches are `registration/{kind}-{issue}-{identifier}`
    prefix = f"registration/{kind}-{number}-"
    candidates = [p for p in all_pulls if p["head"]["ref"].startswith(prefix)]
    open_prs = [p for p in candidates if p["state"] == "open"]
    merged_into_batch = [p for p in candidates if p.get("merged_at") and p["base"]["ref"] == batch.branch]
    merged_elsewhere = [p for p in candidates if p.get("merged_at") and p["base"]["ref"] != batch.branch]

    comment = latest_bot_comment(cfg.cvs_repo, number)
    validation_failed = comment is not None and comment.startswith("### Registration form")
    if comment:
        reg.bot_notes = bullet_points_after("Notes:", comment) or bullet_points_after("Additional notes:", comment)

    if len(open_prs) > 1:
        reg.reason = "several open bot PRs: " + ", ".join(f"#{p['number']}" for p in open_prs)
    elif validation_failed:
        errors = [e for e in bullet_points_after("save the changes.", comment) if e not in reg.bot_notes]
        reg.reason = "form validation failed: " + ("; ".join(errors) or "see the issue")
        if open_prs:
            reg.reason += f" (bot PR #{open_prs[0]['number']} is out of date)"
    elif open_prs:
        reg.automated = True
        reg.bot_pr, reg.bot_pr_state = open_prs[0]["number"], "open"
    elif merged_into_batch:
        reg.automated = True
        reg.bot_pr, reg.bot_pr_state = merged_into_batch[-1]["number"], "merged"
    elif merged_elsewhere:
        p = merged_elsewhere[-1]
        reg.bot_pr, reg.bot_pr_state = p["number"], "merged-elsewhere"
        reg.reason = f"bot PR #{p['number']} was already merged into `{p['base']['ref']}`, check whether this issue is already done"
    elif candidates:
        p = candidates[-1]
        reg.bot_pr, reg.bot_pr_state = p["number"], "closed"
        reg.reason = f"bot PR #{p['number']} was closed without being merged"
    else:
        reg.reason = "no bot PR was created"

    return reg


def find_registrations(cfg: Config, batch: Batch, issues: list[dict[str, Any]], all_pulls: list[dict[str, Any]]) -> list[Registration]:
    mips = {m.lower() for m in batch.mips}
    regs: list[Registration] = []
    for issue in issues:
        body = issue.get("body") or ""
        fields = parse_issue_form_body(body)
        kind = detect_kind(issue, fields)
        if kind is None:
            continue

        activity = (fields.get("Activity") if kind == "experiment" else fields.get("Activity name")) or ""
        activity = activity.strip().strip("`").strip()
        if activity.lower() in mips:
            regs.append(classify(issue, kind, fields, activity, all_pulls, cfg, batch))
        elif any(re.search(rf"\b{re.escape(m)}\b", body, re.IGNORECASE) for m in mips):
            print(
                f"  WARNING: #{issue['number']} ({kind} registration, activity {activity!r}) mentions "
                f"{'/'.join(batch.mips)} but isn't registered under it, so it isn't included. Check by hand."
            )

    # Activity first, then by issue number
    return sorted(regs, key=lambda r: (r.kind != "activity", r.issue))


# --------------------------------------------------------------------------- #
# Step 3: retarget and merge bot PRs, note the failures in the generator
# --------------------------------------------------------------------------- #
def wait_for_mergeable(repo: str, number: int, attempts: int = 10, delay: float = 3.0) -> bool | None:
    """
    GitHub computes mergeability in the background (`mergeable` is `null` until it's done),
    in particular straight after the base branch changes
    """
    for _ in range(attempts):
        mergeable = gh_api(f"repos/{repo}/pulls/{number}")["mergeable"]
        if mergeable is not None:
            return mergeable
        time.sleep(delay)

    return None


def retarget_and_merge(cfg: Config, batch: Batch, regs: list[Registration], all_pulls: list[dict[str, Any]]) -> None:
    by_number = {p["number"]: p for p in all_pulls}
    for reg in regs:
        if not reg.automated or reg.bot_pr_state != "open":
            continue

        label = f"#{reg.bot_pr} (issue #{reg.issue})"
        current_base = by_number[reg.bot_pr]["base"]["ref"]
        if current_base == batch.branch:
            print(f"  {label} already targets `{batch.branch}`")
        else:
            print(f"  retarget {label} from `{current_base}` to `{batch.branch}`")
            if not cfg.dry_run:
                gh_api(f"repos/{cfg.cvs_repo}/pulls/{reg.bot_pr}", method="PATCH", body={"base": batch.branch})

        print(f"  merge {label} into `{batch.branch}`")
        if cfg.dry_run:
            continue

        mergeable = wait_for_mergeable(cfg.cvs_repo, reg.bot_pr)
        if not mergeable:
            why = "it has conflicts" if mergeable is False else "GitHub didn't report whether it can be merged"
            print(f"    WARNING: not merging {label}, {why}. Fix it and re-run.")
            continue

        try:
            gh_api(
                f"repos/{cfg.cvs_repo}/pulls/{reg.bot_pr}/merge",
                method="PUT",
                body={"merge_method": "merge"},
            )
        except RuntimeError as exc:
            print(f"    WARNING: merging {label} failed, re-run to try again:\n{exc}")
            continue

        reg.bot_pr_state = "merged"


def one_line(text: str) -> str:
    return " ".join(text.split())


def generator_note(cfg: Config, batch: Batch, failed: list[Registration]) -> str:
    lines = [
        GENERATOR_NOTE_START.format(branch=batch.branch),
        "# The automated processing failed for these registrations,",
        "# so they have to be added to this script by hand:",
    ]
    for reg in failed:
        lines.append(f"# - {reg.activity} {reg.kind} `{reg.name}`: https://github.com/{cfg.cvs_repo}/issues/{reg.issue}")
        lines.append(f"#   ({one_line(reg.reason)})")
    lines.append(GENERATOR_NOTE_END.format(branch=batch.branch))

    return "\n".join(lines) + "\n"


def update_generator_note(cfg: Config, batch: Batch, regs: list[Registration]) -> None:
    failed = [r for r in regs if not r.automated]
    ref = batch.branch if get_branch_sha(cfg.universe_repo, batch.branch) else cfg.base_branch
    contents = gh_api(f"repos/{cfg.universe_repo}/contents/{cfg.generator_path}?ref={urllib.parse.quote(ref)}")
    source = base64.b64decode(contents["content"]).decode("utf-8")

    start = GENERATOR_NOTE_START.format(branch=batch.branch)
    end = GENERATOR_NOTE_END.format(branch=batch.branch)
    block_re = re.compile(rf"{re.escape(start)}\n.*?{re.escape(end)}\n\n\n", re.DOTALL)

    without = block_re.sub("", source)
    if failed:
        note = generator_note(cfg, batch, failed)
        if "\ndef main(" not in without:
            raise RuntimeError(f"Can't find `def main(` in {cfg.generator_path}")
        updated = without.replace("\ndef main(", f"\n{note}\n\ndef main(", 1)
    else:
        updated = without

    if updated == source:
        print(f"  {cfg.generator_path} note is up to date")
        return

    if failed:
        print(f"  write note for {len(failed)} registration(s) to {cfg.universe_repo}:{batch.branch}/{cfg.generator_path}:")
        print("    " + generator_note(cfg, batch, failed).rstrip().replace("\n", "\n    "))
    else:
        print(f"  remove the (now empty) note from {cfg.generator_path}")

    if not cfg.dry_run:
        gh_api(
            f"repos/{cfg.universe_repo}/contents/{cfg.generator_path}",
            method="PUT",
            body={
                "message": f"Note the `{batch.branch}` registrations that need adding by hand",
                "content": base64.b64encode(updated.encode("utf-8")).decode("ascii"),
                "sha": contents["sha"],
                "branch": batch.branch,
            },
        )


# --------------------------------------------------------------------------- #
# Step 4: batch PRs
# --------------------------------------------------------------------------- #
def pr_body(
    cfg: Config,
    batch: Batch,
    regs: list[Registration],
    repo: str,
    prs: dict[str, int | None],
) -> str:
    def issue_ref(n: int) -> str:
        # Always the full slug, which GitHub needs for cross-repository references
        return f"{cfg.cvs_repo}#{n}"

    def status(reg: Registration) -> str:
        if reg.automated:
            done = "merged into" if reg.bot_pr_state == "merged" else "targeting"
            return f"✓ bot PR {issue_ref(reg.bot_pr)} ({done} `{batch.branch}`)"
        return f"✗ to add by hand: {one_line(reg.reason)}"

    other = {cfg.cvs_repo: "CMIP7-CVs", cfg.universe_repo: "WCRP-universe"}
    if repo == cfg.cvs_repo:
        intro = (
            f"Adds the {batch.label} registrations. "
            f"The bot PRs for the registrations that were processed automatically have been merged into `{batch.branch}`."
        )
    else:
        intro = (
            f"Adds the {batch.label} registrations to the experiment generator "
            f"(`{cfg.generator_path}`) and regenerates."
        )
        if any(not r.automated for r in regs):
            intro += (
                " Registrations whose automated processing failed are listed in a note "
                "just above `main` in the generator and have to be added by hand."
            )

    lines = [intro, "", "## Registrations", "", "| Issue | Kind | Name | Activity | Submitted by | Automated processing |", "|---|---|---|---|---|---|"]
    for reg in regs:
        lines.append(f"| {issue_ref(reg.issue)} | {reg.kind} | `{reg.name}` | {reg.activity} | `{reg.author}` | {status(reg)} |")

    notes = [r for r in regs if r.bot_notes]
    if notes:
        lines.extend(["", "<details><summary>Notes from the automated processing</summary>", ""])
        for reg in notes:
            lines.append(f"- {issue_ref(reg.issue)} (`{reg.name}`)")
            lines.extend(f"    - {n}" for n in reg.bot_notes)
        lines.extend(["", "</details>"])

    lines.extend(["", "## Closes", ""])
    lines.extend(f"Closes {issue_ref(r.issue)}" for r in regs)
    lines.extend(
        [
            "",
            f"GitHub won't close these automatically because this PR targets `{cfg.base_branch}`, "
            "not the default branch. Once both PRs are merged, close them with "
            "`scripts/close-mip-registration-batch-issues.py`.",
            "",
            "## Related",
            "",
        ]
    )
    for other_repo, label in other.items():
        if other_repo != repo:
            number = prs.get(other_repo)
            lines.append(f"- {label}: {other_repo}#{number}" if number else f"- {label}: (to be created)")

    data = {
        "branch": batch.branch,
        "base_branch": cfg.base_branch,
        "issues_repo": cfg.cvs_repo,
        "pull_requests": {k: v for k, v in prs.items() if v},
        "registrations": [asdict(r) for r in regs],
    }
    lines.extend(["", BATCH_DATA_START, json.dumps(data, indent=2), BATCH_DATA_END])

    return "\n".join(lines)


def sync_batch_prs(cfg: Config, batch: Batch, regs: list[Registration]) -> None:
    titles = {
        cfg.cvs_repo: f"Add {batch.label} registrations",
        cfg.universe_repo: f"Add {batch.label} experiments",
    }
    existing = {repo: find_open_pr(repo, batch.branch, cfg.base_branch) for repo in titles}
    prs: dict[str, int | None] = {repo: (pr["number"] if pr else None) for repo, pr in existing.items()}

    # Create any missing PRs first, so that both descriptions can link to each other
    for repo, title in titles.items():
        if prs[repo] is not None:
            continue

        ensure_branch_has_commit(repo, batch.branch, cfg.base_branch, cfg.dry_run)
        print(f"  {repo}: open {'draft ' if cfg.draft else ''}PR `{batch.branch}` -> `{cfg.base_branch}`: {title!r}")
        if not cfg.dry_run:
            pr = gh_api(
                f"repos/{repo}/pulls",
                method="POST",
                body={
                    "title": title,
                    "head": batch.branch,
                    "base": cfg.base_branch,
                    "body": pr_body(cfg, batch, regs, repo, prs),
                    "draft": cfg.draft,
                },
            )
            prs[repo] = pr["number"]
            print(f"    created {pr['html_url']}")

    for repo in titles:
        body = pr_body(cfg, batch, regs, repo, prs)
        if cfg.dry_run:
            print(f"\n----- {repo} PR description -----\n{body}\n-----")
            continue

        current = gh_api(f"repos/{repo}/pulls/{prs[repo]}")
        if (current.get("body") or "") != body:
            print(f"  {repo}: update the description of #{prs[repo]}")
            gh_api(f"repos/{repo}/pulls/{prs[repo]}", method="PATCH", body={"body": body})

    for repo in titles:
        post_review_handles_comment(cfg, regs, repo, prs[repo])


def review_handles_comment(cfg: Config, regs: list[Registration]) -> str:
    handles = sorted({r.author for r in regs} - set(cfg.extra_mentions), key=str.lower) + list(cfg.extra_mentions)
    # Inside a code span, so that nobody is notified until the handles are copied out
    return f"{REVIEW_HANDLES_PREFIX} `{' '.join(f'@{h}' for h in handles)}`"


def post_review_handles_comment(cfg: Config, regs: list[Registration], repo: str, pr_number: int | None) -> None:
    """
    Comment the handles to tag for review, rather than tagging them directly,
    so that the batch can be checked before anyone is notified.
    A new comment is only posted if the handles changed since the last one.
    """
    comment = review_handles_comment(cfg, regs)
    if pr_number is None:
        print(f"  {repo}: comment on the new PR: {comment}")
        return

    previous = [
        c["body"]
        for c in gh_api_paginated(f"repos/{repo}/issues/{pr_number}/comments")
        if c["body"].startswith(REVIEW_HANDLES_PREFIX)
    ]
    if previous and previous[-1] == comment:
        print(f"  {repo}: review handles comment on #{pr_number} is up to date")
        return

    print(f"  {repo}: comment on #{pr_number}: {comment}")
    if not cfg.dry_run:
        gh_api(f"repos/{repo}/issues/{pr_number}/comments", method="POST", body={"body": comment})


# --------------------------------------------------------------------------- #
def process_batch(cfg: Config, batch: Batch, issues: list[dict[str, Any]], all_pulls: list[dict[str, Any]]) -> None:
    print(f"\n===== Batch `{batch.branch}` ({', '.join(batch.mips)}) =====")

    print("Step 1: branches")
    for repo in (cfg.cvs_repo, cfg.universe_repo):
        ensure_branch(repo, batch.branch, cfg.base_branch, cfg.dry_run)

    print("Step 2: registration issues")
    regs = find_registrations(cfg, batch, issues, all_pulls)
    if not regs:
        print("  no open registration issues found, nothing to do")
        return
    for reg in regs:
        outcome = f"automated, bot PR #{reg.bot_pr} ({reg.bot_pr_state})" if reg.automated else f"BY HAND: {reg.reason}"
        print(f"  #{reg.issue} {reg.kind} `{reg.name}` by {reg.author}: {outcome}")

    print("Step 3a: retarget and merge bot PRs")
    retarget_and_merge(cfg, batch, regs, all_pulls)

    print("Step 3b: note failed registrations in the universe generator")
    update_generator_note(cfg, batch, regs)

    print("Step 4: batch PRs")
    sync_batch_prs(cfg, batch, regs)


def main() -> None:
    cfg = Config(
        cvs_repo="WCRP-CMIP/CMIP7-CVs",
        universe_repo="WCRP-CMIP/WCRP-universe",
        base_branch="esgvoc_dev",
        generator_path="scripts/generate-cmip7-experiments.py",
        extra_mentions=("CMIP-IPO", "znichollscr"),
        # Set to False to actually make the changes
        dry_run=True,
        # Open the batch PRs as drafts so they aren't merged before the final review
        draft=True,
    )
    batches = [
        Batch(branch="c4mip", mips=("c4mip",), label="C4MIP"),
        Batch(branch="damip", mips=("damip",), label="DAMIP"),
        Batch(branch="highresmip", mips=("highresmip",), label="HighResMIP"),
        Batch(branch="irrmip", mips=("irrmip",), label="IRRMIP"),
        Batch(branch="cfmip", mips=("cfmip",), label="CFMIP"),
        Batch(branch="tipmip", mips=("tipmip",), label="TIPMIP"),
    ]

    print("DRY RUN, nothing will be written" if cfg.dry_run else "LIVE RUN")
    issues = [i for i in gh_api_paginated(f"repos/{cfg.cvs_repo}/issues?state=open") if "pull_request" not in i]
    all_pulls = gh_api_paginated(f"repos/{cfg.cvs_repo}/pulls?state=all")
    print(f"Found {len(issues)} open issues and {len(all_pulls)} PRs in {cfg.cvs_repo}")

    for batch in batches:
        process_batch(cfg, batch, issues, all_pulls)


if __name__ == "__main__":
    main()
