import praw
import os
from typing import List, Dict
from pydantic_settings import BaseSettings, SettingsConfigDict
from datetime import datetime

type Submission = praw.models.reddit.submission.Submission
type Subreddit = praw.models.reddit.subreddit.Subreddit

class RedditSettings(BaseSettings):
    client_id: str
    client_secret: str
    user_agent: str
    model_config = SettingsConfigDict(env_prefix="REDDIT_")

class RedditGetter():
    def __init__(self):
        DOTENV = os.path.join(os.path.dirname(__file__), '.env.reddit')
        settings: RedditSettings = RedditSettings(_env_file=DOTENV)
        self.reddit = praw.Reddit(
                client_id=settings.client_id,
                client_secret=settings.client_secret,
                user_agent=settings.user_agent
        )

    def get_html_content(self, feed_dict: Dict[str, List[str]]) -> str:
        html_content = ""
        reddit_contents: List[str] = []
        for name in feed_dict:
            print(f"Getting {name} content...")
            reddit_contents.append(self.get_feed_content(name, feed_dict[name]))
        html_content: str = f"""
        <html>
            <head>
                {self.get_style_content()}
            </head>
            <body>
                {"\n".join(reddit_contents)}
            </body>
        </html>        
        """
        return html_content
    
    def get_feed_content(self, feed_name: str, subreddit_names: List[str]) -> str:
        subreddit_contents: List[str] = []
        for name in subreddit_names:
            print(f"\tGetting {name} content...")
            subreddit: Subreddit = self.reddit.subreddit(name)
            subreddit_contents.append(self.get_subreddit_content(subreddit, time_filter="day"))
        feed_text: str = f"<h2>{feed_name}</h2>\n{"\n".join(subreddit_contents)}"
        return feed_text

    def get_subreddit_content(self, subreddit: Subreddit, time_filter: str="day", content_limit: int=10) -> str:
        submission_list: List[str] = []
        for submission in subreddit.top(time_filter=time_filter, limit=content_limit):
            submission_list.append(self.get_submission_content(submission))
        submission_text: str = f"""<h3>{subreddit.title}</h3>\n<table>\n{"\n".join(submission_list)}\n</table>"""
        return submission_text

    def get_submission_content(self, submission: Submission):
        submission_time = datetime.fromtimestamp(submission.created_utc).strftime('%Y-%m-%d %H:%M')
        content = f"""
                    <tr>
                      <td>Score: {submission.score}, Comments: {submission.num_comments}</td>
                      <td>{submission_time}</td>
                      <td><a href='https://reddit.com/{submission.id}'>{submission.title}</a></td>
                    </tr>
                  """
        return content
    
    def get_style_content(self) -> str:
        style: str = ''
        with open('reddit_style.css', 'r') as f:
            style = f.read()
        return f'<style>{style}</style>'
