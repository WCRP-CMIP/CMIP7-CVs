"""Tests for the Typer command-line interface."""

import json

import pytest
from typer.testing import CliRunner

from github_form_processor.cli import (
    RepoTarget,
    _process_registration,
    app,
    repository_slug,
)
from github_form_processor.github_api import GitHubApiError
from github_form_processor.processor import (
    PreparedRegistration,
    RegistrationOutput,
    RegistrationPreparationResult,
)

CMIP7_REPO = "WCRP-CMIP/CMIP7-CVs"
UNIVERSE_REPO = "WCRP-CMIP/WCRP-universe"


def test_process_accepts_repository_and_directory_options(tmp_path, monkeypatch):
    event_path = tmp_path / "event.json"
    event_path.write_text(
        json.dumps(
            {
                "action": "opened",
                "issue": {
                    "number": 1,
                    "title": "[Experiment registration]: Test",
                    "labels": [{"name": "registration: experiment"}],
                    "body": "",
                },
                "repository": {"default_branch": "main"},
            }
        )
    )
    call = {}

    def fake_prepare_registration(**kwargs):
        call.update(kwargs)
        return RegistrationPreparationResult(
            prepared=None,
            validation_errors=[],
            notes=[],
        )

    monkeypatch.setattr(
        "github_form_processor.cli.prepare_registration",
        fake_prepare_registration,
    )

    result = CliRunner().invoke(
        app,
        [
            "--event-path",
            str(event_path),
            "--cmip7-repository",
            "https://github.com/WCRP-CMIP/CMIP7-CVs",
            "--universe-repository",
            "https://github.com/WCRP-CMIP/WCRP-universe",
            "--universe-base-branch",
            "esgvoc_dev",
            "--experiment-output-dir",
            "custom-experiments",
            "--activity-output-dir",
            "custom-activities",
            "--institution-output-dir",
            "custom-institutions",
            "--universe-organisation-dir",
            "custom-organisations",
            "--universe-institution-dir",
            "custom-members",
            "--cmip7-cvs-url",
            "https://example.test/cmip7-cvs/custom",
            "--cmip7-cvs-path",
            str(tmp_path),
        ],
    )

    assert result.exit_code == 0
    # Full URLs are normalised to owner/name slugs.
    assert call["cmip7_repository"] == CMIP7_REPO
    assert call["universe_repository"] == UNIVERSE_REPO
    assert call["experiment_output_dir"] == "custom-experiments"
    assert call["activity_output_dir"] == "custom-activities"
    assert call["institution_output_dir"] == "custom-institutions"
    assert call["universe_organisation_dir"] == "custom-organisations"
    assert call["universe_institution_dir"] == "custom-members"
    # The universe CV URL is derived from the universe repository and base branch.
    assert call["cv_client"].wcrp_universe_url == (
        "https://raw.githubusercontent.com/WCRP-CMIP/WCRP-universe/esgvoc_dev"
    )
    assert call["cv_client"].cmip7_cvs_url == "https://example.test/cmip7-cvs/custom"
    assert call["cv_client"].cmip7_cvs_path == tmp_path.resolve()


@pytest.mark.parametrize(
    ("value", "expected"),
    [
        ("WCRP-CMIP/WCRP-universe", "WCRP-CMIP/WCRP-universe"),
        ("https://github.com/WCRP-CMIP/WCRP-universe", "WCRP-CMIP/WCRP-universe"),
        ("https://github.com/WCRP-CMIP/WCRP-universe/", "WCRP-CMIP/WCRP-universe"),
        ("https://github.com/WCRP-CMIP/WCRP-universe.git", "WCRP-CMIP/WCRP-universe"),
    ],
)
def test_repository_slug_normalises_urls_and_slugs(value, expected):
    assert repository_slug(value) == expected


def test_repository_slug_rejects_unparseable_value():
    with pytest.raises(ValueError, match="repository slug"):
        repository_slug("not-a-repository")


def test_opened_registration_opens_single_pull_request():
    client = FakeClient(CMIP7_REPO)
    prepared = _make_prepared()

    result = _process_registration(
        action="opened",
        issue_client=client,
        issue_number=1,
        branch="registration/experiment-1-new",
        prepared=prepared,
        targets={CMIP7_REPO: RepoTarget(client=client, base_branch="esgvoc_dev")},
    )

    assert result == 0
    assert ("content_exists", "experiment/new.json", "esgvoc_dev") in client.calls
    assert ("create_branch", "registration/experiment-1-new", "sha-esgvoc_dev") in (
        client.calls
    )
    assert ("put_file", "experiment/new.json", "registration/experiment-1-new") in (
        client.calls
    )
    create_call = _find_call(client, "create_pull_request")
    assert create_call[1] == "registration/experiment-1-new"
    assert create_call[2] == "esgvoc_dev"
    assert "Closes #1" in create_call[3]
    assert ("assign_issue", 10, ["znichollscr", "ltroussellier"]) in client.calls
    assert len(client.comments) == 1
    assert "pull request #10" in client.comments[0][1]
    assert f"`{CMIP7_REPO}`" in client.comments[0][1]


def test_opened_registration_raises_if_target_file_exists():
    client = FakeClient(CMIP7_REPO, existing_paths={"experiment/new.json"})
    prepared = _make_prepared()

    with pytest.raises(RuntimeError, match="already exists"):
        _process_registration(
            action="opened",
            issue_client=client,
            issue_number=1,
            branch="registration/experiment-1-new",
            prepared=prepared,
            targets={CMIP7_REPO: RepoTarget(client=client, base_branch="esgvoc_dev")},
        )

    assert len(client.comments) == 1
    assert "already exists" in client.comments[0][1]


def test_edited_registration_raises_if_multiple_open_pull_requests_exist():
    client = FakeClient(
        CMIP7_REPO,
        pulls_for_branch=[
            {"number": 2, "state": "open"},
            {"number": 3, "state": "open"},
        ],
    )
    prepared = _make_prepared()

    with pytest.raises(RuntimeError, match="#2, #3"):
        _process_registration(
            action="edited",
            issue_client=client,
            issue_number=1,
            branch="registration/experiment-1-new",
            prepared=prepared,
            targets={CMIP7_REPO: RepoTarget(client=client, base_branch="esgvoc_dev")},
        )

    assert len(client.comments) == 1
    assert "#2, #3" in client.comments[0][1]


def test_edited_registration_opens_pull_request_when_none_exists():
    client = FakeClient(CMIP7_REPO)
    prepared = _make_prepared()

    result = _process_registration(
        action="edited",
        issue_client=client,
        issue_number=1,
        branch="registration/experiment-1-new",
        prepared=prepared,
        targets={CMIP7_REPO: RepoTarget(client=client, base_branch="esgvoc_dev")},
    )

    assert result == 0
    assert ("find_pull_requests_for_branch", "registration/experiment-1-new") in (
        client.calls
    )
    assert ("find_pull_requests_for_issue", 1) in client.calls
    assert _find_call(client, "create_pull_request") is not None


def test_edited_registration_updates_existing_pull_request():
    client = FakeClient(
        CMIP7_REPO,
        pulls_for_branch=[
            {
                "number": 7,
                "state": "open",
                "html_url": "https://example.test/pr/7",
                "head": {"ref": "registration/experiment-1-new"},
            }
        ],
    )
    prepared = _make_prepared()

    result = _process_registration(
        action="edited",
        issue_client=client,
        issue_number=1,
        branch="registration/experiment-1-new",
        prepared=prepared,
        targets={CMIP7_REPO: RepoTarget(client=client, base_branch="esgvoc_dev")},
    )

    assert result == 0
    assert ("put_file", "experiment/new.json", "registration/experiment-1-new") in (
        client.calls
    )
    assert ("assign_issue", 7, ["znichollscr", "ltroussellier"]) in client.calls
    assert _find_call(client, "create_pull_request") is None
    assert len(client.comments) == 1
    assert "Updated" in client.comments[0][1]


def test_institution_opens_one_pull_request_per_repository():
    issue_client = FakeClient(CMIP7_REPO, pr_number=21)
    universe_client = FakeClient(UNIVERSE_REPO, pr_number=20)
    prepared = PreparedRegistration(
        kind="institution",
        identifier="cnrm-cerfacs",
        outputs=[
            RegistrationOutput(
                repository=UNIVERSE_REPO,
                path="organisation/cnrm-cerfacs.json",
                content="{}",
            ),
            RegistrationOutput(
                repository=CMIP7_REPO,
                path="institution/cnrm-cerfacs.json",
                content="{}",
            ),
        ],
        pull_request_title="Register institution cnrm-cerfacs",
        commit_message="Register institution cnrm-cerfacs",
        notes=[],
    )

    result = _process_registration(
        action="opened",
        issue_client=issue_client,
        issue_number=1,
        branch="registration/institution-1-cnrm-cerfacs",
        prepared=prepared,
        targets={
            UNIVERSE_REPO: RepoTarget(client=universe_client, base_branch="main"),
            CMIP7_REPO: RepoTarget(client=issue_client, base_branch="esgvoc_dev"),
        },
    )

    assert result == 0

    universe_create = _find_call(universe_client, "create_pull_request")
    assert universe_create[2] == "main"
    assert f"Generated from {CMIP7_REPO}#1" in universe_create[3]
    assert ("put_file", "organisation/cnrm-cerfacs.json", universe_create[1]) in (
        universe_client.calls
    )

    cmip7_create = _find_call(issue_client, "create_pull_request")
    assert cmip7_create[2] == "esgvoc_dev"
    assert "Closes #1" in cmip7_create[3]

    # A single success comment is posted on the source issue, listing both PRs.
    assert len(issue_client.comments) == 1
    body = issue_client.comments[0][1]
    assert "pull request #20" in body
    assert "pull request #21" in body
    assert f"`{UNIVERSE_REPO}`" in body
    assert f"`{CMIP7_REPO}`" in body


def test_assignment_failure_does_not_abort_registration():
    client = FakeClient(CMIP7_REPO, assign_error=True)
    prepared = _make_prepared()

    result = _process_registration(
        action="opened",
        issue_client=client,
        issue_number=1,
        branch="registration/experiment-1-new",
        prepared=prepared,
        targets={CMIP7_REPO: RepoTarget(client=client, base_branch="esgvoc_dev")},
    )

    assert result == 0
    assert len(client.comments) == 1


def _make_prepared():
    return PreparedRegistration(
        kind="experiment",
        identifier="new",
        outputs=[
            RegistrationOutput(
                repository=CMIP7_REPO,
                path="experiment/new.json",
                content="{}",
            )
        ],
        pull_request_title="Register experiment new",
        commit_message="Register experiment new",
        notes=[],
    )


def _find_call(client, name):
    for call in client.calls:
        if call[0] == name:
            return call
    return None


class FakeClient:
    """Configurable fake GitHub client recording the calls made against it."""

    def __init__(
        self,
        repository,
        *,
        existing_paths=None,
        branch_exists=False,
        pulls_for_branch=None,
        pulls_for_issue=None,
        pr_number=10,
        assign_error=False,
    ):
        self.repository = repository
        self.calls = []
        self.comments = []
        self._existing = set(existing_paths or [])
        self._branch_exists = branch_exists
        self._pulls_for_branch = pulls_for_branch or []
        self._pulls_for_issue = pulls_for_issue or []
        self._pr_number = pr_number
        self._assign_error = assign_error

    def content_exists(self, path, branch):
        self.calls.append(("content_exists", path, branch))
        return path in self._existing

    def branch_exists(self, branch):
        self.calls.append(("branch_exists", branch))
        return self._branch_exists

    def get_ref_sha(self, branch):
        self.calls.append(("get_ref_sha", branch))
        return f"sha-{branch}"

    def create_branch(self, branch, sha):
        self.calls.append(("create_branch", branch, sha))

    def put_file(self, path, branch, content, message):
        self.calls.append(("put_file", path, branch))

    def delete_file(self, path, branch, message):
        self.calls.append(("delete_file", path, branch))

    def create_pull_request(self, title, head, base, body):
        self.calls.append(("create_pull_request", head, base, body))
        return {
            "number": self._pr_number,
            "html_url": f"https://example.test/pr/{self._pr_number}",
        }

    def find_pull_requests_for_branch(self, branch):
        self.calls.append(("find_pull_requests_for_branch", branch))
        return list(self._pulls_for_branch)

    def find_pull_requests_for_issue(self, issue_number):
        self.calls.append(("find_pull_requests_for_issue", issue_number))
        return list(self._pulls_for_issue)

    def assign_issue(self, issue_number, assignees):
        self.calls.append(("assign_issue", issue_number, assignees))
        if self._assign_error:
            raise GitHubApiError("assignment rejected")

    def comment_issue(self, issue_number, body):
        self.comments.append((issue_number, body))
