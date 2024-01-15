from googleapiclient.discovery import build
from isodate import parse_duration

from .base import MetadataDownloader


class GoogleAPIDownloader(MetadataDownloader):
    def __init__(self, api_key):
        super().__init__()
        self.api_key = api_key


    def get_top_results_metadata(self, query: str, top_k: int = 10) -> dict:
        """
        Note that 101 units of cost is needed per query.
        100 for the search().list and 1 for videos().list.
        """
        api_key = self.api_key
        youtube = build('youtube', 'v3', developerKey=api_key)

        search_response = youtube.search().list(
            q=query,
            part='snippet',
            maxResults=top_k,
            type='video'
        ).execute()

        metadata_dict = {}
        for item in search_response['items']:
            video_id = item['id']['videoId']
            metadata_dict[video_id] = {
                'id': video_id,
                'title': item['snippet']['title'],
                'channel_id': item['snippet']['channelId']
            }

        video_response = youtube.videos().list(
            id=','.join(metadata_dict.keys()),
            part='contentDetails,snippet'
        ).execute()

        for item in video_response['items']:
            video_id = item['id']
            metadata_dict[video_id].update({
                'duration': parse_duration(item['contentDetails']['duration']).total_seconds(),
                'channel_title': item['snippet']['channelTitle'],
                'description': item['snippet']['description']
            })

        return metadata_dict