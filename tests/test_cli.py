import json
from pathlib import Path

import pytest
from click.testing import CliRunner

from ocrvid.cli import cli


# testing the cli, key command group
def test_lang_command():
    runner = CliRunner()
    result = runner.invoke(cli, ["langs"])

    assert result.exit_code == 0
    assert result.output != ""


@pytest.fixture
def input_file():
    return str(Path(__file__).parent / "video/pexels-eva-elijas.mp4")


def test_props_command(input_file):
    runner = CliRunner()
    with runner.isolated_filesystem():
        result = runner.invoke(cli, ["props", input_file])

        assert result.exit_code == 0
        assert result.output != ""


def test_run_command_with_frames_dir(input_file):
    runner = CliRunner()
    with runner.isolated_filesystem():
        frames_dir_str = ".ocrvid/frames/pexels-eva-elijas"
        result = runner.invoke(cli, ["run", input_file, "-fd", frames_dir_str])

        assert result.exit_code == 0
        assert (Path.cwd() / "pexels-eva-elijas.json").exists()
        assert (Path.cwd() / frames_dir_str).is_dir()

        result = runner.invoke(cli, ["detect", f"{frames_dir_str}/frame-0.png"])
        assert result.exit_code == 0
        assert result.output != ""


def test_run_command_with_custom_path(input_file):
    runner = CliRunner()
    with runner.isolated_filesystem():
        result = runner.invoke(
            cli,
            ["run", input_file, "-o", "some/custom.json", "-fd", "custom-frame-dir"],
        )

        assert result.exit_code == 0
        assert (Path.cwd() / "some/custom.json").exists()
        assert (Path.cwd() / "custom-frame-dir").is_dir()


def test_run_command_with_by_second(input_file):
    runner = CliRunner()
    with runner.isolated_filesystem():
        result = runner.invoke(cli, ["run", input_file, "-bs", "1"])

        assert result.exit_code == 0
        assert (Path.cwd() / "pexels-eva-elijas.json").exists()

        with open(Path.cwd() / "pexels-eva-elijas.json") as f:
            data = json.load(f)
            assert len(data["frames"]) == 24  # 24 seconds in the video
