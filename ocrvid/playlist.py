import typing as t
from dataclasses import dataclass, field
from pathlib import Path

import googleapiclient.discovery
import googleapiclient.errors
from serde import serde
from serde.json import from_json, to_json

from ocrvid import get_key
from ocrvid.config import get_logger

logger = get_logger(__name__)


@dataclass
@serde
class Playlist:
    playlist_id: str
    items: t.List[dict] = field(default_factory=list)

    def __get_api(self) -> googleapiclient.discovery.Resource:
        YOUTUBE_API_KEY = get_key("YOUTUBE_API_KEY")

        if not YOUTUBE_API_KEY:
            raise Exception("YOUTUBE_API_KEY is not set")

        api_service_name = "youtube"
        api_version = "v3"

        youtube = googleapiclient.discovery.build(
            api_service_name, api_version, developerKey=YOUTUBE_API_KEY
        )

        return youtube

    def get_playlist(self, max_results: int = 500) -> t.Optional[t.List[dict]]:
        youtube = self.__get_api()
        next_page_token = None

        items = []

        while True:
            logger.info("requesting playlist items...")
            request = youtube.playlistItems().list(
                part="snippet,contentDetails",
                playlistId=self.playlist_id,
                maxResults=max_results,
                pageToken=next_page_token,
            )

            try:
                response = request.execute()
            except googleapiclient.errors.HttpError as e:
                logger.error("HttpError when requesting playlist items:")
                logger.error(e)
                return None

            items.extend(response["items"])

            next_page_token = response.get("nextPageToken")

            if not next_page_token:
                logger.info("finish requesting playlist items.")
                break

        self.items = items
        return items

    def first_video_id_item(self, video_id):
        for item in self.items:
            if item.get("contentDetails").get("videoId") == video_id:
                return item

    def to_video_ids(self) -> t.List[str]:
        return list(map(lambda x: x.get("contentDetails").get("videoId"), self.items))  # type: ignore

    def to_json(self, output: Path) -> Path:

        if not output.parent.exists():
            output.parent.mkdir(parents=True)

        s = to_json(self, indent=4)

        with open(output, "w") as f:
            f.write(s)

        return output
