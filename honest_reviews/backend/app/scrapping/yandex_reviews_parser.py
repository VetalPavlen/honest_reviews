# Основной парсер Яндекса
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
import time
import random
from loguru import logger
from honest_reviews.backend.app.secondary_functions.human_interaction import HumanInteraction
from honest_reviews.backend.app.secondary_functions.proxy_manager import ProxyManager
from honest_reviews.backend.app.secondary_functions.browser_manager import BrowserManager


class YandexReviewsParser:
    def __init__(self, config):
        self.config = config
        self.proxy_manager = ProxyManager(config)
        self.browser_manager = BrowserManager(config)

    def parse_reviews(self, org_id: str) -> bool:
        proxy = self.proxy_manager.get_random_proxy()
        if not proxy:
            logger.error("Не найдено рабочих прокси")
            return False

        driver = None
        try:
            driver = self.browser_manager.init_driver(proxy)
            if not driver:
                return False

            driver.set_page_load_timeout(30)
            url = self.config.yandex_reviews_url.format(org_id=org_id)
            driver.get(url)
            time.sleep(random.uniform(2, 4))

            HumanInteraction.simulate(driver)

            try:
                WebDriverWait(driver, 25).until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, "div.business-reviews-card-view"))
                )
                logger.success("Блок отзывов обнаружен")
            except Exception as e:
                logger.warning(f"Блок отзывов не найден: {e}")
                return False

            HumanInteraction.smart_scroll(driver)
            HumanInteraction.simulate(driver)
            time.sleep(random.uniform(2, 3))

            with open(self.config.debug_html, "w", encoding="utf-8") as f:
                f.write(driver.page_source)

            logger.success(f"Успешно получены данные через прокси: {proxy.split(':')[0]}:****")
            return True
        except Exception as e:
            logger.error(f"Ошибка при парсинге: {str(e)[:200]}...")
            return False
        finally:
            if driver:
                driver.quit()
