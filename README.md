# ocrvid

[![PyPI](https://img.shields.io/pypi/v/ocrvid.svg)](https://pypi.org/project/ocrvid/)
[![Changelog](https://img.shields.io/github/v/release/kj-9/ocrvid?include_prereleases&label=changelog)](https://github.com/kj-9/ocrvid/releases)
[![Tests](https://github.com/kj-9/ocrvid/workflows/CI/badge.svg)](https://github.com/kj-9/ocrvid/actions?query=workflow%3ACI)
[![License](https://img.shields.io/badge/license-Apache%202.0-blue.svg)](https://github.com/kj-9/ocrvid/blob/master/LICENSE)


CLI tool to extract text from videos using OCR on macOS.


> [!NOTE]
> Currently, this tool only tested and works on macOS 13 or later.


> [!CAUTION]
> This tool is still in early development stage. Current v0.x releases are not stable and may have breaking changes.

## Installation

Install this tool using `pip`:

    pip install ocrvid


## Usage

<!-- [[[cog
import cog
from ocrvid import cli
from click.testing import CliRunner
runner = CliRunner()
result = runner.invoke(cli.cli, ["--help"])
help = result.output.replace("Usage: cli", "Usage: ocrvid")
cog.out(
    f"```\n{help}\n```"
)
]]] -->
```
Usage: ocrvid [OPTIONS] COMMAND [ARGS]...

Options:
  --version  Show the version and exit.
  --help     Show this message and exit.

Commands:
  detect  Run OCR on a single picture, and print the results as json
  langs   Show supported recognition languages
  props   Show properties of video file
  run     Run OCR on a video, and save result as a json file

```
<!-- [[[end]]] -->

### Run OCR on a video

Use `ocr run` sub command to run ocr on a video file:

<!-- [[[cog
runner = CliRunner()
result = runner.invoke(cli.cli, ["run", "--help"])
help = result.output.replace("Usage: cli", "Usage: ocrvid")
cog.out(
    f"```\n{help}\n```"
)
]]] -->
```
Usage: ocrvid run [OPTIONS] INPUT_VIDEO

  Run OCR on a video, and save result as a json file

Options:
  -o, --output FILE            Path to output json file. By default, if you run
                               `ocrvid run some/video.mp4` then the output file
                               will be `./video.json`
  -fd, --frames-dir DIRECTORY  If passed, then save video frames to this
                               directory. By default, frames are not saved.
  -fs, --frame-step INTEGER    Number of frames to skip between each frame to be
                               processed. By default, 100 which means every 100
                               frames, 1 frame will be processed.
  -bs, --by-second FLOAT       If passed, then process 1 frame every N seconds.
                               This option relies on fps metadata of the video.
  -l, --langs TEXT             Prefered languages to detect, ordered by
                               priority. See avalable languages run by `ocrvid
                               langs`. If not passed, language is auto detected.
  --help                       Show this message and exit.

```
<!-- [[[end]]] -->

For example, run against the test video file at `tests/video/pexels-eva-elijas.mp4` in this repo:

```
ocrvid run tests/video/pexels-eva-elijas.mp4
```

Then `pexels-eva-elija.json` is generated in the current directory which looks like this:

```json
{
    "video_file":"tests/video/pexels-eva-elijas.mp4",
    "frames":[
        {
            "frame_index":0,
            "results":[
                {
                    "text":"INSPIRING WORDS",
                    "confidence":1.0,
                    "bbox":[
                        0.17844826551211515,
                        0.7961793736859821,
                        0.3419540405273438,
                        0.10085802570754931
                    ]
                },
                {
                    "text":"\"Foar kills more dre",
                    "confidence":1.0,
                    "bbox":[
                        0.0724226723609706,
                        0.6839455987759758,
                        0.4780927975972494,
                        0.14592710683043575
                    ]
                },
                {
                    "text":"than failure ever",
                    "confidence":1.0,
                    "bbox":[
                        0.018455287246445035,
                        0.6549868414269003,
                        0.45329265594482426,
                        0.14363905857426462
                    ]
                },
                {
                    "text":"IZY KASSEM",
                    "confidence":0.5,
                    "bbox":[
                        -0.015967150208537523,
                        0.6675747977206025,
                        0.23065692583719888,
                        0.08114868486431293
                    ]
                },
                {
                    "text":"Entrepreneur",
                    "confidence":1.0,
                    "bbox":[
                        0.01941176222542875,
                        0.1353812367971159,
                        0.9058370590209961,
                        0.26137274083956863
                    ]
                }
            ]
        },
...
```


### Show supported languages

You can run `ocrvid langs` to show supported languages to detect.
Results can be different from your macos version.

On macOS version:
<!-- [[[cog
import platform
cog.out(
    f"""```\n{platform.mac_ver()[0]=}\n```""")
]]] -->
```
platform.mac_ver()[0]='14.2.1'
```
<!-- [[[end]]] -->


Result of `ocrvid langs`:
<!-- [[[cog
runner = CliRunner()
result = runner.invoke(cli.cli, ["langs"])
help = result.output.replace("Usage: cli", "Usage: ocrvid")
cog.out(
    f"```\n{help}\n```"
)
]]] -->
```
en-US
fr-FR
it-IT
de-DE
es-ES
pt-BR
zh-Hans
zh-Hant
yue-Hans
yue-Hant
ko-KR
ja-JP
ru-RU
uk-UA
th-TH
vi-VT

```
<!-- [[[end]]] -->

## How can I run OCR on YouTube videos?

Take a look at [yt-dlp](https://github.com/yt-dlp/yt-dlp).


## Development

To contribute to this tool, first checkout the code. Then create a new virtual environment:

    cd ocrvid
    python -m venv venv
    source venv/bin/activate

Now install the dependencies and test dependencies:

    pip install -e '.[test,dev]'

To run the tests:

    make test
