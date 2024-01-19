from pathlib import Path

import click

from ocrvid.video import Video


@click.group()
@click.version_option()
def cli():
    """"""


@cli.command(name="run")
@click.argument(
    "input_video",
    required=True,
    type=click.Path(dir_okay=False, writable=True),
)
@click.option(
    "-o",
    "--output",
    default="video.json",
    type=click.STRING,
    help='Output json filename (without path). By default, the filename is "video.json"',
)
@click.option(
    "--directory",
    "-d",
    default=".",
    type=click.Path(file_okay=False, writable=True),
    help="Directory to save the output file. By default, the current directory is used",
)
@click.option(
    "--frames-dir",
    "-fd",
    type=click.Path(file_okay=False, writable=True),
    help="Directory to store frames. By default, a `.frames/` is created in the output directory",
)
@click.option(
    "--frame-rate",
    "-fr",
    default=100,
    type=int,
    help="Number of frames per second to extract from the video",
)
@click.option(
    "--langs",
    "-l",
    default=None,
    multiple=True,
    type=str,
    help="Prefered languages to detect, ordered by priority. See avalable languages run by `ocrvid langs`. If not passed, language is auto detected.",
)
def run_ocr(input_video, output, directory, frames_dir, frame_rate, langs):  # noqa: PLR0913
    """Write a ocr json file from a video file"""

    # validate output is just a filename
    if "/" in output:
        raise ValueError("output must be a filename, not a path")

    if not output.endswith(".json"):
        output += ".json"

    output_file = Path(directory) / output

    if not frames_dir:
        frames_dir = Path(directory) / ".frames"

    video = Video(
        output_file=Path(output_file),
        video_file=Path(input_video),
        frames_dir=Path(frames_dir),
        frame_rate=frame_rate,
    )
    video.gen_frame_files()
    video.run_ocr(langs=langs)
    video.to_json()


@cli.command(name="langs")
def echo_supported_recognition_languages():
    """Show supported recognition languages"""
    import ocrvid.ocr

    for lang in ocrvid.ocr.supported_recognition_languages():
        click.echo(lang)


@cli.command(name="detect")
@click.argument(
    "input_picture",
    required=True,
    type=click.Path(dir_okay=False),
)
@click.option(
    "--langs",
    "-l",
    default=None,
    multiple=True,
    type=str,
    help="Prefered languages to detect, ordered by priority. See avalable languages run by `ocrvid langs`. If not passed, language is auto detected.",
)
def detect_text(input_picture, langs):
    """Detect text in a picture, and print the results as json array"""
    from serde.json import to_json

    from ocrvid.ocr import detect_text

    results = detect_text(str(Path(input_picture)), languages=langs)

    # pretty print results
    click.echo(to_json(results, indent=4))
