"""Qualified-host cmsRun wrapper that always retains a structured job record."""

from __future__ import print_function

import argparse
import hashlib
import json
import os
import subprocess
import sys
import time


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--record", required=True)
    parser.add_argument("--log", required=True)
    arguments, command = parser.parse_known_args()
    if not command or command[0] != "cmsRun":
        parser.error("the wrapped command must begin with cmsRun")
    started = time.time()
    process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    stdout, stderr = process.communicate()
    finished = time.time()
    record = {
        "schema_version": "1.0.0",
        "status": "passed" if process.returncode == 0 else "failed",
        "failure_code": None if process.returncode == 0 else "EXTRACT_CMSRUN_FAILED",
        "return_code": process.returncode,
        "wall_seconds": finished - started,
        "command": command,
        "stdout_sha256": hashlib.sha256(stdout).hexdigest(),
        "stderr_sha256": hashlib.sha256(stderr).hexdigest(),
        "host_id": os.environ.get("PARTICLEML_QUALIFIED_HOST_ID", "UNRESOLVED"),
    }
    with open(arguments.log, "w") as stream:
        json.dump(record, stream, sort_keys=True, separators=(",", ":"))
        stream.write("\n")
    sys.stdout.write(stdout.decode("utf-8", "replace"))
    sys.stderr.write(stderr.decode("utf-8", "replace"))
    return process.returncode


if __name__ == "__main__":
    sys.exit(main())
