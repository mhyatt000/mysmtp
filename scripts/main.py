from dotenv import load_dotenv
from pathlib import Path
from mysmtp.task.plot import plot_gpu_day
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

@app.task(daily.after("11:00"))
def do_send_plot():

    d = Path(".").resolve()
    f = list(d.glob("*metric*.csv"))[0]
    print(f)
    fig, ax = plot_gpu_day(f)
    # plt.show()
    # save to file
    out_png = f.with_suffix(".png")
    fig.savefig(out_png)
    print(f"Saved plot to {out_png}")



    hostname = lines(do(parse("hostname"))[0])[0]
    subject = f'[auto smtp] {hostname}'
    msg = f"GPU metrics plot from {hostname}"
    M = Mailer()
    (
        M.compose(subject=subject, message=msg)
        .attach(path="gpu_metrics.png")
        .send()
    )
    



def main():
    do_send_plot()
    print("Starting Rocketry app...")
    # app.run()

if __name__ == '__main__':
    main()
