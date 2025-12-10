from dotenv import load_dotenv
from mysmtp.email import Mailer
from mysmtp.subproc import do, parse, lines

from rocketry import Rocketry
from rocketry.conds import daily

load_dotenv()
app = Rocketry()

# @app.task(daily)
@app.task(daily.after("07:00"))
def do_daily():
    M = Mailer()
    M.send(subject="Test Email", message="Hello, this is a test email from Python.")

# @app.task(cron("* 2 * * *"))
# def do_based_on_cron():

def main():
    do_daily()
    app.run()

if __name__ == '__main__':
    main()
