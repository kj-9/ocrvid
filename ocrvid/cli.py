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
    type=click.Path(dir_okay=False, writable=True),
    help="Path to output json file. By default, if you run `ocrvid run some/video.mp4` then the output file will be `./video.json`",
)
@click.option(
    "--frames-dir",
    "-fd",
    type=click.Path(file_okay=False, writable=True),
    help="Directory to store frames. By default, `./.ocrvid/frames/{stem of output json}`",
)
@click.option(
    "--frame-step",
    "-fs",
    default=100,
    type=int,
    help="Number of frames to skip between each frame to be processed. By default, 100 which means every 100 frames, 1 frame will be processed.",
)
@click.option(
    "--langs",
    "-l",
    default=None,
    multiple=True,
    type=str,
    help="Prefered languages to detect, ordered by priority. See avalable languages run by `ocrvid langs`. If not passed, language is auto detected.",
)
def run_ocr(input_video, output, frames_dir, frame_step, langs):  # noqa: PLR0913
    """Write a ocr json file from a video file"""

    if output:
        output = Path(output)
        # if output is not passed, then use the same file name as the input video
        # but with a json extension, and in output to the current directory
    else:
        output = Path.cwd() / Path(input_video).with_suffix(".json").name

    if frames_dir:
        frames_dir = Path(frames_dir)
    else:
        frames_dir = Path.cwd() / ".ocrvid/frames" / output.stem

    video = Video(
        output_file=Path(output),
        video_file=Path(input_video),
        frames_dir=Path(frames_dir),
        frame_step=frame_step,
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
