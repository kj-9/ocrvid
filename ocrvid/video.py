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
    frame_index: int
    results: t.List[OCRResult]


# @serde
@dataclass
class Video:
    output_file: Path = field(default=None, skip=True)  # where to de/serialize
    video_file: t.Optional[Path] = None
    frames: t.List[Frame] = field(default_factory=list)
    frame_prefix: t.ClassVar[str] = "frame-"  # prefix for frame files

    def frame_generator(self, frame_step: int):
        vid = cv2.VideoCapture(str(self.video_file))
        index = 0

        logger.info("start converting image to frames...")
        while vid.isOpened():
            ret, frame = vid.read()

            # end of video
            if not ret:
                break

            if index % frame_step == 0:
                yield index, frame

            index += 1

        vid.release()
        cv2.destroyAllWindows()

    def run_ocr(
        self,
        frame_step: int,
        frames_dir: t.Optional[Path] = None,
        langs: t.Optional[t.List[str]] = None,
    ) -> t.List[Frame]:
        """Run OCR on frames and return a list of Frame objects

        Args:
            frames_dir (Path, optional): where to save frames. Defaults to None i.e. not save frames.
            langs (t.Optional[t.List[str]], optional): prefered languages to detect, ordered by priority. Defaults to None i.e. auto detect.
        """

        frames = []

        if frames_dir and not frames_dir.exists():
            frames_dir.mkdir(parents=True)

        logger.info("start OCR on frames...")
        for index, frame in self.frame_generator(frame_step):
            buffer = cv2.imencode(".png", frame)[1].tobytes()

            results = detect_text(buffer, languages=langs)

            if frames_dir:
                frame_file = frames_dir / f"{self.frame_prefix}{index}.png"
                with open(frame_file, "wb") as f:
                    f.write(buffer)

            if results:
                frames.append(Frame(frame_index=index, results=results))

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
