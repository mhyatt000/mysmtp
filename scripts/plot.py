from pathlib import Path
from rich import print
from mysmtp.task.plot import plot_gpu_day
import matplotlib.pyplot as plt

def main():

    d = Path(".").resolve()
    f = list(d.glob("*metric*.csv"))[0]
    print(f)
    fig, ax = plot_gpu_day(f)
    # plt.show()
    # save to file
    out_png = f.with_suffix(".png")
    fig.savefig(out_png)
    print(f"Saved plot to {out_png}")


if __name__ == "__main__":
    main()
