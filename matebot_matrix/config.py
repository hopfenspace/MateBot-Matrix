"""
MateBot Matrix configuration provider
"""

import logging.config

from hopfenmatrix.config import Config, Namespace


class MateBotConfig(Config):
    def __init__(self):
        super(MateBotConfig, self).__init__()
        del self["logging"]

        self.room = ""

        self.api = Namespace()
        self.api.base_url = "<Base URL to the MateBot backend server>"
        self.api.app_name = "<Name of your deployed application>"
        self.api.app_password = "<Password of your deployed application>"
        self.api.ca_path = None

        self.api.callback = Namespace()
        self.api.callback.enabled = True
        self.api.callback.address = "127.0.0.1"
        self.api.callback.port = 8080
        self.api.callback.public_url = "<Public base URL of the callback server (reachable by the API server)>"
        self.api.callback.username = None
        self.api.callback.password = None

        self.client = Namespace()
        self.client.adjust_stock = True
        self.client.respect_stock = True

        self.database = Namespace()
        self.database.host = "localhost"
        self.database.port = 3306
        self.database.db = "mate_db"
        self.database.user = "matebot_user"
        self.database.password = "password"
        self.database.charset = "utf8mb4"

        self.logging = Namespace()
        self.logging.version = 1
        self.logging.disable_existing_loggers = False
        self.logging.incremental = False

        self.logging.root = Namespace()
        self.logging.root.level = "INFO"
        self.logging.root.handlers = ["console", "file"]

        self.logging.formatters = Namespace()
        self.logging.handlers = Namespace()
        self.logging.filters = Namespace()
        self.logging.formatters.console = {
            "style": "{",
            "class": "logging.Formatter",
            "format": "{asctime}: MateBot {process}: [{levelname}] {name}: {message}",
            "datefmt": "%d.%m.%Y %H:%M"
        }
        self.logging.formatters.file = {
            "style": "{",
            "class": "logging.Formatter",
            "format": "matebot {process}: [{levelname}] {name}: {message}",
            "datefmt": "%d.%m.%Y %H:%M"
        }
        self.logging.handlers.console = {
            "level": "INFO",
            "class": "logging.StreamHandler",
            "formatter": "console",
            "filters": ["no_peewee_debug"],
            "stream": "ext://sys.stdout"
        }
        self.logging.handlers.file = {
            "level": "INFO",
            "class": "logging.handlers.WatchedFileHandler",
            "formatter": "file",
            "filters": ["no_peewee_debug"],
            "filename": "matebot_matrix.log",
            "encoding": "UTF-8"
        }
        self.logging.filters.no_peewee_debug = {
            "()": "hopfenmatrix.logging.NotBelowFilter",
            "name": "peewee",
            "level": logging.INFO
        }

    def setup_logging(self):
        logging.config.dictConfig(self.logging)
