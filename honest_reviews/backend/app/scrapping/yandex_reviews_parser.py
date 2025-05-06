from selenium.webdriver import Chrome  # Добавляем этот импорт
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
import time
import random
from loguru import logger
from typing import Optional
from honest_reviews.backend.app.secondary_functions.human_interaction import HumanInteraction
from honest_reviews.backend.app.secondary_functions.browser_manager import BrowserManager


class YandexReviewsParser:
    def __init__(self, config, proxy: Optional[str] = None):
        self.config = config
        self.proxy = proxy
        self.browser_manager = BrowserManager(config)
        self.retry_count = 3
        self.page_load_timeout = 30
        self.browser_warning_count = 0
        self.max_browser_warnings = 2

    def parse_reviews(self, org_id: str) -> bool:
        """Улучшенный метод парсинга с обработкой предупреждений"""
        if not self.proxy:
            logger.error("Не указан прокси-сервер")
            return False

        for attempt in range(1, self.retry_count + 1):
            driver = None
            try:
                logger.info(f"Попытка {attempt}/{self.retry_count}")
                driver = self._init_driver_with_retry()
                if not driver:
                    continue

                if not self._load_page_safely(driver, org_id):
                    continue

                if not self._process_reviews_page(driver):
                    continue

                self._save_debug_data(driver)
                return True

            except Exception as e:
                logger.error(f"Ошибка при парсинге: {str(e)[:200]}")
            finally:
                if driver:
                    driver.quit()

        logger.error(f"Не удалось получить данные после {self.retry_count} попыток")
        return False

    def _init_driver_with_retry(self) -> Optional[Chrome]:
        """Инициализация драйвера с дополнительными попытками"""
        for _ in range(2):  # Дополнительные попытки для инициализации
            driver = self.browser_manager.init_driver(self.proxy)
            if driver:
                driver.set_page_load_timeout(self.page_load_timeout)
                return driver
            time.sleep(random.uniform(2, 5))
        return None

    def _load_page_safely(self, driver: Chrome, org_id: str) -> bool:
        """Безопасная загрузка страницы с обработкой предупреждений"""
        url = self._prepare_url(org_id)

        try:
            driver.get(url)
            time.sleep(random.uniform(2, 4))  # Имитация чтения

            if self._check_browser_warning(driver):
                self.browser_warning_count += 1
                if self.browser_warning_count >= self.max_browser_warnings:
                    logger.warning("Превышено максимальное количество предупреждений о браузере")
                    return False

                logger.warning("Обнаружено предупреждение, пробуем обходные методы...")
                return self._handle_browser_warning(driver, url)

            return True
        except Exception as e:
            logger.error(f"Ошибка загрузки страницы: {e}")
            return False

    def _prepare_url(self, org_id: str) -> str:
        """Подготовка URL с параметрами для обхода защиты"""
        base_url = self.config.yandex_reviews_url.format(org_id=org_id)
        if "?" in base_url:
            return f"{base_url}&no-tests=1&disable-browser-check=1"
        return f"{base_url}?no-tests=1&disable-browser-check=1"

    def _check_browser_warning(self, driver: Chrome) -> bool:
        """Проверка на страницу с предупреждением о браузере"""
        warning_phrases = [
            "У вас старая версия браузера",
            "попробуйте другой браузер",
            "browser-update",
            "устаревший браузер"
        ]
        page_source = driver.page_source.lower()
        return any(phrase in page_source for phrase in warning_phrases)

    def _handle_browser_warning(self, driver: Chrome, url: str) -> bool:
        """Методы обхода предупреждения о браузере"""
        methods = [
            lambda: driver.refresh(),
            lambda: driver.delete_all_cookies(),
            lambda: driver.execute_script("window.location.href = arguments[0]", url),
            lambda: driver.get(f"{url}&rand={random.randint(10000, 99999)}")
        ]

        for method in methods:
            try:
                method()
                time.sleep(random.uniform(3, 6))
                if not self._check_browser_warning(driver):
                    return True
            except Exception as e:
                logger.warning(f"Ошибка при обработке предупреждения: {e}")

        return False

    def _process_reviews_page(self, driver: Chrome) -> bool:
        """Обработка страницы с отзывами"""
        # Имитация человеческого поведения перед проверкой
        HumanInteraction.simulate_random_interaction(driver)

        if not self._wait_for_reviews_block(driver):
            return False

        # Основное взаимодействие с отзывами
        HumanInteraction.simulate_reading(driver, max_reviews=5)
        HumanInteraction.smart_scroll(driver)

        # Дополнительные случайные действия
        if random.random() > 0.3:
            HumanInteraction.simulate_random_interaction(driver)

        return True

    def _wait_for_reviews_block(self, driver: Chrome, timeout: int = 25) -> bool:
        """Ожидание появления блока отзывов"""
        try:
            WebDriverWait(driver, timeout).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "div.business-reviews-card-view"))
            )
            return True
        except Exception as e:
            logger.warning(f"Блок отзывов не найден: {e}")
            return False

    def _save_debug_data(self, driver: Chrome):
        """Сохранение отладочной информации"""
        try:
            debug_file = getattr(self.config, 'debug_html', 'debug_page.html')
            with open(debug_file, 'w', encoding='utf-8') as f:
                f.write(driver.page_source)
            logger.debug(f"Сохранен HTML для парсинга: {debug_file}")

            # Дополнительно сохраняем скриншот
            if hasattr(self.config, 'debug_screenshot'):
                driver.save_screenshot(self.config.debug_screenshot)
        except Exception as e:
            logger.warning(f"Ошибка сохранения отладочных данных: {e}")