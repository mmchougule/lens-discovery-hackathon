# syntax=docker.io/docker/dockerfile:1.4
FROM cartesi/toolchain:0.12.0 as dapp-build

WORKDIR /opt/cartesi/dapp

RUN apt update && apt install -y pip python3.10-venv && pip install crossenv

COPY . .

RUN <<EOF
python3 -m crossenv $(which python3) .crossenv
. ./.crossenv/bin/activate
pip install -r requirements.txt -v
EOF