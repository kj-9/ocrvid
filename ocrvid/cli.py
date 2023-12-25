import json
from pathlib import Path

import click

from ocrvid import key_path
from ocrvid.playlist import Playlist
from ocrvid.video import Video


@click.group()
@click.version_option()
def cli():
    """"""


@cli.group()
def key():
    "Manage stored Youtube API key"


@key.command(name="path")
def key_path_command():
    "Output the path to the .ocrvid.json file"
    click.echo(key_path())


@key.command(name="set")
@click.argument("value", required=True, type=str)
def key_set(value):
    """
    Save a key in the .ocrvid.json file
    """
    default = {"// Note": "This file stores secret API credentials. Do not share!"}
    path = key_path()
    path.parent.mkdir(parents=True, exist_ok=True)
    if not path.exists():
        path.write_text(json.dumps(default))
    try:
        current = json.loads(path.read_text())
    except json.decoder.JSONDecodeError:
        current = default
    current["YOUTUBE_API_KEY"] = value
    path.write_text(json.dumps(current, indent=2) + "\n")


@cli.group()
def youtube():
    "Manage Youtube resources"


@youtube.command(name="playlist")
@click.argument("playlist_id", required=True, type=str)
@click.option(
    "-n",
    "--name",
    type=str,
    help="Specify the file name",
)
@click.option(
    "-d",
    "--directory",
    type=click.Path(file_okay=False, writable=True),
    help="Specify the directory to save the file",
)
@click.option(
    "-f",
    "--force",
    is_flag=True,
    default=False,
    help="Overwrite the file if it already exists",
)
def write_playlist(playlist_id, name, directory, force):
    """Write a playlist to a json file"""
    if not name:
        name = f"playlist-{playlist_id}.json"

    if not directory:
        directory = "."

    output_path = Path(directory) / name

    if output_path.exists() and not force:
        click.echo(f"{output_path} already exists. Use -f to overwrite")
        return

    playlist = Playlist(playlist_id)
    playlist.get_playlist()

    playlist.to_json(output_path)


@youtube.command(name="ls")
@click.argument("video_id", required=True, type=str)
def get_resolutions(video_id):
    """Get resolutions for a video"""
    resolutions = Video.get_resolutions(video_id)
    for resolution in resolutions:
        click.echo(resolution)


@youtube.command(name="download")
@click.argument("video_id", required=True, type=str)
@click.option(
    "-n",
    "--name",
    type=str,
    help="Specify the file name",
)
@click.option(
    "-d",
    "--directory",
    type=click.Path(file_okay=False, writable=True),
    help="Specify the directory to save the file",
)
@click.option(
    "-f",
    "--force",
    is_flag=True,
    default=False,
    help="Overwrite the file if it already exists",
)
@click.option(
    "--resolution",
    "--res",
    default="worst",
    type=str,
    help="Resolution of the video to download. worst/best or a itag. Use `ocrvid video resolutions` to get a list of itags",
)
def download_video(video_id, name, directory, force, resolution):
    """Download a video"""
    if not name:
        name = f"{video_id}.{resolution}.mp4"

    if not directory:
        directory = "."

    output_path = Path(directory) / name

    if output_path.exists() and not force:
        click.echo(f"{output_path} already exists. Use -f to overwrite")
        return

    video = Video(video_file=output_path)
    video.download_video(video_id, resolution=resolution)


@cli.command(name="run")
@click.argument(
    "input_video", required=True, type=click.Path(dir_okay=False, writable=True)
)
@click.option(
    "--directory",
    "-d",
    default=".",
    type=click.Path(file_okay=False, writable=True),
    help="Directory to save the output file",
)
@click.option(
    "--frames-dir",
    "-fd",
    type=click.Path(file_okay=False, writable=True),
    help="Directory to store frames",
)
@click.option(
    "--frame-rate",
    "-fr",
    default=100,
    type=int,
    help="Number of frames per second to extract from the video",
)
def run_ocr(input_video, directory, frames_dir, frame_rate):
    """Write a ocr json file from a video file"""
    output_file = Path(directory) / "video.json"

    if not frames_dir:
        frames_dir = Path(directory) / ".frames"

    video = Video(
        output_file=Path(output_file),
        video_file=Path(input_video),
        frames_dir=Path(frames_dir),
        frame_rate=frame_rate,
    )
    video.gen_frame_files()
    video.run_ocr()
    video.to_json()

@cli.command(name="langs")
def echo_supported_recognition_languages():
    """Show supported recognition languages"""
    import ocrvid.ocr

    for lang in ocrvid.ocr.supported_recognition_languages():
        click.echo(lang)
