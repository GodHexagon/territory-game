from enum import Enum
from typing import *
from abc import ABC, abstractmethod
import traceback
import json

import requests

from ...access.commander import Commander, PusherError
from .access_event import SequencerEvent
from ..base.view import View

class Error(Enum):
    NETWORK_ERROR = 0
    IMPLEMENTATION_ERROR = 1
    SERVER_ERROR = 2
    PUSHER_ERROR = 3

class GameAccessSequencer(View, ABC):
    def create_commander(self,
        on_error_throwed: Callable[['Error'], None],
        access_key: str
    ):
        self.error_event = SequencerEvent(on_error_throwed)
        
        self.commander = Commander(
            access_key,
            self._handle_error,
            lambda: None,
            self._handle_response,
            self._handle_game_message
        )
        
    def _handle_error(self, e: Exception) -> None:
        """エラーコールバック"""
        if isinstance(e, PusherError):
            ve = e.internal
            tb = traceback.format_exception(type(ve), ve, ve.__traceback__)
            message = f"{Error.PUSHER_ERROR}:\nPusher throw ValueError:\n" + ''.join(tb)
            print(message)
            self.error_event.pend(Error.PUSHER_ERROR)
        elif isinstance(e, OSError): 
            tb = traceback.format_exception(type(e), e, e.__traceback__)
            message = f"{Error.NETWORK_ERROR}:\n" + ''.join(tb)
            print(message)
            self.error_event.pend(Error.NETWORK_ERROR)
        else: 
            tb = traceback.format_exception(type(e), e, e.__traceback__)
            message = f"{Error.IMPLEMENTATION_ERROR}:\n" + ''.join(tb)
            print(message)
            self.error_event.pend(Error.IMPLEMENTATION_ERROR)

    def _handle_response(self, response: requests.Response) -> None:
        """APIサーバ接続のレスポンスコールバック"""
        if 500 <= response.status_code and response.status_code <= 599:
            message = f"{Error.SERVER_ERROR}:\n\
                        [{response.status_code}] {response.reason}\n\
                        Response body:\n{response.text}"
            print(message)
            self.error_event.pend(Error.SERVER_ERROR)
        elif response.status_code == 408: 
            message = f"{Error.SERVER_ERROR}:\n\
                        [{response.status_code}] {response.reason}\n\
                        Response body:\n{response.text}"
            print(message)
            self.error_event.pend(Error.SERVER_ERROR)
        elif response.status_code != 200:
            message = f"{Error.IMPLEMENTATION_ERROR}:\n\
                        [{response.status_code}] {response.reason}\n\
                        Response body:\n{response.text}"
            print(message)
            self.error_event.pend(Error.IMPLEMENTATION_ERROR)
        else:
            self.process_initialization_data(response)

    def _handle_game_message(self, message: str) -> None:
        """ゲームメッセージコールバック"""
        self.process_message(message)

    def draw(self):
        raise ValueError("シーケンサーはdrawメソッドを実行できない。")
    
    def message(self, json_str: str) -> None:
        raise RuntimeError("Not impemented.")
    
    @abstractmethod
    def process_initialization_data(self, response: requests.Response):
        pass

    @abstractmethod
    def process_message(self, json_str: str):
        pass

class HostAccessSequencer(GameAccessSequencer):
    OnHostedToServerArg: TypeAlias = List[str]
    OnPlayerJoinedArg: TypeAlias = str
    OnAllPlayersHereArg: TypeAlias = bool
    OnHostedToServerCallable: TypeAlias = Callable[[List[str]], None]
    OnPlayerJoinedCallable: TypeAlias = Callable[[str], None]
    OnAllPlayersHereCallable: TypeAlias = Callable[[bool], None]
    
    def __init__(self, access_key: str, on_error_throwed: Callable[[Error], None]):
        super().create_commander(on_error_throwed, access_key)

        self.hosted_to_server_event: SequencerEvent["HostAccessSequencer.OnHostedToServerArg"] | None = None
        self.player_joined_event: SequencerEvent["HostAccessSequencer.OnPlayerJoinedArg"] | None = None
        self.all_player_here_event: SequencerEvent["HostAccessSequencer.OnAllPlayersHereArg"] | None = None

    def connect(self,
            player_number: int,
            handlers: Tuple["HostAccessSequencer.OnHostedToServerCallable",
                "HostAccessSequencer.OnPlayerJoinedCallable",
                "HostAccessSequencer.OnAllPlayersHereCallable"]
        ) -> None:
        """
        handlers = tuple(on_hosted_to_server, on_player_joined, on_all_players_here)
        """

        self.hosted_to_server_event = SequencerEvent(handlers[0])
        self.player_joined_event = SequencerEvent(handlers[1])
        self.all_player_here_event = SequencerEvent(handlers[2])

        self.commander.host(player_number)
    
    def process_initialization_data(self, response: requests.Response):
        try:
            data = response.json()
            players = data["initialization_data"]["players"]
            ps = [
                p["password"]
                for p in players
                if not p["assignment"]
            ]
            
            if not all(isinstance(p, str) for p in ps):
                # パスワードが文字列でない場合は型エラーとみなす
                raise TypeError("Invalid type for password in response.")

        except (KeyError, TypeError, requests.exceptions.JSONDecodeError) as e:
            message = f"{Error.IMPLEMENTATION_ERROR}:\nResponse is incorrect. Response body:\n{response.text}"
            print(message)
            self.error_event.pend(Error.IMPLEMENTATION_ERROR)
            return
            
        if self.hosted_to_server_event is None:
            raise ValueError("Commanderクラスによる不適切なコールバック呼び出し。")

        self.hosted_to_server_event.pend(ps)
    
    def update(self):
        """
        フレームごとの更新処理
        """
        self.error_event.update()
        
        if self.hosted_to_server_event is not None:
            self.hosted_to_server_event.update()
        if self.player_joined_event is not None:
            self.player_joined_event.update()
        if self.all_player_here_event is not None:
            self.all_player_here_event.update()

    def process_message(self, json_str: str):
        try:
            message = json.loads(json_str)
            event_type = message.get("event")
            data = message.get("data")

            if event_type == "player_joined":
                if self.player_joined_event is None:
                    raise ValueError("player_joined_event is not initialized.")
                if not isinstance(data, str):
                    raise TypeError("Invalid data type for player_joined event.")
                self.player_joined_event.pend(data)

            elif event_type == "all_players_here":
                if self.all_player_here_event is None:
                    raise ValueError("all_player_here_event is not initialized.")
                if not isinstance(data, bool):
                    raise TypeError("Invalid data type for all_players_here event.")
                self.all_player_here_event.pend(data)

        except (json.JSONDecodeError, KeyError, TypeError, ValueError) as e:
            log = f"{Error.IMPLEMENTATION_ERROR}:\nFailed to process game message: {json_str}\n" + ''.join(traceback.format_exception(type(e), e, e.__traceback__))
            print(log)
            self.error_event.pend(Error.IMPLEMENTATION_ERROR)

from src.data import players_data

class JoinAccessSequencer(GameAccessSequencer):
    OnJoinedArg: TypeAlias = Tuple[int, List[players_data.PlayerData]]
    OnPlayerJoinedArg: TypeAlias = str
    OnAllPlayersHereArg: TypeAlias = bool
    OnJoinedCallable: TypeAlias = Callable[[Tuple[int, List[players_data.PlayerData]]], None]
    OnPlayerJoinedCallable: TypeAlias = Callable[[str], None]
    OnAllPlayersHereCallable: TypeAlias = Callable[[bool], None]

    def __init__(self, access_key: str, on_error_throwed: Callable[[Error], None]):
        super().create_commander(on_error_throwed, access_key)
    
    def connect(self,
            password: str,
            on_joined_callback: "JoinAccessSequencer.OnJoinedCallable",
            on_player_joined_callback: "JoinAccessSequencer.OnPlayerJoinedCallable",
            on_all_players_here_callback: "JoinAccessSequencer.OnAllPlayersHereCallable"
        ) -> None:
        self.joined_event = SequencerEvent(on_joined_callback)
        self.player_joined_event = SequencerEvent(on_player_joined_callback)
        self.all_player_here_event = SequencerEvent(on_all_players_here_callback)

        self.commander.join(password)
        
    def process_initialization_data(self, response: requests.Response):
        if self.joined_event is None:
            raise ValueError("Commanderクラスによる不適切なコールバック呼び出し。")

        try:
            data = response.json()
            init_data = data["initialization_data"]
            player_id = init_data["player_id"]
            players = init_data["players"]

            if not isinstance(player_id, int):
                raise TypeError("Invalid type for player_id in response.")
            if not isinstance(players, list):
                raise TypeError("Invalid type for players in response.")

            arg: "JoinAccessSequencer.OnJoinedArg" = (player_id, players)
            self.joined_event.pend(arg)

        except (KeyError, TypeError, requests.exceptions.JSONDecodeError):
            message = f"{Error.IMPLEMENTATION_ERROR}:\nResponse is incorrect. Response body:\n{response.text}"
            print(message)
            self.error_event.pend(Error.IMPLEMENTATION_ERROR)

    def process_message(self, json_str: str):
        try:
            message = json.loads(json_str)
            event_type = message.get("event")
            data = message.get("data")

            if event_type == "player_joined":
                if self.player_joined_event is None:
                    raise ValueError("player_joined_event is not initialized.")
                if not isinstance(data, str):
                    raise TypeError("Invalid data type for player_joined event.")
                self.player_joined_event.pend(data)

            elif event_type == "all_players_here":
                if self.all_player_here_event is None:
                    raise ValueError("all_player_here_event is not initialized.")
                if not isinstance(data, bool):
                    raise TypeError("Invalid data type for all_players_here event.")
                self.all_player_here_event.pend(data)

        except (json.JSONDecodeError, KeyError, TypeError, ValueError) as e:
            log = f"{Error.IMPLEMENTATION_ERROR}:\nFailed to process game message: {json_str}\n" + ''.join(traceback.format_exception(type(e), e, e.__traceback__))
            print(log)
            self.error_event.pend(Error.IMPLEMENTATION_ERROR)
