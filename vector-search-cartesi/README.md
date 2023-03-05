# vector-search DApp

vector-search is a customized DApp written in Python, which originally resembles the one provided by the sample [Echo Python DApp](https://github.com/cartesi/rollups-examples/tree/main/echo-python).
Contrary to that example, this DApp does not use shared resources from the `rollups-examples` main directory, and as such the commands for building, running and deploying it are slightly different.

_Original README.md was moved to README.old.me_

## Installation

```bash
virtualenv .venv
source .venv/bin/activate
pip install -r requirements.txt

cd frontend-console
yarn install
yarn build
```

## Running

```bash
docker compose -f docker-compose.yml -f docker-compose.override.yml -f docker-compose-host.yml up
# then, in other console:
ROLLUP_HTTP_SERVER_URL="http://127.0.0.1:5004" python3 vector-search.py
# then, in yet another console:
cd frontend-console
yarn start input send --payload "Hello there"
```

## Screenshots

### Request
![frontend-console-request](https://i.imgur.com/L5TYHQM.png)

### Result
![frontend-console-result](https://i.imgur.com/p8W8xEn.png)