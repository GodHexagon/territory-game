from ..view import View

from pathlib import Path
import threading

from typing import *
from enum import Enum
import os
import platform

class AccessKeyManager(View):
    def __init__(self,
        on_error_throwed: Callable[[], None],
        on_load_complete: Callable[[str], None],
        on_save_completed: Callable[[], None]
    ):
        self.on_error_throwed = on_error_throwed
        self.on_load_complete = on_load_complete
        self.on_save_completed = on_save_completed

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

    def update(self):
        if self._common_lock.acquire(blocking=False):
            if self._errored:
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

class Access:
    ROOT_PATH = "territory_game"
    LOG_FILE_PATH = "territory_game/log.txt"
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
            self.__log("ファイルへのアクセスに失敗しました。プログラムとディレクトリの権限が影響している可能性があります。")
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
            self.__log("ファイルへのアクセスに失敗しました。プログラムとディレクトリの権限が影響している可能性があります。")
            return -1
    
    def __log(self, message: str):
        home = Path.home()
        directory = home / self.SECRET_DIRECTORY_PATH
        directory.mkdir(parents=True, exist_ok=True)
        log_path = home / self.LOG_FILE_PATH

        log_path.write_text(f'エラー：{message}', encoding='utf-8')

        # OSによって異なるコマンドを使用してファイルを開く
        if platform.system() == 'Windows':
            os.startfile(log_path)
        elif platform.system() == 'Darwin':  # macOS
            os.system(f'open {log_path}')
        else:  # Linux
            os.system(f'xdg-open {log_path}')
