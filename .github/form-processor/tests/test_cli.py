"""Tests for the Typer command-line interface."""

import json

from typer.testing import CliRunner

from github_form_processor.cli import _process_edited_issue, _process_opened_issue, app
from github_form_processor.processor import RegistrationPreparationResult


def test_process_accepts_output_directories_as_options(tmp_path, monkeypatch):
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
            "--experiment-output-dir",
            "custom-experiments",
            "--activity-output-dir",
            "custom-activities",
            "--wcrp-universe-url",
            "https://example.test/wcrp-universe/custom",
            "--cmip7-cvs-url",
            "https://example.test/cmip7-cvs/custom",
            "--cmip7-cvs-path",
            str(tmp_path),
        ],
    )

    assert result.exit_code == 0
    assert call["experiment_output_dir"] == "custom-experiments"
    assert call["activity_output_dir"] == "custom-activities"
    assert call["cv_client"].wcrp_universe_url == (
        "https://example.test/wcrp-universe/custom"
    )
    assert call["cv_client"].cmip7_cvs_url == "https://example.test/cmip7-cvs/custom"
    assert call["cv_client"].cmip7_cvs_path == tmp_path.resolve()


def test_opened_issue_raises_if_target_file_exists():
    client = FakeDuplicateFileClient()
    prepared = FakePreparedRegistration()

    try:
        _process_opened_issue(
            client=client,
            issue_number=1,
            base_branch="esgvoc_dev",
            branch="registration/experiment-1-existing",
            prepared=prepared,
        )
    except RuntimeError as exc:
        assert "already exists" in str(exc)
    else:
        raise AssertionError("Expected RuntimeError")

    assert client.comments == [
        (
            1,
            "### Registration form validation failed\n"
            "\n"
            "The issue form could not be processed. Please edit the issue body "
            "and save the changes.\n"
            "\n"
            "- Target file `experiment/existing.json` already exists on "
            "`esgvoc_dev`.",
        )
    ]


def test_opened_issue_targets_esgvoc_dev():
    client = FakeOpenedIssueClient()
    prepared = FakePreparedRegistration()
    prepared.output_path = "experiment/new.json"
    prepared.pull_request_title = "Test registration"
    prepared.commit_message = "Add registration"
    prepared.content = "{}"

    result = _process_opened_issue(
        client=client,
        issue_number=1,
        base_branch="esgvoc_dev",
        branch="registration/experiment-1-new",
        prepared=prepared,
    )

    assert result == 0
    assert client.calls == [
        ("content_exists", "experiment/new.json", "esgvoc_dev"),
        ("branch_exists", "registration/experiment-1-new"),
        ("get_ref_sha", "esgvoc_dev"),
        ("create_branch", "registration/experiment-1-new", "sha-esgvoc_dev"),
        ("put_file", "experiment/new.json", "registration/experiment-1-new"),
        ("create_pull_request", "registration/experiment-1-new", "esgvoc_dev"),
        ("assign_issue", 10, ["znichollscr", "ltroussellier"]),
        ("comment_issue", 1),
    ]


def test_edited_issue_raises_if_multiple_open_pull_requests_exist():
    client = FakeMultipleOpenPullsClient()
    prepared = FakePreparedRegistration()

    try:
        _process_edited_issue(
            client=client,
            issue_number=1,
            branch="registration/experiment-1-existing",
            prepared=prepared,
        )
    except RuntimeError as exc:
        assert "#2, #3" in str(exc)
    else:
        raise AssertionError("Expected RuntimeError")

    assert client.comments == [
        (
            1,
            "### Registration form processing failed\n"
            "\n"
            "Multiple open registration pull requests were found for this issue: "
            "#2, #3. Please close the duplicates before editing the registration "
            "issue again.",
        )
    ]


def test_edited_issue_raises_if_no_open_pull_request_exists():
    client = FakeNoOpenPullsClient()
    prepared = FakePreparedRegistration()

    try:
        _process_edited_issue(
            client=client,
            issue_number=1,
            branch="registration/experiment-1-existing",
            prepared=prepared,
        )
    except RuntimeError as exc:
        assert "No open registration pull request" in str(exc)
    else:
        raise AssertionError("Expected RuntimeError")

    assert client.comments == [
        (
            1,
            "### Registration form processing failed\n"
            "\n"
            "No open registration pull request was found for branch "
            "`registration/experiment-1-existing`. Please open a new registration "
            "issue.",
        )
    ]


class FakeDuplicateFileClient:
    def __init__(self):
        self.comments = []

    def content_exists(self, path, branch):
        assert path == "experiment/existing.json"
        assert branch == "esgvoc_dev"
        return True

    def comment_issue(self, issue_number, body):
        self.comments.append((issue_number, body))


class FakePreparedRegistration:
    output_path = "experiment/existing.json"
    kind = "experiment"
    pull_request_title = "Test registration"
    commit_message = "Add registration"
    content = "{}"

    def __init__(self):
        self.notes = []


class FakeMultipleOpenPullsClient:
    def __init__(self):
        self.comments = []

    def find_pull_requests_for_branch(self, branch):
        assert branch == "registration/experiment-1-existing"
        return [
            {"number": 2, "state": "open"},
            {"number": 3, "state": "open"},
        ]

    def comment_issue(self, issue_number, body):
        self.comments.append((issue_number, body))


class FakeOpenedIssueClient:
    def __init__(self):
        self.calls = []

    def content_exists(self, path, branch):
        self.calls.append(("content_exists", path, branch))
        return False

    def branch_exists(self, branch):
        self.calls.append(("branch_exists", branch))
        return False

    def get_ref_sha(self, branch):
        self.calls.append(("get_ref_sha", branch))
        return f"sha-{branch}"

    def create_branch(self, branch, sha):
        self.calls.append(("create_branch", branch, sha))

    def put_file(self, path, branch, content, message):
        self.calls.append(("put_file", path, branch))

    def create_pull_request(self, title, head, base, body):
        self.calls.append(("create_pull_request", head, base))
        return {"number": 10, "html_url": "https://example.test/pr/10"}

    def assign_issue(self, issue_number, assignees):
        self.calls.append(("assign_issue", issue_number, assignees))

    def comment_issue(self, issue_number, body):
        self.calls.append(("comment_issue", issue_number))


class FakeNoOpenPullsClient:
    def __init__(self):
        self.comments = []

    def find_pull_requests_for_branch(self, branch):
        assert branch == "registration/experiment-1-existing"
        return []

    def find_pull_requests_for_issue(self, issue_number):
        assert issue_number == 1
        return []

    def comment_issue(self, issue_number, body):
        self.comments.append((issue_number, body))
