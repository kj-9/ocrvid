import typing as t
from contextlib import contextmanager
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


@contextmanager
def VideoCapture(*args, **kwargs):
    cap = cv2.VideoCapture(*args, **kwargs)
    try:
        yield cap
    finally:
        cap.release()
        cv2.destroyAllWindows()


# @serde
@dataclass
class Video:
    output_file: Path = field(default=None, skip=True)  # where to de/serialize
    video_file: t.Optional[Path] = None
    frames: t.List[Frame] = field(default_factory=list)
    frame_prefix: t.ClassVar[str] = "frame-"  # prefix for frame files

    def frame_generator(self, frame_step: int):
        """
        Generates frames from a video file.

        Args:
            frame_step (int): The step size between frames to be generated.

        Yields:
            Tuple[int, numpy.ndarray]: A tuple containing the index of the frame and the frame itself.
        """
        with VideoCapture(str(self.video_file)) as vid:
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

    def get_props(self) -> t.Dict[str, t.Optional[float]]:
        """
        Retrieve the properties of the video file.

        Returns:
            A dictionary containing the following properties:
            - frame_count: The total number of frames in the video.
            - fps: The frames per second of the video.
            - seconds: The duration of the video in seconds.
            - width: The width of each frame in pixels.
            - height: The height of each frame in pixels.
        """

        with VideoCapture(str(self.video_file)) as vid:

            def get_or_none(prop: int):
                v = vid.get(prop)
                return None if v == 0 else v

            width = get_or_none(cv2.CAP_PROP_FRAME_WIDTH)
            height = get_or_none(cv2.CAP_PROP_FRAME_HEIGHT)
            frame_count = get_or_none(cv2.CAP_PROP_FRAME_COUNT)
            fps = get_or_none(cv2.CAP_PROP_FPS)

        seconds = None
        if frame_count and fps:
            seconds = frame_count / fps

        props = {
            "frame_count": frame_count,
            "fps": fps,
            "seconds": seconds,
            "width": width,
            "height": height,
        }
        return props

    def run_ocr(
        self,
        frame_step: t.Optional[int] = None,
        by_second: t.Optional[int] = None,
        frames_dir: t.Optional[Path] = None,
        langs: t.Optional[t.List[str]] = None,
    ) -> t.List[Frame]:
        """
        Run OCR on the video frames.
        Must provide either frame_step or by_second.

        Args:
            frame_step (int, optional): The number of frames to skip between OCR operations. Defaults to None.
            by_second (int, optional): The number of seconds between OCR operations. Defaults to None.
            frames_dir (Path, optional): The directory to save the extracted frames. Defaults to None.
            langs (List[str], optional): The list of languages to use for OCR. Defaults to None which means auto detect.

        Returns:
            List[Frame]: The list of Frame objects containing OCR results.
        """

        if by_second:
            fps = self.get_props()["fps"]

            if not fps or fps <= 0:
                raise ValueError(
                    f"Invalid fps: {fps}. This video file may not have fps as metadata."
                )

            frame_step = int(fps * by_second)

            if frame_step <= 0:
                raise ValueError(
                    f"Invalid frame_step: {frame_step}. by_second may be too small."
                )

            logger.info(f"{frame_step=}, calucated from: {fps=} * {by_second=}.")

        if frames_dir and not frames_dir.exists():
            frames_dir.mkdir(parents=True)

        frames = []

        logger.info("start OCR on frames...")
        for index, frame in self.frame_generator(frame_step):  # type: ignore
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
