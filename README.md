# Media Newsletter
The Media Newsletter gets your favorite content from Youtube and Reddit and emails it to you - no algorithm involved to keep you glued to your computer screen.
## Install
You need to install python dependancies in `requirements.txt`. You can do so in a virtual environment with the following commands:
```shell
cd media-newsletter
python3.12 -m venv .venv
source .venv/bin/activate
pip install requirements.txt
```
## Usage
**NOTE:** There is likely more configuration setup to get this working. This setup works for my development accounts. It has not been tested for a standard user account.

Requires Python 3.12.
Configure `youtube_feeds.json` and `reddit_feeds.json` to your preferences.
Run
```shell
python3.12 main.py
```
Follow the Google Oauth2 prompt and click "Allow" to both scopes.
Enter the email you want the newsletter to be sent to.
Enjoy content sent straight to you! No annoying algorithm to deal with!
