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

## Unsolved challenges

- Build time for Cartesi machine was prohibitively long due to the size of dependencies (such as `pytorch`). The build time took about 185 minutes.
- After successful build, machine fails with OOM error. TODO: Try increasing error limits again.
- `numpy` fails to build or run on this machine. Some of the error messages in the toggle below:

<details>
  <summary>numpy errors</summary>
  
  #0 287.5                   sources = self.generate_sources(sources, ext)
  #0 287.5                 File "/tmp/pip-install-8g4q4na8/numpy_013c6621a6a94ea3a936d008fac0c0a8/numpy/distutils/command/build_src.py", line 378, in generate_sources
  #0 287.5                   source = func(extension, build_dir)
  #0 287.5                 File "/tmp/pip-install-8g4q4na8/numpy_013c6621a6a94ea3a936d008fac0c0a8/numpy/core/setup.py", line 434, in generate_config_h
  #0 287.5                   moredefs, ignored = cocache.check_types(config_cmd, ext, build_dir)
  #0 287.5                 File "/tmp/pip-install-8g4q4na8/numpy_013c6621a6a94ea3a936d008fac0c0a8/numpy/core/setup.py", line 44, in check_types
  #0 287.5                   out = check_types(*a, **kw)
  #0 287.5                 File "/tmp/pip-install-8g4q4na8/numpy_013c6621a6a94ea3a936d008fac0c0a8/numpy/core/setup.py", line 289, in check_types
  #0 287.5                   raise SystemError(
  #0 287.5               SystemError: Cannot compile 'Python.h'. Perhaps you need to install python-dev|python-devel.
  #0 287.5               [end of output]
  
</details>

## Screenshots

### Request
![frontend-console-request](https://i.imgur.com/L5TYHQM.png)

### Result
![frontend-console-result](https://i.imgur.com/p8W8xEn.png)
