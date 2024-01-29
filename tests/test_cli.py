from pathlib import Path

from click.testing import CliRunner

from ocrvid.cli import cli


# testing the cli, key command group
def test_lang_command():
    runner = CliRunner()
    result = runner.invoke(cli, ["langs"])

    assert result.exit_code == 0
    assert result.output != ""


def test_run_command_with_frames_dir():
    runner = CliRunner()
    with runner.isolated_filesystem():
        input_file = str(Path(__file__).parent / "video/pexels-eva-elijas.mp4")
        frames_dir_str = ".ocrvid/frames/pexels-eva-elijas"
        result = runner.invoke(cli, ["run", input_file, "-fd", frames_dir_str])

        assert result.exit_code == 0
        assert (Path.cwd() / "pexels-eva-elijas.json").exists()
        assert (Path.cwd() / frames_dir_str).is_dir()

        result = runner.invoke(cli, ["detect", f"{frames_dir_str}/frame-0.png"])
        assert result.exit_code == 0
        assert result.output != ""


def test_run_command_with_custom_path():
    runner = CliRunner()
    with runner.isolated_filesystem():
        input_file = str(Path(__file__).parent / "video/pexels-eva-elijas.mp4")
        result = runner.invoke(
            cli,
            ["run", input_file, "-o", "some/custom.json", "-fd", "custom-frame-dir"],
        )

        assert result.exit_code == 0
        assert (Path.cwd() / "some/custom.json").exists()
        assert (Path.cwd() / "custom-frame-dir").is_dir()
