"""
IO v0.1

Author  : Christian Carter
Date    : 13 June 2021

Contains classes that connect the game engine with the input and the display. 
"""
version_info = "v0.2"
from multiprocessing import connection
from multiprocessing.context import AuthenticationError
import os
import time
import dill
import pickle
from secrets import token_bytes
from multiprocessing import Process, Pipe, Queue
from multiprocessing.connection import Connection, Listener, Client
from typing import Any, List, Tuple
import logging

logging.basicConfig()
log = logging.getLogger(__name__)
log.setLevel(logging.DEBUG)

class Input(object):

    def __init__(self, max_attempts: int, address: int):
        """
            creates the input terminal and connects to it allowing
            Instruction objects to be passed through
        """
        self.__path = os.path.realpath(__file__)
        self.__address = ('localhost', address)
        self.__auth_key = token_bytes(10)
        self.__auth_list = list(self.__auth_key)
        self.max_attempts = max_attempts
        self.__connect_attempt = 0
        self.connect()

    def authkey_str(self) -> str:
        token = f"{self.__auth_key}"
        return token

    def connect(self, script_str: str = 'InputScreen.py', 
    data: Any = pickle.dumps("Test", protocol=5,buffer_callback=True)):
        """establishes a connection with the GameInstance object"""
        cmd_arg = f'start cmd /k python "G:\Personal Projects\TextGame\{script_str}" --name {self.__address[0]} --num {self.__address[1]} --auth ' + self.authkey_str()
        # time.sleep(1)
        self.listen = Listener(self.__address)
        while 1:
            try:
                log.debug("starting Input Screen")
                os.system(cmd_arg)
                log.debug("connection attempt started")
                if data != None:
                    self.connection: Connection = self.listen.accept()
                    if dill.pickles(data):
                        self.connection.send(data)
                log.info('Connection successful')
                break
            except AuthenticationError:
                if self.__connect_attempt <= self.max_attempts:
                    self.__connect_attempt += 1
                    continue
                else:
                    log.info(f"""Failed to authenticate on port:
                    {self.__address[1]}. Aborting...""")
                    quit()

    def send(self, instruct):
        assert dill.pickles(instruct), "data not picklable"
        self.connection.send(pickle.dumps(instruct))

    def get(self) -> Any:
        while not self.connection.poll():
            continue
        return pickle.loads(self.connection.recv())

class Output(Input):

    def __init__(self, max_attempts: int, address: int):
        super().__init__(max_attempts, address)

    def connect(self, script_str: str = 'Display.py'):
        return super().connect(script_str = script_str, data = "Testing Output")
    
    def send(self, instruct):
        return super().send(instruct)
    
    def get(self) -> Any:
        return super().get()
