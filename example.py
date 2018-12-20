from getemails import EmailReader,ProcessData

# A simple example to use the email grabber
class App():
    def __init__(self):
        # email that will send emails
        self.sender_email = "[Enter email here]"
        # Initialize emaiReader
        self.email = EmailReader()
        
        self.detectEmails()
     
    # Loops through all unread messages
    def detectEmails(self):
        # Use "me" since we are recieving and sending
        # from same email the API was enabled
        emails = self.email.get_emails('me',['UNREAD'])
        if emails:
            # Get all emails and put data into list
            email_info = self.email.read_emails("me",emails)
            
            # Loop through all the email info
            for data in email_info:
                
                # parse and display body of email
                email_text = ProcessData(data[3]).parse_data()
                print(email_text)
                
            # resend body text back to last email as a reply
            message = self.email.generate_email(
                str(email_text),email_info[-1][0],
                self.sender_email,email_info[-1][1],
                thread = email_info[-1][2])
            
            self.email.send_email("me",message)
            

if __name__ == "__main__":
    App()
