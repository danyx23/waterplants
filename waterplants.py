"""Water plants script

Usage:
  waterplants.py on [-d <device>]
  waterplants.py on5min [-d <device>]
  waterplants.py on-x-sec <seconds> [-d <device>]
  waterplants.py off [-d <device>]
  waterplants.py on5minifwarmernow <temp> [-d <device>]
  waterplants.py on5minifwarmertoday <temp> [-d <device>]
  waterplants.py status [-d <device>]
  waterplants.py weather
  waterplants.py (-h | --help)
  waterplants.py --version

Options:
  -h --help     Show this screen.
  -d <device>   Specify the device [default: HS100]
  --version     Show version.

"""
import asyncio
from docopt import docopt
from kasa import SmartPlug
from datetime import datetime
import platform
import requests
from tenacity import *


@retry(stop=stop_after_attempt(5), wait=wait_exponential(multiplier=1, min=1, max=20))
async def get_high_today():
    weather = requests.get("https://wttr.in/Berlin?format=j1").json()

    return int(weather["weather"][0]["maxtempC"])

@retry(stop=stop_after_attempt(5), wait=wait_exponential(multiplier=1, min=1, max=20))
async def get_temp_now():
    # declare the client. format defaults to metric system (celcius, km/h, etc.)
    weather = requests.get("https://wttr.in/Berlin?format=j1").json()

    return int(weather["current_condition"][0]["temp_C"])

async def print_weather():
    temp = await get_temp_now()
    print(f"Temperature now is {temp} C")

async def on_if_warmer_today(threshold: int, device: str):
    print("Getting temperature forecast for today")
    temp = await get_high_today()
    print(f"High today is {temp}, threshold is {threshold}")
    if temp >= threshold:
        await on5min(device)

async def on_if_warmer_now(threshold: int, device: str):
    print("Getting temperature right now")
    temp = await get_temp_now()
    print(f"Temperature now is {temp}, threshold is {threshold}")
    if temp >= threshold:
        await on5min(device)

async def on(device: str):
    print(f"Turning on device {device}")
    p = SmartPlug(device)

    await p.update()
    await p.turn_off()
    await asyncio.sleep(5)
    await p.update()
    await p.turn_on()

async def on45sec(device: str):
    await on(device)
    await asyncio.sleep(40)
    print("Turning off")
    await off(device)

async def on5min(device: str):
    await on(device)
    await asyncio.sleep(300)
    print("Turning off")
    await off(device)

async def on_x_sec(seconds: int, device: str):
    await on(device)
    await asyncio.sleep(seconds)
    print("Turning off")
    await off(device)

async def off(device: str):
    print(f"Turning off device {device}")
    p = SmartPlug(device)

    await p.update()
    await p.turn_off()

async def status(device: str):
    p = SmartPlug(device)
    await p.update()
    if p.is_on:
        print("Device is on")
    else:
        print("Device is off")


def main():
    arguments = docopt(__doc__, version='waterplants V1')
    if platform.system()=='Windows':
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    if arguments["on5minifwarmernow"]:
        asyncio.run(on_if_warmer_now(int(arguments["<temp>"]), arguments["-d"]))
    elif arguments["on5minifwarmertoday"]:
        asyncio.run(on_if_warmer_today(int(arguments["<temp>"]), arguments["-d"]))
    elif arguments["on"]:
        asyncio.run(on(arguments["-d"]))
    elif arguments["on5min"]:
        asyncio.run(on5min(arguments["-d"]))
    elif arguments["on-x-sec"]:
        asyncio.run(on_x_sec(int(arguments["<seconds>"]), arguments["-d"]))
    elif arguments["off"]:
        asyncio.run(off(arguments["-d"]))
    elif arguments["weather"]:
        asyncio.run(print_weather())
    elif arguments["status"]:
        asyncio.run(status(arguments["-d"]))

if __name__ == "__main__":
    main()
