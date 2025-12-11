from dotenv import load_dotenv
from mysmtp.email import Mailer
from mysmtp.subproc import do, parse, lines
from mysmtp.tasks import log_gpu_metrics

from rocketry import Rocketry
from rocketry.conds import daily, every

load_dotenv()
app = Rocketry()

# @app.task(daily)
@app.task(daily.after("07:00"))
def do_daily():
    M = Mailer()
    M.send(subject="Test Email", message="Hello, this is a test email from Python.")


# @app.task(every("1 second"))
# def do_every_second():
    # pass

# @app.task(cron("* 2 * * *"))
# def do_based_on_cron():

@app.task(every("1 second"))
def do_log_gpu():
    log_gpu_metrics()

def main():
    print("Starting Rocketry app...")
    app.run()

if __name__ == '__main__':
    main()
