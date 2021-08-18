"""
Input screen v0.1

Author  : Christian Carter
Date    : 23 May 2021

Code for interpreting the input of the 
command prompt and relaying that info 
to other code to run the game.
"""
version_info = "v0.2"
import logging
import os
from multiprocessing.connection import Connection, Client, Listener
import argparse
import pickle
from typing import Any
import time

logging.basicConfig()
log = logging.getLogger(__name__)
log.setLevel(logging.DEBUG)

class InputEvent(Exception):
    """ Define an input flag for quick data sending and retreival """
    def __init__(self, data: str):
        self.input = data
    
    def get(self):
        return self.input

class Instruction(object):

    def __init__(self):
        raise NotImplementedError('Not implimented yet')

def cli() -> object:
    """ Get arguments from command line """
    
    log.info("starting parser")
    parser = argparse.ArgumentParser(description = "Linkage argument parser")
    parser.add_argument("--name", type = str, required = True, 
                        help = "address name")
    parser.add_argument("--num", type = int, required = True, 
                        help = "address int")
    parser.add_argument("--auth", type = str, required = True, 
                        help = "auth key")
    args = parser.parse_args()
    log.info(f"args got {args}")
    return args

def cls():
    """ Clear the terminal screen """
    os.system('cls')

def s(time_set):
    """ Sleep the program for the input amount of time in seconds """
    time.sleep(time_set)

def send_input(data: Any):
    """ Send input data. Input data must be pickleble """
    client.send(pickle.dumps(data))

def main_loop():
    """
        Keep getting input from the command line using the
        input funtion of python
    """
    try:
        while True:
            cls()
            cmd_input = input("Input: ")
            # add input parsing so only valid inputs trigger input event
            raise InputEvent(cmd_input)
    except KeyboardInterrupt:
        quit()
    except InputEvent as e:
        send_input(e.get())

def get_data():
    try:
        log.debug("getting data")
        data = pickle.loads(client.recv())
    except Exception as e:
        if e == "get_data: invalid load key, '#'.":
            log.debug("if")
            data = get_data()
        else:
            log.debug("else")
            data = get_data()
        pass
    log.debug(f"fetched data...")
    return data

if __name__ == "__main__":
    try:
        args = cli()  
    except Exception as e: # ValueError
        log.debug(f"first: {e}")
        args = {"name": "127.0.0.1", "num": 2000} 
    log.debug("attepting to connect...")
    try:
        log.debug(args)
        log.debug(args.num)
        log.debug(args.name)
        log.debug(args.auth)
        with Client((args.name, args.num)) as client:
            client = client
    except Exception as e:
        log.debug(f"second: {e}")
        s(1)
    send_input("test")
    print("connected")
    s(3)
    info_present = client.poll()
    while info_present == False:
        info_present = client.poll()
        s(0.5)
        log.debug("no info present")
    good_data = False
    tries = 0
    while good_data == False:
        try:
            data = get_data()
            good_data = True
        except Exception as e:
            log.debug(f"last debug: {e}")
            pass
            log.debug("continuing")
            data = get_data()
    log.debug("got data")
    print(data)
    time.sleep(2)
    main_loop()
