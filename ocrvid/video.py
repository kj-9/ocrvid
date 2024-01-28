import typing as t
from dataclasses import dataclass
from pathlib import Path

import cv2
from serde import field, serde
from serde.json import to_json

from ocrvid.config import get_logger
from ocrvid.ocr import OCRResult, detect_text

logger = get_logger(__name__)


@serde
@dataclass
class Frame:
    frame_file: Path
    results: t.List[OCRResult]


# @serde
@dataclass
class Video:
    output_file: Path = field(default=None, skip=True)  # where to de/serialize
    video_file: t.Optional[Path] = None
    frames_dir: t.Optional[Path] = None
    frame_step: int = 100
    frames: t.List[Frame] = field(default_factory=list)

    frame_prefix: t.ClassVar[str] = "frame-"  # prefix for frame files

    def gen_frame_files(self):
        if not self.frames_dir.exists():
            self.frames_dir.mkdir(parents=True)

        vid = cv2.VideoCapture(str(self.video_file))
        index = 0

        logger.info("start converting image to frames...")
        while vid.isOpened():
            ret, frame = vid.read()

            # end of video
            if not ret:
                break

            if index % self.frame_step == 0:
                file_name = f"{self.frame_prefix}{index}.png"
                frame_path = self.frames_dir / file_name

                cv2.imwrite(str(frame_path), frame)

            index += 1

        logger.info("finished converting image to frames.")
        vid.release()
        cv2.destroyAllWindows()

    def run_ocr(self, langs: t.Optional[t.List[str]] = None) -> t.List[Frame]:
        if not self.frames_dir:
            raise ValueError("frames_dir is not set. needed to run ocr.")

        frames = []

        # glob all frames and sort by name
        frame_files = list(self.frames_dir.glob(f"{self.frame_prefix}*.png"))

        # sort by number in filename
        frame_files = sorted(frame_files, key=lambda f: int(f.stem.split("-")[-1]))

        logger.info("start OCR on frames...")
        for frame_file in frame_files:
            results = detect_text(str(frame_file), languages=langs)

            if results:
                frames.append(Frame(frame_file=frame_file, results=results))

        logger.info("completed OCR on frames.")

        self.frames = frames

        return frames

    def to_json(self) -> Path:
        if not self.output_file.parent.exists():
            self.output_file.parent.mkdir(parents=True)

        s = to_json(self, indent=4)
        with open(self.output_file, "w") as f:
            f.write(s)

        return self.output_file
