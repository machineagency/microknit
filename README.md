# microknit
Micropython controller for the Silver Reed

## Setup

Git clone this repo then:

- `$ pip install adafruit-ampy`
- edit fields in `.ampy` for ESP's USB details
- edit fields in `config.json` for networking details

## Install on ESP

- `$ ampy put config.json`
- `$ ampy run py/wifi.py`
- `$ ampy run py/install.py`
- `$ ampy put py`
- `$ ampy put main.py`

## Communications to ESP from client

- `$ cd client/`
- `$ pip install -r requirements.txt`
- `$ python3 client.py`

