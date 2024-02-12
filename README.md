# HatDrive! Tool

A tool for the [HatDrive!](https://pineberrypi.com/products/hat-top-2230-2240-for-rpi5).
It can read power data from the monitor chip, as well as data from the EEPROM.

## Disclaimer

I have used the HatDrive! **Bottom**.
It was hacked to access the SDA and SCL lines and connected to the GPIO pins 3 and 5.
Use at your own risk! This is not a official modification!
You are complete responsible for your own actions!

## Installation

It is recommended to use the Python Virtual Environment!

```
$ python -m venv .
$ source bin/activate
```

Afterwards you can install the dependencies for the python modules.

```
$ sudo apt-get install python3-dev libgpiod-dev
```

And finally the module itself.

```
$ pip install pi-ina219
$ pip install adafruit-python-shell
$ pip install click
$ pip install setuptools
$ pip install gpiod
```

## Usage

```
$ ./hatdrivetool.py meter
```

## Debugging

```
$ i2cdetect -y 1
```
You should see the `40` and `50` device.
