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


def detect_text(  # noqa: PLR0913
    image_path: str,
    recognition_level: str = "accurate",
    orientation: t.Optional[int] = None,
    languages: t.Optional[t.List[str]] = None,
    auto_detect_language: bool = True,
    language_correction: bool = True,
    minimum_text_height: t.Optional[float] = None,
) -> t.List[OCRResult]:
    """process image with VNRecognizeTextRequest and return results

    Just a wrapper around FrameworkVNRecognizeTextRequest in Apple's Vision framework,
    see also: https://developer.apple.com/documentation/vision/vnrecognizetextrequest?language=objc
    This code originally developed for https://github.com/RhetTbull/osxphotos

    Args:
        image_path: path to image to process
        recognition_level: "accurate" or "fast"
        orientation: orientation of image, 1-8, see also: https://developer.apple.com/documentation/imageio/kcgimagepropertyorientation
        languages: list of languages to recognize, order of list is order of preference for recognition. Specify the languages as ISO language codes. e.g. ["en-US", "ja"]
        auto_detect_language: automatically detect language
        language_correction: use language correction
        minimum_text_height: The minimum height, relative to the image height, of the text to recognize.
    """

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

        if languages is not None:
            vision_request.setRecognitionLanguages_(languages)

        if auto_detect_language:
            vision_request.setAutomaticallyDetectsLanguage_(True)

        if language_correction:
            vision_request.setUsesLanguageCorrection_(True)

        if minimum_text_height:
            vision_request.setMinimumTextHeight_(minimum_text_height)

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


def supported_recognition_languages() -> t.Tuple[str]:
    """return list of supported recognition languages"""

    with objc.autorelease_pool():
        results: t.List[OCRResult] = []
        handler = make_request_handler(results)
        vision_request = (
            Vision.VNRecognizeTextRequest.alloc().initWithCompletionHandler_(handler)
        )

        # [1] is passed arg i.g. None
        languages = vision_request.supportedRecognitionLanguagesAndReturnError_(None)[0]

        return languages
