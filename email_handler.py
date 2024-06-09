import base64
from email.mime.text import MIMEText
from google_creds_getter import GoogleCreds
from requests import HTTPError

class EmailHandler:
    def __init__(self, creds: GoogleCreds):
        self.service = creds.get_service('gmail', 'v1')

    def send_message(self, html_content: str, recipient: str, subject:str ='Media Newsletter'):
        message = MIMEText(html_content, 'html')
        message['to'] = recipient
        message['subject'] = subject
        create_message = {'raw': base64.urlsafe_b64encode(message.as_bytes()).decode()}

        try:
            message = (self.service.users().messages().send(userId="me", body=create_message).execute())
            print(F'sent message to {message} Message Id: {message["id"]}')
        except HTTPError as error:
            print(F'An error occurred: {error}')
            message = None
