from dotenv import load_dotenv
from mysmtp.email import Mailer

def main():
    load_dotenv()
    M = Mailer()
    M.send(subject="Test Email", message="Hello, this is a test email from Python.")

if __name__ == "__main__":
    main()
