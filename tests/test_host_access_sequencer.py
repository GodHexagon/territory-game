__package__ = "src"

import unittest
from unittest.mock import Mock, patch
from typing import List

from src.view.sequencer.game_access import HostAccessSequencer, Error  # クラスが定義されているモジュールを指定

class TestHostAccessSequencer(unittest.TestCase):
    def setUp(self):
        self.on_error = Mock()
        self.sequencer = HostAccessSequencer("dummy_key", self.on_error)

    def test_connect_sets_event_handlers(self):
        hosted_cb = Mock()
        joined_cb = Mock()
        all_here_cb = Mock()

        self.sequencer.connect(3, (hosted_cb, joined_cb, all_here_cb))

        self.assertIsNotNone(self.sequencer.hosted_to_server_event)
        self.assertIsNotNone(self.sequencer.player_joined_event)
        self.assertIsNotNone(self.sequencer.all_player_here_event)

    @patch("requests.Response")
    def test_handle_response_success(self, mock_response):
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "initialization_data": {
                "players": [
                    {"password": "pw1", "assignment": False},
                    {"password": "pw2", "assignment": True},
                ]
            }
        }

        self.sequencer.hosted_to_server_event = Mock()
        self.sequencer._handle_response(mock_response)

        self.sequencer.hosted_to_server_event.pend.assert_called_once_with(["pw1"])
        
    @patch("requests.Response")
    def test_handle_response_success_four_player(self, mock_response):
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "initialization_data": {
                "players": [
                    {"password": "pw1", "assignment": False},
                    {"password": "pw2", "assignment": False},
                    {"password": "pw3", "assignment": False},
                    {"password": "pw4", "assignment": True}
                ]
            }
        }

        self.sequencer.hosted_to_server_event = Mock()
        self.sequencer._handle_response(mock_response)

        self.sequencer.hosted_to_server_event.pend.assert_called_once_with(["pw1", "pw2", "pw3"])
        
    @patch("requests.Response")
    def test_handle_response_ve_missing_assignment(self, mock_response):
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "initialization_data": {
                "players": [
                    {"password": "pw1", "ssignment": False},
                    {"password": "pw2", "assignment": True},
                ]
            }
        }

        self.sequencer.error_event = Mock()
        self.sequencer._handle_response(mock_response)

        self.sequencer.error_event.pend.assert_called_once_with(Error.IMPLEMENTATION_ERROR)
        
    @patch("requests.Response")
    def test_handle_response_ve_missing_password(self, mock_response):
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "initialization_data": {
                "players": [
                    {"assword": "pw1", "assignment": False},
                    {"password": "pw2", "assignment": True},
                ]
            }
        }

        self.sequencer.error_event = Mock()
        self.sequencer._handle_response(mock_response)

        self.sequencer.error_event.pend.assert_called_once_with(Error.IMPLEMENTATION_ERROR)
        
    @patch("requests.Response")
    def test_handle_response_ve_missing_players(self, mock_response):
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "initialization_data": {
                "layers": [
                    {"password": "pw1", "assignment": False},
                    {"password": "pw2", "assignment": True},
                ]
            }
        }

        self.sequencer.error_event = Mock()
        self.sequencer._handle_response(mock_response)

        self.sequencer.error_event.pend.assert_called_once_with(Error.IMPLEMENTATION_ERROR)
        
    @patch("requests.Response")
    def test_handle_response_ve_missing_initialization_data(self, mock_response):
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "nitialization_data": {
                "layers": [
                    {"password": "pw1", "assignment": False},
                    {"password": "pw2", "assignment": True},
                ]
            }
        }

        self.sequencer.error_event = Mock()
        self.sequencer._handle_response(mock_response)

        self.sequencer.error_event.pend.assert_called_once_with(Error.IMPLEMENTATION_ERROR)



if __name__ == "__main__":
    unittest.main()
