# Основной парсер Яндекса
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from honest_reviews.config.config_loader import CHROMEDRIVER_PATH, YANDEX_URL
from honest_reviews.app.secondary_functions.proxy_manager import ProxyManager
from honest_reviews.app.secondary_functions.behavior_simulation import UserBehavior
import time
import random
import logging


class Scraper:
    def __init__(self, org_id):
        self.org_id = org_id
        self.proxy_manager = ProxyManager()  # путь берётся из config_loader.py
        self.user_behavior = None

    def init_driver(self, proxy):
        """Инициализация Chrome-драйвера с прокси"""
        options = Options()
        options.add_argument("--disable-blink-features=AutomationControlled")
        options.add_argument("--window-size=1920,1080")
        options.add_experimental_option("excludeSwitches", ["enable-automation"])
        options.add_experimental_option('useAutomationExtension', False)

        proxy_parts = proxy.split(":")
        if len(proxy_parts) >= 2:
            proxy_address = f"{proxy_parts[0]}:{proxy_parts[1]}"
            options.add_argument(f"--proxy-server={proxy_address}")

        driver = webdriver.Chrome(executable_path=CHROMEDRIVER_PATH, options=options)
        self.user_behavior = UserBehavior(driver)
        return driver

    def fetch_reviews_page(self):
        proxies = self.proxy_manager.get_proxies()
        random.shuffle(proxies)
        max_attempts = min(10, len(proxies))

        for proxy in proxies[:max_attempts]:
            if self.proxy_manager.is_proxy_working(proxy):
                logging.info(f"[Scraper] Используется рабочий прокси: {proxy}")
                driver = self.init_driver(proxy)
                try:
                    url = YANDEX_URL.format(org_id=self.org_id)
                    driver.get(url)
                    time.sleep(random.uniform(2, 4))
                    self.user_behavior.safe_interaction()
                    self.user_behavior.smart_scroll()
                    return True
                except Exception as e:
                    logging.error(f"[Scraper] Ошибка при парсинге с прокси {proxy}: {e}")
                finally:
                    driver.quit()
        logging.warning("[Scraper] Не удалось найти рабочий прокси")
        return False
