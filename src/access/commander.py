import requests
import pysher # type:ignore

from typing import *
from pathlib import Path
import os
import platform
import threading

from ..file_path import *

URI = "https://territory-game-server-docker-604712033635.asia-northeast1.run.app"

class Commander:
    def __init__(self,
        access_key: str,
        on_errored: Callable[[Exception], None],
        on_connected_to_pusher: Callable[[], None],
        on_responsed: Callable[[requests.Response], None],
        on_recieved: Callable[[str], None],
    ):
        """コールバック関数は別スレッドで実行されます。"""
        
        self.access_key = access_key
        self.on_errored = on_errored
        self.on_connected_to_pusher = on_connected_to_pusher
        self.on_responsed = on_responsed
        self.on_recieved = on_recieved
        
        self.prev: requests.Response | None = None
        self.p: str | None = None
    
    def host(self,
        player_number: int
    ) -> None:
        def hdl_connected(socket_id: str):
            sample_data = {
                "command": "host",
                "access_key": self.access_key,
                "content": { 
                    "player_number" : player_number,
                    "socket_id" : socket_id 
                }
            }

            try:
                self.prev = requests.post(URI, json=sample_data, verify=True)

                self.p = self.prev.json()["initialization_data"]["owner_password"]
                self.on_responsed(self.prev)
                return self.prev.json()["channel_name"], self.prev.json()["pusher_auth"]
            except OSError as e:
                self.on_errored(e)

        self.__pusher_subscribe(
            self.on_recieved,
            hdl_connected,
            "broadcast"
        )
    
    def join(self,
        password: str
    ) -> None:
        def hdl_connected(socket_id: str):
            sample_data = {
                "command": "join",
                "access_key": self.access_key,
                "content": { 
                    "password": password,
                    "socket_id" : socket_id 
                }
            }

            try:
                self.prev = requests.post(URI, json=sample_data, verify=True)
                
                self.p = password
                self.on_responsed(self.prev)
                return self.prev.json()["channel_name"], self.prev.json()["pusher_auth"]
            except OSError as e:
                self.on_errored(e)

        self.__pusher_subscribe(
            self.on_recieved,
            hdl_connected,
            "broadcast"
        )
    
    def __pusher_subscribe(self,
            on_recieved: Callable[[str], None],
            get_auth: Callable[[str], Tuple[str, str]], 
            event_name: str
        ):
        # We can't subscribe until we've connected, so we use a callback handler
        # to subscribe when able
        def connect_handler(_):
            self.on_connected_to_pusher()
            try:
                channel = pusher.subscribe(*get_auth(pusher.connection.socket_id))
                channel.bind(event_name, on_recieved)
            except ValueError as e:
                self.on_errored(PusherError(e))

        pusher = pysher.Pusher(
            key="06f286e121ad2b17de17",
            cluster='ap3',
            secure=True
        )

        pusher.connection.bind('pusher:connection_established', connect_handler)
        pusher.connect()
    
    def broadcast(self,
        message: str
    ) -> None:
        def connect():
            if self.prev is None: raise ValueError("まだ接続していないのにブロードキャストを送信しようとした。")
            sample_data = {
                "command": "broadcast",
                "access_key": self.access_key,
                "content": { 
                    "channel_name" : self.prev.json()["channel_name"],
                    "password" : self.p,
                    "message" : message
                }
            }

            try:
                self.prev = requests.post(URI, json=sample_data, verify=True)
            except OSError as e:
                self.on_errored(e)
        
        thr_connecting = threading.Thread(target=connect)
        thr_connecting.start()

class PusherError(Exception):
    def __init__(self, *args):
        super().__init__(*args)
        self.internal = cast(ValueError, args[0])
