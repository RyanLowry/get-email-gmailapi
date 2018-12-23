import base64

import email
from email.mime.base import MIMEBase
from email.mime.image import MIMEImage
from email.mime.text import MIMEText
import mimetypes
from googleapiclient.discovery import build
from httplib2 import Http
from oauth2client import file, client, tools
from apiclient import errors
from bs4 import BeautifulSoup
import json

class EmailReader:
    
    def __init__(self):
        # Initial lines specify scope and initializes connection of gmail API
        SCOPES = 'https://www.googleapis.com/auth/gmail.modify'
        self.store = file.Storage('token.json')
        self.creds = self.store.get()
        if not self.creds or self.creds.invalid:
            flow = client.flow_from_clientsecrets('credentials.json', SCOPES)
            self.creds = tools.run_flow(flow, self.store)
        self.service = build('gmail', 'v1', http=self.creds.authorize(Http()))
    
    # Get emails based on specified labels
    def get_emails(self,user_id,label_ids):
        results = self.service.users().messages().list(
            userId=user_id,labelIds = label_ids).execute()
        
        messages = results.get('messages', [])
        return messages
    
    def read_emails(self,user_id,messages):
        email_data = []
        # Loop through all messages reversed, since we want oldest first
        for message in reversed(messages):
            msg = self.service.users().messages().get(
                userId=user_id,id=message["id"]).execute()
            thread= msg["threadId"]
            payload = msg["payload"]
            emailSub = "undefined"
            # get headers info from payload
            for info in payload["headers"]:
                if info["name"] == "From":
                    emailFrom = info["value"]
                if info["name"] == "Subject":
                    if info["value"]:
                        emailSub = info["value"]
                    else:
                        emailSub = "undefined"

            # Detect where the body information is
            if payload["body"]["size"] != 0:
                body = payload["body"]["data"]
                body = base64.urlsafe_b64decode(body)
                body = str(body,'utf-8')
            else:
                # The body can be inside multiple nested parts
                # so we loop through many parts
                body = self._loop_email_data(payload["parts"],0 )
                
                # Decode body to properly parse information
                decoded_body = base64.urlsafe_b64decode(
                    body.encode("ASCII")).decode("utf-8")
                
                HTML_parse = HTMLParse(decoded_body)
                
                # Check if body is parsed with HTML or is only a string
                body = HTML_parse.parse() if HTML_parse.is_HTML() is True else decoded_body.replace("\u200b","")
                
            # Verify we get proper text using message_from_string
            mime = email.message_from_string(body)

            # self.service.users().messages().modify(
            #     userId=user_id,id=message["id"],
            #     body={"removeLabelIds":["UNREAD"]}).execute()

            email_data.append({'from':emailFrom,'subject':emailSub,'threadId':thread,'body':str(mime)})
<<<<<<< HEAD
=======
            #email_data.append([emailFrom, emailSub,thread, str(mime)])
>>>>>>> 509e4cf2d6253aba5d3bf88d6947c5faa9d486c2
            
        return email_data
        
    # Recursive method that grabs part data
    # The data position is dependent on how email is sent
    # (ex. phone, desktop)
    def _loop_email_data(self,info,rec_length):
        
        # Return placeholder text if unable to find body
        if rec_length == 4:
            return "No body text found"
        
        # typical error would involve not finding next part data
        try:
            if info[0]["body"]["size"] == 0:
                data = self._loop_email_data(
                    info[0]["parts"],rec_length + 1)
            else:
                data = info[0]["body"]["data"]
        except:
            return "No body text found"
        return data
            
    # Add thread keyword to determine if you want to reply
    # thread is a list consisting of thread id and message id
    def generate_email(
            self, message,
            reply_to, email_from,
            subject, thread="None"):
        
        msg = MIMEText(message)
        msg["to"] = reply_to
        # TODO:verify reply works with other services(yahoo,hotmail)
        # Add multiple headers to comply with rfc-2822
        if thread is not "None":
            msg["reply-to"] = email_from
            msg["subject"] = "Re: {}".format(subject)
            msg["in-reply-to"] = thread
            msg["references"] = thread
            
            return {'raw': base64.urlsafe_b64encode(
                msg.as_bytes()).decode("utf-8"), 'threadId':thread}
        else:
            msg["from"] = email_from
            msg["subject"] = "Reply to {}".format(subject)
                    
            return {'raw': base64.urlsafe_b64encode(
                msg.as_bytes()).decode("utf-8")}

    def send_email(self,user_id,msg):
        try:
            message = (self.service.users().messages().send(
                userId=user_id, body=msg).execute())

            return message
        
        except errors.HttpError as err:
            print("An Error Occured: %r") % err
  
class HTMLParse:
    def __init__(self,html):
        self.soup = BeautifulSoup(html,"html.parser")
        
    # only parse data if body is valid HTML
    def is_HTML(self):
        return bool(self.soup.find())
    
    def parse(self):
        text = self.soup.body.get_text()
        return text
    
# Class that parses the data once we get it from email
class ProcessData:
    # set data inside init to easily access it for further use
    def __init__(self,data):
        self.data = data
        
    def parse_data(self):
        return self.data.strip().splitlines()
    
