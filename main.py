from email_handler import EmailHandler
from reddit_getter import RedditGetter
from typing import List, Dict
import json
from youtube_getter import YoutubeGetter
from google_creds_getter import GoogleCreds

def main():
    SCOPES = ["https://www.googleapis.com/auth/gmail.send",
              "https://www.googleapis.com/auth/youtube.readonly"]
    credential_manager: GoogleCreds = GoogleCreds(SCOPES)
    email_handler: EmailHandler = EmailHandler(credential_manager)
    reddit_getter: RedditGetter = RedditGetter()
    youtube_getter: YoutubeGetter = YoutubeGetter(credential_manager)
    
    print("\n\nWelcome to Media Newsletter!\n\n")
    reddit_feeds: Dict[str, List[str]]
    youtube_feeds: Dict[str, List[str]]
    with open('reddit_feeds.json', 'r') as f:
        reddit_feeds = json.load(f)
    with open('youtube_feeds.json', 'r') as f:
        youtube_feeds = json.load(f)

    email: str = input("Please enter email to send to: ")

    reddit_content: str = reddit_getter.get_html_content(reddit_feeds)
    write_html("reddit_output.html", reddit_content)
    print("Sending Reddit Digest...")
    email_handler.send_message(reddit_content, email, subject='Media Newsletter: Reddit Digest')
    
    youtube_content: str = youtube_getter.get_html_content(youtube_feeds, channels_filepath='channels.json')
    write_html("youtube_output.html", youtube_content)
    print("Sending Youtube Digest...")
    email_handler.send_message(youtube_content, email, subject='Media Newsletter: Youtube Digest')

    print("\n\nEnjoy your media!\n\n")

def write_html(title: str, html_content: str):
    with open(title, 'w') as f:
        f.write(html_content)

if __name__=="__main__":
    main()
