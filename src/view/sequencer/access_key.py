from ..base.view import View

from pathlib import Path
import threading
import tkinter as tk
from tkinter import messagebox

from typing import *

class AccessKeyManager(View):
    def __init__(self,
        on_error_throwed: Callable[[], None],
        on_load_complete: Callable[[str], None],
        on_save_completed: Callable[[], None]
    ):
        self.on_error_throwed = on_error_throwed
        self.on_load_complete = on_load_complete
        self.on_save_completed = on_save_completed

        self.error_message = ""

        self.manager = Access()

        self._common_lock = threading.Lock()
        self._ak: str | None = None
        self._errored = False
        self._saved = False
    
    def load(self):
        def hdl_read_ak():
            result = self.manager.read()

            with self._common_lock:
                if isinstance(result, int):
                    self._errored = True
                else:
                    self._ak = result if result is not None else ""
        
        if self._common_lock.acquire(blocking=False):
            trd = threading.Thread(target=hdl_read_ak)
            trd.start()

            self._common_lock.release()

            processed = True
        else: 
            processed = False 
        
        return processed
    
    def save(self, key: str):
        def hdl_write_ak():
            result = self.manager.write(key)

            with self._common_lock:
                if result < 0:
                    self._errored = True
                else:
                    self._saved = True
        
        if self._common_lock.acquire(blocking=False):
            trd = threading.Thread(target=hdl_write_ak)
            trd.start()

            self._common_lock.release()

            processed = True
        else: 
            processed = False 
        
        return processed
    
    def get_error_message(self):
        return self.error_message

    def update(self):
        if self._common_lock.acquire(blocking=False):
            if self._errored:
                self.error_message = "ファイルへのアクセスに失敗しました。プログラムとディレクトリの権限が影響している可能性があります。"
                self.on_error_throwed()
                self._errored = False
            if self._ak is not None:
                self.on_load_complete(self._ak)
                self._ak = None
            if self._saved:
                self.on_save_completed()
                self._saved = False

            self._common_lock.release()
    
    def draw(self):
        pass

from ...file_path import *

class Access:
    ROOT_PATH = ROOT_PATH
    LOG_FILE_PATH = LOG_FILE_PATH
    SECRET_DIRECTORY_PATH = "territory_game/secret"
    SECRET_FILE_PATH = "territory_game/secret/secret.properties"
    PROPERTY_NAME = "ACCESS_KEY"

    def write(self, key: str):
        home = Path.home()
        directory = home / self.SECRET_DIRECTORY_PATH
        file_path = home / self.SECRET_FILE_PATH
        
        try:
            directory.mkdir(parents=True, exist_ok=True)
            file_path.write_text(f'{self.PROPERTY_NAME}={key}', encoding='utf-8')
            return 0
        except OSError:
            return -1

    def read(self) -> str | None | int:
        # ホームディレクトリからのパスを作成
        home = Path.home()
        directory = home / self.SECRET_DIRECTORY_PATH
        file_path = home / self.SECRET_FILE_PATH

        try:
            directory.mkdir(parents=True, exist_ok=True)
            if not file_path.exists():
                return None
            # ファイルを読み込む
            content = file_path.read_text(encoding='utf-8')
            return content.split("=")[1]
            
        except OSError as e:
            return -1
