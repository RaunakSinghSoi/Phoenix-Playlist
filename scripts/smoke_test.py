"""Start the Flask server and verify the HTTP health and home endpoints."""

import json
import os
from pathlib import Path
import subprocess
import sys
import time
from urllib.error import HTTPError, URLError
from urllib.request import urlopen

ROOT = Path(__file__).resolve().parents[1]


def main():
    env = os.environ.copy()
    env.setdefault("DEBUG", "false")
    process = subprocess.Popen(
        [sys.executable, "-m", "backend.app"],
        cwd=ROOT,
        env=env,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
    )
    try:
        for _ in range(30):
            if process.poll() is not None:
                raise RuntimeError("Flask process exited before startup")
            try:
                with urlopen("http://127.0.0.1:5000/api/health", timeout=1) as response:
                    if response.status != 200:
                        raise RuntimeError(f"Health returned {response.status}")
                    payload = json.load(response)
                with urlopen("http://127.0.0.1:5000/", timeout=1) as response:
                    if response.status != 200 or b"PhoenixPlaylist" not in response.read():
                        raise RuntimeError("Homepage did not render")
                if payload.get("status") != "ok":
                    raise RuntimeError("Unexpected health response")
                print("PASS: Flask server starts, /api/health and / return HTTP 200")
                return
            except (URLError, ConnectionError, TimeoutError):
                time.sleep(0.5)
        raise RuntimeError("Flask failed to respond within 15 seconds")
    finally:
        process.terminate()
        try:
            output, _ = process.communicate(timeout=5)
        except subprocess.TimeoutExpired:
            process.kill()
            output, _ = process.communicate()
        if process.returncode not in (0, -15, None) and output:
            print(output[-3000:], file=sys.stderr)


if __name__ == "__main__":
    main()
