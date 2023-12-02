import json
import os
from pathlib import Path

from click.testing import CliRunner

from ocrvid import get_key
from ocrvid.cli import cli


# testing the cli, key command group
def test_key_path_command():
    runner = CliRunner()
    with runner.isolated_filesystem():
        result = runner.invoke(cli, ["key", "path"])
        assert result.exit_code == 0
        assert result.output == str(Path.home() / ".ocrvid.json") + "\n"

    with runner.isolated_filesystem():
        os.environ["ocrvid_USER_PATH"] = str(Path.home() / "ocrvid-test")
        result = runner.invoke(cli, ["key", "path"])
        assert result.exit_code == 0
        assert result.output == str(Path.home() / "ocrvid-test" / ".ocrvid.json") + "\n"


def test_keys_set_and_load():
    runner = CliRunner()
    with runner.isolated_filesystem():
        # set isolated filesystem as user dir
        os.environ["ocrvid_USER_PATH"] = str(Path.cwd())

        result = runner.invoke(cli, ["key", "set", "test_key"])
        assert result.exit_code == 0

        path = Path.cwd() / ".ocrvid.json"
        assert json.loads(path.read_text())["YOUTUBE_API_KEY"] == "test_key"
        assert get_key("YOUTUBE_API_KEY") == "test_key"

        # extract from env var
        os.environ["YOUTUBE_API_KEY"] = "test_key_env"
        assert get_key(None, env_var="YOUTUBE_API_KEY") == "test_key_env"
