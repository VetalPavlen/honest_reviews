# Имитация пользовательского поведения
from selenium import webdriver  # ← вот этого не хватает
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.by import By
import random
import time


class HumanInteraction:
    @staticmethod
    def simulate(driver: webdriver.Chrome) -> bool:
        try:
            driver.maximize_window()
            time.sleep(random.uniform(0.5, 1.5))

            action = ActionChains(driver)
            body = driver.find_element(By.TAG_NAME, 'body')

            action.move_to_element_with_offset(body, 100, 100).perform()
            time.sleep(random.uniform(0.3, 0.7))

            for _ in range(random.randint(2, 4)):
                x_offset = random.randint(-200, 200)
                y_offset = random.randint(-200, 200)
                action.move_by_offset(x_offset, y_offset).perform()
                time.sleep(random.uniform(0.2, 0.5))

            if random.random() > 0.5:
                action.click().perform()
                time.sleep(random.uniform(0.5, 1.2))

            return True
        except Exception as e:
            return False

    @staticmethod
    def smart_scroll(driver: webdriver.Chrome) -> bool:
        try:
            for i in range(1, 4):
                scroll_height = driver.execute_script("return document.body.scrollHeight")
                scroll_point = scroll_height * (i / 4)
                driver.execute_script(f"window.scrollTo(0, {scroll_point})")
                time.sleep(random.uniform(1.0, 2.0))

            driver.execute_script("window.scrollTo(0, document.body.scrollHeight)")
            time.sleep(random.uniform(1.5, 2.5))

            return True
        except Exception as e:
            return False
