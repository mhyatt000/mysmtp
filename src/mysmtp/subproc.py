import subprocess
from rich import print

def parse(str) -> list[str]:
    return [x.strip() for x in str.split(" ") if x.strip()]

def do(args: list[str]) -> None:
    p = subprocess.run(args, capture_output=True, text=True)
    out = p.stdout
    err = p.stderr

    print(out, err)
    return (out, err)

def lines(out: str) -> list[str]:
    return [x.strip() for x in out.split("\n") if x.strip()]
