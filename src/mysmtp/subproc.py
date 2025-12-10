import subprocess
from rich import print

p = subprocess.run(["ls", "-l"], capture_output=True, text=True)
out = p.stdout
err = p.stderr

print(out, err)
