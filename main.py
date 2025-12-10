import smtplib
from email.mime.text import MIMEText
import os

from dotenv import load_dotenv
load_dotenv()

SMTP_SERVER = "smtp.gmail.com"
SMTP_PORT = 587

GMAIL_APP_PW = os.getenv("GMAIL_APP_PW").replace(' ','')
GMAIL_EMAIL_FROM = os.getenv("GMAIL_EMAIL_FROM")
GMAIL_EMAIL_TO = os.getenv("GMAIL_EMAIL_TO")

msg = MIMEText("Hello, this is a test email from Python.")
msg["Subject"] = "Test Email"
msg["From"] = GMAIL_EMAIL_FROM
msg["To"] = GMAIL_EMAIL_TO

with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
    server.starttls()                     # upgrade to TLS
    server.login(GMAIL_EMAIL_FROM, GMAIL_APP_PW)  
    server.send_message(msg)

print("Email sent.")


def main():
    print("Hello from mysmtp!")


if __name__ == "__main__":
    main()
