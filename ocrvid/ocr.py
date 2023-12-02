"""
reference:
mainly copied from : https://github.com/RhetTbull/textinator/blob/3aae89d0eea18aa44cd8304f30b50bc49b33b134/src/macvision.py
also credits: https://github.com/straussmaximilian/ocrmac/blob/main/ocrmac/ocrmac.py
"""

import typing as t
from dataclasses import dataclass

import objc
import Quartz
import Vision
from Foundation import NSURL, NSDictionary, NSLog
from serde import serde


@serde
@dataclass(frozen=True)
class OCRResult:
    text: str
    confidence: float
    bbox: t.Tuple[float, float, float, float]  # x, y, weight, height


def detect_text(
    image_path: str,
    recognition_level: str = "accurate",
    orientation: t.Optional[int] = None,
    languages: t.Optional[t.List[str]] = None,
) -> t.List[OCRResult]:
    """process image with VNRecognizeTextRequest and return results

    This code originally developed for https://github.com/RhetTbull/osxphotos

    Args:
        image_path: path to image to process
        recognition_level: "accurate" or "fast"
        orientation: orientation of image, 1-8, see https://developer.apple.com/documentation/imageio/kcgimagepropertyorientation
        languages: list of languages to recognize, e.g. ["en-US", "ja"]

    """

    if languages is None:
        languages = ["en-US"]
    input_url = NSURL.fileURLWithPath_(image_path)

    """
    with pipes() as (out, err):
    # capture stdout and stderr from system calls
    # otherwise, Quartz.CIImage.imageWithContentsOfURL_
    # prints to stderr something like:
    # 2020-09-20 20:55:25.538 python[73042:5650492] Creating client/daemon connection: B8FE995E-3F27-47F4-9FA8-559C615FD774
    # 2020-09-20 20:55:25.652 python[73042:5650492] Got the query meta data reply for: com.apple.MobileAsset.RawCamera.Camera, response: 0
        input_image = Quartz.CIImage.imageWithContentsOfURL_(input_url)
    """
    image = Quartz.CIImage.imageWithContentsOfURL_(input_url)

    with objc.autorelease_pool():
        vision_options = NSDictionary.dictionaryWithDictionary_({})
        if orientation is None:
            vision_handler = (
                Vision.VNImageRequestHandler.alloc().initWithCIImage_options_(
                    image, vision_options
                )
            )
        elif 1 <= orientation <= 8:
            vision_handler = Vision.VNImageRequestHandler.alloc().initWithCIImage_orientation_options_(
                image, orientation, vision_options
            )
        else:
            raise ValueError("orientation must be between 1 and 8")
        results: t.List[OCRResult] = []
        handler = make_request_handler(results)
        vision_request = (
            Vision.VNRecognizeTextRequest.alloc().initWithCompletionHandler_(handler)
        )

        vision_request.setRecognitionLanguages_(languages)
        vision_request.setUsesLanguageCorrection_(True)

        if recognition_level == "fast":
            vision_request.setRecognitionLevel_(1)
        else:
            vision_request.setRecognitionLevel_(0)

        success, error = vision_handler.performRequests_error_([vision_request], None)
        if not success:
            raise ValueError(f"Vision request failed: {error}")

        return results


def make_request_handler(results):
    """results: list to store results"""
    if not isinstance(results, list):
        raise ValueError("results must be a list")

    def handler(request, error):
        if error:
            NSLog(f"Error! {error}")
        else:
            observations = request.results()

            for observation in observations:
                bbox = observation.boundingBox()
                w, h = bbox.size.width, bbox.size.height
                x, y = bbox.origin.x, bbox.origin.y

                results.append(
                    OCRResult(
                        text=observation.text(),
                        confidence=observation.confidence(),
                        bbox=[x, y, w, h],
                    )
                )

    return handler
