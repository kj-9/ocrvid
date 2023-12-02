# ocrvid

[![PyPI](https://img.shields.io/pypi/v/ocrvid.svg)](https://pypi.org/project/ocrvid/)
[![Changelog](https://img.shields.io/github/v/release/kj-9/ocrvid?include_prereleases&label=changelog)](https://github.com/kj-9/ocrvid/releases)
[![Tests](https://github.com/kj-9/ocrvid/workflows/Test/badge.svg)](https://github.com/kj-9/ocrvid/actions?query=workflow%3ATest)
[![License](https://img.shields.io/badge/license-Apache%202.0-blue.svg)](https://github.com/kj-9/ocrvid/blob/master/LICENSE)


CLI tool to extract text from videos using OCR on macOS.




## Installation

Install this tool using `pip`:

    pip install ocrvid

## Usage

### Run OCR on a video

To extract text from a video, run:

    ocrvid run path/to/video.mp4

then ocrvid generates frames from the video and runs OCR on each frame. Frames are saved in a directory named `.frames/` in the same directory as the video. 

The text is saved in a json file named `video.json` in the same directory as the video.
`video.json` looks like this:

```json
{
    "video_file":"data/43TjPJ88xWU-worst.mp4",
    "frames_dir":"data/.frames",
    "frame_rate":100,
    "frames":[
        {
            "frame_file":"data/.frames/frame-300.png",
            "results":[
                {
                    "text":"目的地",
                    "confidence":0.5,
                    "bbox":[
                        0.34375000234374997,
                        0.6944444452380952,
                        0.328125,
                        0.2222222222222222
                    ]
                },
                {
                    "text":"福岡市博多区",
                    "confidence":1.0,
                    "bbox":[
                        0.062203050380895686,
                        0.38636815776546085,
                        0.852156400680542,
                        0.3244859112633599
                    ]
                },}
...
```


### Interact with YouTube

`orcvid` has some commands to interact with YouTube.

To download a YouTube video without audio, run:

    ocrvid youtube $video_id


To get information about a YouTube plalylist from YouTube API, 
you need to set `YOUTUBE_API_KEY` environment variable or store key by running:
    
    ocrvid key set $key
    
You can see the path of the key file by running:
    
    ocrvid key path


Once you set the key, you can run:

    ocrvid youtube playlist $playlist_id

This saves the information about the playlist in a json file named `playlist-{playlist_id}.json` in the current directory.


## Development

To contribute to this tool, first checkout the code. Then create a new virtual environment:

    cd ocrvid
    python -m venv venv
    source venv/bin/activate

Now install the dependencies and test dependencies:

    pip install -e '.[test,dev]'

To run the tests:

    make test
