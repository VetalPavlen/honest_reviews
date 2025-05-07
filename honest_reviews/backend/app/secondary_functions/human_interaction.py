import random
import time
from selenium.webdriver import Chrome
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.by import By
from loguru import logger
import re

class HumanInteraction:
    @staticmethod
    def simulate_random_interaction(driver: Chrome) -> bool:
        """Безопасная имитация случайных действий пользователя"""
        try:
            action = ActionChains(driver)
            viewport_width = driver.execute_script("return window.innerWidth")
            viewport_height = driver.execute_script("return window.innerHeight")

            for _ in range(random.randint(3, 5)):
                x = random.randint(100, viewport_width - 100)
                y = random.randint(100, viewport_height - 100)
                driver.execute_script(f"window.scrollBy(0, {random.randint(50, 150)});")  # добавим реализма
                action.move_by_offset(0, 0).move_by_offset(x - viewport_width // 2, y - viewport_height // 2)
                action.reset_actions()

            clickable_elements = driver.find_elements(By.CSS_SELECTOR, "button, [onclick]:not(a)")
            if clickable_elements and random.random() > 0.5:
                elem = random.choice(clickable_elements)
                try:
                    action.move_to_element(elem).pause(0.5).click().perform()
                    time.sleep(random.uniform(1.0, 2.0))
                except:
                    pass

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
            action = ActionChains(driver)
            reviews = driver.find_elements(By.CSS_SELECTOR, "div.business-review-view")
            if not reviews:
                return False

            for _ in range(min(max_reviews, len(reviews))):
                review = random.choice(reviews)
                driver.execute_script("arguments[0].scrollIntoView({behavior: 'smooth', block: 'center'})", review)
                time.sleep(random.uniform(0.5, 1.5))

                try:
                    action.move_to_element(review).pause(random.uniform(2.0, 4.0)).perform()
                    action.reset_actions()
                except:
                    pass

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
    def get_total_reviews_count(driver: Chrome) -> int:
        """Получает общее количество отзывов из meta-тега og:description"""
        try:
            meta = driver.find_element(By.CSS_SELECTOR, 'meta[property="og:description"]')
            content = meta.get_attribute("content")
            match = re.search(r"(\d+)\s+отзыва", content.replace('\xa0', ' '))
            if match:
                return int(match.group(1))
        except Exception as e:
            logger.warning(f"Не удалось получить количество отзывов из meta: {e}")
        return 0

    @staticmethod
    def load_all_reviews(driver: Chrome) -> bool:
        try:
            from selenium.webdriver.common.action_chains import ActionChains

            def random_mouse_move():
                try:
                    action = ActionChains(driver)
                    width = driver.execute_script("return window.innerWidth")
                    height = driver.execute_script("return window.innerHeight")
                    x = random.randint(100, width - 100)
                    y = random.randint(100, height - 100)
                    action.move_by_offset(0, 0).move_by_offset(x - width // 2, y - height // 2).perform()
                    action.reset_actions()
                except Exception as e:
                    logger.debug(f"Ошибка при перемещении мышки: {e}")

            def set_sorting_by_novelty():
                try:
                    logger.debug("Выбираем сортировку по новизне...")
                    # Нажимаем на заголовок отзывов, чтобы раскрыть список
                    title_button = driver.find_element(By.CSS_SELECTOR, "div.card-section-header._wide")
                    title_button.click()
                    time.sleep(random.uniform(0.5, 1.0))

                    # Нажимаем на "По умолчанию"
                    sorting_button = driver.find_element(By.CSS_SELECTOR, "div.rating-ranking-view")
                    sorting_button.click()
                    time.sleep(random.uniform(0.5, 1.0))

                    # Выбираем "По новизне"
                    novelty_option = driver.find_element(By.XPATH,
                                                         '//div[contains(@class, "rating-ranking-view__popup-line") and text()="По новизне"]')
                    novelty_option.click()
                    logger.debug("Сортировка по новизне выбрана.")
                    time.sleep(random.uniform(1.0, 2.0))
                except Exception as e:
                    logger.warning(f"Не удалось выбрать сортировку: {e}")

            set_sorting_by_novelty()
            time.sleep(random.uniform(0.3, 0.8))  # Пауза после выбора сортировки

            target_count = HumanInteraction.get_total_reviews_count(driver)
            logger.info(f"Ожидаем загрузку {target_count} отзывов...")

            review_container = driver.find_element(By.CSS_SELECTOR, '[class*="scroll__container"]')

            last_count = 0
            no_growth_cycles = 0
            rescue_attempts = 0
            min_required = int(target_count * 0.5)

            # Резкий скачок вниз
            driver.execute_script("arguments[0].scrollTop += arguments[1]", review_container, random.randint(800, 1500))
            random_mouse_move()
            time.sleep(random.uniform(1.0, 2.0))

            while True:
                block_length = random.choice([6, 8, 10, 12, 15])
                for _ in range(block_length):
                    driver.execute_script(
                        "arguments[0].scrollTop += arguments[1]",
                        review_container,
                        random.randint(80, 180)
                    )
                    time.sleep(random.uniform(0.1, 0.3))

                if random.random() < 0.8:
                    random_mouse_move()

                if random.random() < 0.4:
                    time.sleep(random.uniform(2.0, 5.0))

                reviews = driver.find_elements(By.CSS_SELECTOR, "div.business-review-view")
                current_count = len(reviews)
                logger.debug(f"Найдено отзывов — {current_count} / {target_count}")

                if current_count >= target_count:
                    logger.info(f"Все отзывы загружены: {current_count}")
                    break

                if current_count == last_count:
                    no_growth_cycles += 1
                    logger.debug(f"Цикл {no_growth_cycles} без прироста отзывов")

                    if current_count >= min_required:
                        # Попытка «разбудить» подгрузку
                        if rescue_attempts < 3:
                            rescue_attempts += 1
                            logger.debug("Подгрузка остановилась. Пытаемся разбудить:")
                            driver.execute_script("arguments[0].scrollTop -= arguments[1]", review_container,
                                                  random.randint(200, 400))
                            random_mouse_move()
                            time.sleep(random.uniform(3.0, 5.0))
                            continue
                        else:
                            logger.warning(
                                f"После {rescue_attempts} попыток подгрузка не возобновилась. Останавливаемся.")
                            break
                else:
                    no_growth_cycles = 0
                    rescue_attempts = 0
                    last_count = current_count

            return last_count >= min_required
        except Exception as e:
            logger.error(f"Ошибка в load_all_reviews: {str(e)[:200]}")
            return False

    @staticmethod
    def smart_scroll(driver: Chrome) -> bool:
        """Устаревшая простая прокрутка страницы — оставлена для совместимости"""
        logger.warning("smart_scroll устарел. Используйте load_all_reviews для полноценной подгрузки отзывов.")
        return HumanInteraction.load_all_reviews(driver)
