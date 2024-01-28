# ocrvid

[![PyPI](https://img.shields.io/pypi/v/ocrvid.svg)](https://pypi.org/project/ocrvid/)
[![Changelog](https://img.shields.io/github/v/release/kj-9/ocrvid?include_prereleases&label=changelog)](https://github.com/kj-9/ocrvid/releases)
[![Tests](https://github.com/kj-9/ocrvid/workflows/CI/badge.svg)](https://github.com/kj-9/ocrvid/actions?query=workflow%3ACI)
[![License](https://img.shields.io/badge/license-Apache%202.0-blue.svg)](https://github.com/kj-9/ocrvid/blob/master/LICENSE)


CLI tool to extract text from videos using OCR on macOS.


> [!NOTE]
> Currently, this tool only tested and works on macOS 13 or later.


> [!CAUTION]
> This tool is still in early development stage. The API may change in the future.

## Installation

Install this tool using `pip`:

    pip install ocrvid


## Usage

### Run OCR on a video

To extract text from a video, run:

    ocrvid run path/to/video.mp4

then ocrvid generates frames from the video and runs OCR on each frame. Frames are saved in a directory named `.ocrvid/frames/video/` in the current directory.

OCR results are saved in a json file named `video.json` in the current directory. (where `video` is taken from input file name `video`)

for example, run against the test video file at `tests/video/pexels-eva-elijas.mp4` in this repo:

```
ocrvid run tests/video/pexels-eva-elijas.mp4
```

Then `pexels-eva-elija.json` is generated in the current directory which looks like this:

```json
{
    "video_file":"tests/video/pexels-eva-elijas.mp4",
    "frames_dir":"xxx/.ocrvid/frames/pexels-eva-elijas",
    "frame_step":100,
    "frames":[
        {
            "frame_file":"xxx/.ocrvid/frames/pexels-eva-elijas/frame-0.png",
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


### Interact with YouTube

Interacting YouTube? Please see [yt-dlp](https://github.com/yt-dlp/yt-dlp).


## Development

To contribute to this tool, first checkout the code. Then create a new virtual environment:

    cd ocrvid
    python -m venv venv
    source venv/bin/activate

Now install the dependencies and test dependencies:

    pip install -e '.[test,dev]'

To run the tests:

    make test
