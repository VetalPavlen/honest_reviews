import random
import time
from typing import Optional
from selenium.webdriver import Chrome
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from loguru import logger


class HumanInteraction:
    @staticmethod
    def simulate_random_interaction(driver: Chrome) -> bool:
        """Безопасная имитация случайных действий пользователя"""
        try:
            action = ActionChains(driver)
            viewport_width = driver.execute_script("return window.innerWidth")
            viewport_height = driver.execute_script("return window.innerHeight")

            # 1. Плавное перемещение внутри видимой области
            for _ in range(random.randint(3, 5)):
                x = random.randint(0, viewport_width - 1)
                y = random.randint(0, viewport_height - 1)
                action.move_by_offset(x, y).pause(random.uniform(0.2, 0.5)).perform()
                action.reset_actions()

            # 2. Клик по случайному элементу (если есть)
            clickable_elements = driver.find_elements(By.CSS_SELECTOR, "a, button, [onclick]")
            if clickable_elements and random.random() > 0.5:
                elem = random.choice(clickable_elements)
                try:
                    action.move_to_element(elem).pause(0.5).click().perform()
                    time.sleep(random.uniform(1.0, 2.0))
                except:
                    pass  # Игнорируем ошибки кликов

            # 3. Имитация прокрутки
            if random.random() > 0.3:
                scroll_amount = random.randint(200, 800)
                driver.execute_script(f"window.scrollBy(0, {scroll_amount})")
                time.sleep(random.uniform(0.5, 1.5))

            return True
        except Exception as e:
            logger.debug(f"Ошибка в simulate_random_interaction: {str(e)[:200]}")
            return False

    @staticmethod
    def simulate_reading(driver: Chrome, max_reviews: int = 5) -> bool:
        """Имитация чтения отзывов с безопасными перемещениями"""
        try:
            viewport_height = driver.execute_script("return window.innerHeight")
            action = ActionChains(driver)

            reviews = driver.find_elements(By.CSS_SELECTOR, "div.business-review-view")
            if not reviews:
                return False

            for _ in range(min(max_reviews, len(reviews))):
                review = random.choice(reviews)

                # Плавное перемещение к отзыву
                driver.execute_script("arguments[0].scrollIntoView({behavior: 'smooth', block: 'center'})", review)
                time.sleep(random.uniform(0.5, 1.5))

                # Наведение и пауза
                try:
                    action.move_to_element(review).pause(random.uniform(2.0, 4.0)).perform()
                    action.reset_actions()
                except:
                    pass

                # Случайное раскрытие отзыва
                if random.random() > 0.7:
                    try:
                        expand_btn = review.find_element(By.CSS_SELECTOR, "button[aria-expanded='false']")
                        expand_btn.click()
                        time.sleep(random.uniform(1.0, 2.0))
                    except:
                        pass

            return True
        except Exception as e:
            logger.debug(f"Ошибка в simulate_reading: {str(e)[:200]}")
            return False

    @staticmethod
    def smart_scroll(driver: Chrome) -> bool:
        """Безопасная прокрутка страницы"""
        try:
            scroll_height = driver.execute_script("return document.body.scrollHeight")
            window_height = driver.execute_script("return window.innerHeight")

            if scroll_height <= window_height:
                return False

            # Плавная прокрутка с паузами
            for step in range(1, random.randint(3, 5)):
                scroll_to = min(scroll_height, step * window_height // 2)
                driver.execute_script(f"window.scrollTo(0, {scroll_to})")
                time.sleep(random.uniform(0.8, 1.8))

                # Иногда прокручиваем немного назад
                if random.random() > 0.7:
                    driver.execute_script(f"window.scrollBy(0, -{random.randint(50, 150)})")
                    time.sleep(random.uniform(0.5, 1.0))

            # Финишная прокрутка
            driver.execute_script("window.scrollTo(0, document.body.scrollHeight)")
            time.sleep(random.uniform(1.0, 2.0))

            return True
        except Exception as e:
            logger.debug(f"Ошибка в smart_scroll: {str(e)[:200]}")
            return False