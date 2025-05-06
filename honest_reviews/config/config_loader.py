from loguru import logger
import configparser
from dataclasses import dataclass

@dataclass
class Config:
    chromedriver_path: str
    proxy_list_file: str
    debug_html: str
    yandex_reviews_url: str
    proxy_username: str
    proxy_password: str

class ConfigLoader:
    @staticmethod
    def load_config(config_path: str = 'config.ini') -> Config:
        config = configparser.ConfigParser()
        config.read(config_path)

        loaded_config = Config(
            chromedriver_path=config['Paths']['chromedriver_path'],
            proxy_list_file=config['Paths']['proxy_list_file'],
            debug_html=config['Paths']['debug_html'],
            yandex_reviews_url=config['URLs']['yandex_reviews_url'],
            proxy_username=config['ProxyAuth'].get('username', ''),
            proxy_password=config['ProxyAuth'].get('password', '')
        )

        print("Загруженная конфигурация:", loaded_config)
        logger.debug(f"Загруженная конфигурация: {loaded_config}")

        return loaded_config

# 🔽 Эта часть будет выполнена только при запуске напрямую
if __name__ == "__main__":
    config = ConfigLoader.load_config()
