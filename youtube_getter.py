import json
from typing import Dict, List
from dataclasses import dataclass
from google_creds_getter import GoogleCreds
from datetime import datetime, timedelta

    # This is the format of published date data. Can be used in future to give time scope to videos 
    #publish_date='2024-05-27T12:04:07Z'

@dataclass
class Video:
    title: str
    publish_date: str
    id: str
    url: str

    def __init__(self, title: str, id: str, publish_date: str) -> None:
        self.title = title
        self.id = id
        self.publish_date = publish_date
        self.url = f'https://youtube.com/watch?v={id}'

    @staticmethod    
    def get_video_from_item(item: Dict): 
        title: str = item['snippet']['title']
        id: str = item['snippet']['resourceId']['videoId']
        publish_date: str  = item['snippet']['publishedAt']
        dateandtime = datetime.strptime(publish_date, '%Y-%m-%dT%H:%M:%SZ')
        return Video(title, id, dateandtime.strftime('%Y-%m-%d %H:%M'))

    def to_json(self):
        return json.dumps(self, default=lambda o: o.__dict__, sort_keys=True, indent=4)

@dataclass
class Channel:
    title: str
    id: str
    uploads_id: str
    
    def __init__(self, title: str, id: str, uploads_id: str) -> None:
        self.title = title
        self.id = id
        self.uploads_id = uploads_id
    
    def to_json(self):
        return json.dumps(self, default=lambda o: o.__dict__, sort_keys=True, indent=4)

class YoutubeGetter:
    def __init__(self, creds: GoogleCreds) -> None:
        self.service = creds.get_service('youtube', 'v3')

    def get_html_content(self, feed_dict: Dict[str, List[str]], channels_filepath: str) -> str:
        youtube_contents: List[str] = []
        for name in feed_dict:
            print(f'Getting {name} content...')
            youtube_contents.append(self.get_feed_content(feed_name=name, channel_titles=feed_dict[name], channels_filepath=channels_filepath))
        html_content: str = f"""
        <html>
            <head>
            {self.get_style_content()}
            </head>
            <body>
                {"\n".join(youtube_contents)}
            </body>
        </html>        
        """
        return html_content

    def get_feed_content(self, feed_name: str, channel_titles: List[str], channels_filepath='channels.json') -> str:
        channels: Dict[str, Channel] = self.load_channels(filepath=channels_filepath)
        channel_contents: List[str] = []
        for title in channel_titles:
            if title not in channels.keys():
                print(f"Could not find {title}, searching...")
                channel: Channel = self.get_channel(title)
                channels[title] = channel
                self.save_channels('channels.json', channels)

            channel_content: str = self.get_channel_content(channels[title], max_results=5)
            channel_contents.append(channel_content)

        feed_text: str = f'<h2>{feed_name}</h2>\n{'\n'.join(channel_contents)}'
        return feed_text
    
    def get_uploads_playlist_id(self, channel_id: str):
        """Get id for recent uploads playlist id."""
        request = self.service.channels().list(
            part='contentDetails',
            id=channel_id
            )
        response = request.execute()
        return response['items'][0]['contentDetails']['relatedPlaylists']['uploads']

    def get_channel(self, channel_title: str) -> Channel:
        """Get Channel object for channel title."""
        id: str = self.get_channel_id(channel_title)
        playlist_id: str = self.get_uploads_playlist_id(id)
        return Channel(title=channel_title, id=id, uploads_id=playlist_id)

    def get_channel_content(self, channel: Channel, max_results: int=3) -> str:
        """Get HTML content of most recent uploads from Channel object"""
        print(f'\tGetting {channel.title} content...')
        video_contents: List[str] = []
        request = self.service.playlistItems().list(
                part='snippet,contentDetails',
                playlistId=channel.uploads_id,
                maxResults=max_results
                )
        response = request.execute()
        response_items= response['items']
        for item in response_items:
            new_video = False
            video = Video.get_video_from_item(item)
            if datetime.now() - datetime.strptime(video.publish_date, '%Y-%m-%d %H:%M') < timedelta(days=7):
                new_video = True

            video_content = f"""
                <tr>
                    <td{' style="color:red"' if new_video else ''}>{video.publish_date}</td>
                    <td><a href='{video.url}'>{video.title}</a></td>
                </tr>
            """
            video_contents.append(video_content)
        channel_text: str = f"""
            <h3>{channel.title}</h3>
                <table>
                    {"\n".join(video_contents)}\n
                </table>
        """
        return channel_text

    def get_channel_id(self, channel_title: str) -> str:
        """Get channel id from channel title."""
        search = self.service.search().list
        request = search(part='snippet', type='channel', q=channel_title)
        response = request.execute()
        channel_id = response['items'][0]['id']['channelId']
        channel_title = response['items'][0]['snippet']['title']
        return channel_id
    
    @staticmethod
    def save_channels(filepath: str, channels: Dict[str, Channel]):
        """Save Channel dictionary to file. Avoids unneccesary API calls."""
        with open(filepath, 'w') as f:
            json.dump(channels, f, default=lambda o: o.__dict__, indent=4)

    @staticmethod
    def load_channels(filepath: str) -> Dict[str, Channel]:
        """Load Channel dictionary from file."""
        channels: Dict[str, Channel] = {}
        file_data: str = ''
        with open(filepath, 'r') as f:
            file_data: str = f.read()
        channels_data: Dict = json.loads(file_data)
        for title in channels_data.keys():
            channels[title] = Channel(title = channels_data[title]['title'],
                                      id= channels_data[title]['id'],
                                      uploads_id= channels_data[title]['uploads_id'])

        return channels

    def get_style_content(self) -> str:
        style: str = ''
        with open('youtube_style.css', 'r') as f:
            style = f.read()
        return f'<style>{style}</style>'
