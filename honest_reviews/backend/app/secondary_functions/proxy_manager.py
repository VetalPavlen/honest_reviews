# Управление прокси
# Импорт необходимых модулей
import random
import requests
from requests.auth import HTTPProxyAuth
from loguru import logger
from typing import List, Optional
from honest_reviews.backend.config.config_loader import Config

class ProxyManager:
    def __init__(self, config: Config):
        self.config = config
        self.proxies = self._load_proxies()

    def _load_proxies(self) -> List[str]:
        try:
            with open(self.config.proxy_list_file, "r") as f:
                proxies = [line.strip() for line in f if line.strip()]
            logger.info(f"Загружено {len(proxies)} прокси")
            return proxies
        except Exception as e:
            logger.error(f"Ошибка при чтении файла прокси: {e}")
            return []

    def get_random_proxy(self) -> Optional[str]:
        if not self.proxies:
            return None
        random.shuffle(self.proxies)
        for proxy in self.proxies[:10]:
            if self.is_proxy_working(proxy):
                return proxy
        return None

    def is_proxy_working(self, proxy: str) -> bool:
        try:
            proxy_address = f"http://{proxy}"
            proxies = {"http": proxy_address, "https": proxy_address}
            auth = HTTPProxyAuth(self.config.proxy_username, self.config.proxy_password)
            response = requests.get("http://httpbin.org/ip", proxies=proxies, auth=auth, timeout=10)
            return response.status_code == 200
        except requests.exceptions.RequestException as e:
            logger.error(f"Ошибка с прокси {proxy}: {str(e)}")
            return False
