import logging
import smtplib
from typing import List
from email.message import EmailMessage

try:
    from .settings import HOST, PORT, SENDER_EMAIL, SENDER_PASSWORD
except:
    from settings import HOST, PORT, SENDER_EMAIL, SENDER_PASSWORD

class SMTPException(BaseException):
    pass

class EmailNotification:
    def __init__(self, to:list) -> None:
        self.recipients = to

    def send_notification(self, message:str, subject:str="Test: Script issue detected!") -> None:
        logging.info(f"Preparing email notification message with subject: {subject}")
        try:
            smtpObj = self.__login()
            msg = self.__set_email_content(message, subject)  
            self.__send_email(smtpObj, msg)    
            logging.info("Successfully sent email")
        except SMTPException as e:
            logging.error(f"Error: unable to send email: {e}")

    def __send_email(self, smtpObj, msg):
        logging.info("Sending the email...")
        smtpObj.send_message(msg)
        smtpObj.quit()

    def __login(self):
        logging.info("Logging in with sender account credentials...")
        smtpObj = smtplib.SMTP(HOST, PORT)
        smtpObj.ehlo()
        smtpObj.starttls()
        smtpObj.login(SENDER_EMAIL, SENDER_PASSWORD)
        return smtpObj

    def __set_email_content(self, message, subject):
        logging.info("Setting email message...")
        msg = EmailMessage()
        msg["Subject"] = subject
        msg["From"] = SENDER_EMAIL
        msg["To"] = self.recipients
        msg.set_content(message)
        return msg