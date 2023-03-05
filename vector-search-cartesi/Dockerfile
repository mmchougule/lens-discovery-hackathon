# syntax=docker.io/docker/dockerfile:1.4
FROM cartesi/toolchain:0.12.0 as dapp-build

WORKDIR /opt/cartesi/dapp

RUN apt update && apt install -y pip
RUN pip install virtualenv

COPY . .

RUN <<EOF
virtualenv .venv
. ./.venv/bin/activate
export TARGET=riscv64-cartesi-linux-gnu
export TARGET_DIR=/opt/riscv/rootfs/buildroot/work/staging/usr
export ROOT_DIR=${PWD}/3rdparty
export PYTHON_DIR=/opt/build-python/

export CC="${TARGET}-gcc"
export CXX="${TARGET}-g++"
export CXXFLAGS="-I${TARGET_DIR}/include -I${PYTHON_DIR}/include"
export CFLAGS="-I${TARGET_DIR}/include -I${PYTHON_DIR}/include"
export LDFLAGS="-L${TARGET_DIR}/lib -L${PYTHON_DIR}/lib -L${ROOT_DIR}/.env/cross/lib -shared"
export LDSHARED="${TARGET}-gcc"
export LD="${TARGET}-gcc"

pip install -r requirements.txt -v
EOF