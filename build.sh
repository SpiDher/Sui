#!/bin/bash
export TMPDIR=/tmp
export CARGO_HOME=/tmp/cargo
pip install --no-cache-dir pysui_fastcrypto
pip install --no-cache-dir -r requirements.txt
