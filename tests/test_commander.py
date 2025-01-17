__package__ = "src"

import unittest
from unittest.mock import Mock, patch
import requests
import json
from typing import Dict, Any

from src.access.commander import Commander  # 適切なインポートパスに修正してください

class TestCommander(unittest.TestCase):
    def setUp(self):
        # コールバック関数のモック
        self.mock_on_errored = Mock()
        self.mock_on_connected_to_pusher = Mock()
        self.mock_on_responsed = Mock()
        self.mock_on_recieved = Mock()

        # Commanderインスタンスの作成
        self.commander = Commander(
            access_key="test_key",
            on_errored=self.mock_on_errored,
            on_connected_to_pusher=self.mock_on_connected_to_pusher,
            on_responsed=self.mock_on_responsed,
            on_recieved=self.mock_on_recieved
        )

    def create_mock_response(self, data: Dict[str, Any]) -> Mock:
        mock_response = Mock(spec=requests.Response)
        mock_response.json.return_value = data
        return mock_response

    @patch('requests.post')
    @patch('pysher.Pusher')
    def test_host(self, mock_pusher_class, mock_post):
        # モックレスポンスの設定
        mock_response = self.create_mock_response({
            "channel_name": "test_channel",
            "pusher_auth": "test_auth",
            "initialization_data": {
                "owner_password": "test_password"
            }
        })
        mock_post.return_value = mock_response

        # Pusherのモックの設定
        mock_pusher = Mock()

        # コネクション
        mock_connection = Mock()
        mock_connection.socket_id = "test_socket_id"
        mock_pusher.connection = mock_connection

        # サブスクライブ
        mock_channel = Mock()
        mock_subscribe = Mock()
        mock_subscribe.return_value = mock_channel
        mock_pusher.subscribe = mock_subscribe

        mock_pusher_class.return_value = mock_pusher

        # hostメソッドの実行
        self.commander.host(player_number=2)

        # Pusherの接続イベントをシミュレート
        connection_callback = mock_pusher.connection.bind.call_args[0][1]
        connection_callback(json.dumps({"socket_id": "test_socket_id"}))

        # ゲームメッセージ受信をシミュレート
        subscribe_callback = mock_channel.bind.call_args[0][1]
        subscribe_callback("test_game_message")

        # 検証
        mock_post.assert_called_with(
            "https://territory-game-server-docker-604712033635.asia-northeast1.run.app",
            json={
                "command": "host",
                "access_key": "test_key",
                "content": {
                    "player_number": 2,
                    "socket_id": "test_socket_id"
                }
            },
            verify=True
        )
        self.mock_on_responsed.assert_called_with(mock_response)
        self.mock_on_connected_to_pusher.assert_called_once()
        self.mock_on_recieved.assert_called_with("test_game_message")

    @patch('requests.post')
    @patch('pysher.Pusher')
    def test_join(self, mock_pusher_class, mock_post):
        # モックレスポンスの設定
        mock_response = self.create_mock_response({
            "channel_name": "test_channel",
            "pusher_auth": "test_auth"
        })
        mock_post.return_value = mock_response

        # Pusherのモックの設定
        mock_pusher = Mock()

        # コネクション
        mock_connection = Mock()
        mock_connection.socket_id = "test_socket_id"
        mock_pusher.connection = mock_connection

        # サブスクライブ
        mock_channel = Mock()
        mock_subscribe = Mock()
        mock_subscribe.return_value = mock_channel
        mock_pusher.subscribe = mock_subscribe

        mock_pusher_class.return_value = mock_pusher

        # joinメソッドの実行
        self.commander.join(password="test_password")

        # Pusherの接続イベントをシミュレート
        connection_callback = mock_pusher.connection.bind.call_args[0][1]
        connection_callback(json.dumps({"socket_id": "test_socket_id"}))

        # ゲームメッセージ受信をシミュレート
        subscribe_callback = mock_channel.bind.call_args[0][1]
        subscribe_callback("test_game_message")

        # 検証
        mock_post.assert_called_with(
            "https://territory-game-server-docker-604712033635.asia-northeast1.run.app",
            json={
                "command": "join",
                "access_key": "test_key",
                "content": {
                    "password": "test_password",
                    "socket_id": "test_socket_id"
                }
            },
            verify=True
        )
        self.mock_on_responsed.assert_called_with(mock_response)
        self.mock_on_connected_to_pusher.assert_called_once()
        self.mock_on_recieved.assert_called_once()

    @patch('requests.post')
    def test_broadcast(self, mock_post):
        # 事前条件の設定
        mock_response = self.create_mock_response({
            "channel_name": "test_channel"
        })
        self.commander.prev = mock_response
        self.commander.p = "test_password"

        # broadcastメソッドの実行
        self.commander.broadcast(message="test_message")

        # スレッドの完了を待つ
        import time
        time.sleep(0.1)

        # 検証
        mock_post.assert_called_with(
            "https://territory-game-server-docker-604712033635.asia-northeast1.run.app",
            json={
                "command": "broadcast",
                "access_key": "test_key",
                "content": {
                    "channel_name": "test_channel",
                    "password": "test_password",
                    "message": "test_message"
                }
            },
            verify=True
        )

    @patch('requests.post')
    def test_network_error(self, mock_post):
        # ネットワークエラーのシミュレーション
        mock_post.side_effect = OSError("Network error")

        # 事前条件の設定
        mock_response = self.create_mock_response({
            "channel_name": "test_channel"
        })
        self.commander.prev = mock_response
        self.commander.p = "test_password"

        # broadcastメソッドの実行
        self.commander.broadcast(message="test_message")

        # スレッドの完了を待つ
        import time
        time.sleep(0.1)

        # エラーコールバックが呼ばれたことを確認
        self.mock_on_errored.assert_called_once()
        error = self.mock_on_errored.call_args[0][0]
        self.assertIsInstance(error, OSError)

if __name__ == '__main__':
    unittest.main()