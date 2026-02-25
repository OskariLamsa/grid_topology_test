from invoke import task
import subprocess
import sys

@task
def main(c):
    #c.run("poetry run python main.py")
    cmd = ["poetry", "run", "python", "main.py"]
    subprocess.run(cmd, check=False)
@task
def test(c):
    cmd = ["poetry", "run", "pytest"]
    subprocess.run(cmd, check=False)