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
            default_branch="main",
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
            "- Target file `experiment/existing.json` already exists on `main`.",
        )
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


class FakeDuplicateFileClient:
    def __init__(self):
        self.comments = []

    def content_exists(self, path, branch):
        assert path == "experiment/existing.json"
        assert branch == "main"
        return True

    def comment_issue(self, issue_number, body):
        self.comments.append((issue_number, body))


class FakePreparedRegistration:
    output_path = "experiment/existing.json"

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
