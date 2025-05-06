from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait, Select
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from bs4 import BeautifulSoup
from fake_useragent import UserAgent
from loguru import logger
import time
import random
import os
import sys
import re

PROXY_URL = "https://spys.one/free-proxy-list/RU/"
OUTPUT_FILE = "proxies.txt"
CHROMEDRIVER_PATH = r"C:\Users\wangr\.wdm\drivers\chromedriver\chromedriver-win64\chromedriver-win64\chromedriver.exe"  # укажи абсолютный путь, если не рядом

logger.add("logs/proxy_scraper.log", rotation="1 MB", level="DEBUG")

def init_driver():
    try:
        if not os.path.isfile(CHROMEDRIVER_PATH):
            logger.error(f"Chromedriver не найден по пути: {CHROMEDRIVER_PATH}")
            sys.exit("❌ Укажи путь к chromedriver в переменной CHROMEDRIVER_PATH или установи в PATH")

        ua = UserAgent()
        options = Options()
        options.add_argument(f"user-agent={ua.random}")
        # options.add_argument("--headless=new")
        options.add_argument("--disable-blink-features=AutomationControlled")
        options.add_argument("--disable-extensions")
        options.add_argument("--start-maximized")
        options.add_argument("--disable-infobars")

        service = Service(executable_path=CHROMEDRIVER_PATH)
        driver = webdriver.Chrome(service=service, options=options)
        return driver

    except Exception as e:
        logger.exception(f"Ошибка при инициализации драйвера: {e}")
        raise

def parse_proxies_from_file(file_path):
    try:
        # Чтение сохранённого HTML-файла
        with open(file_path, "r", encoding="utf-8") as file:
            html = file.read()

        soup = BeautifulSoup(html, "html.parser")

        # Логируем HTML на случай, если прокси не найдены
        logger.debug("HTML content of the page:\n" + html[:500])  # Логируем только первые 500 символов для упрощения

        # Находим все строки с классом 'spy1xx'
        rows = soup.find_all("tr", class_="spy1xx")

        proxies = []
        for row in rows:
            cols = row.find_all("td")
            if cols:
                # Извлекаем HTML-контент из первого столбца
                ip_port_raw = cols[0].decode_contents()

                # Извлекаем IP и порт
                ip_port = extract_ip_port(ip_port_raw)
                if ip_port:
                    proxies.append(ip_port)

        return proxies
    except Exception as e:
        logger.exception(f"Ошибка при парсинге HTML из файла: {e}")
        return []


def extract_ip_port(raw_html):
    try:
        # Убираем все теги <script>
        soup = BeautifulSoup(raw_html, "html.parser")
        for tag in soup.find_all("script"):
            tag.decompose()
        cleaned = soup.text.strip()

        # Используем регулярное выражение для извлечения IP:PORT
        match = re.search(r"(\d+\.\d+\.\d+\.\d+):(\d+)", cleaned)
        if match:
            return f"{match.group(1)}:{match.group(2)}"
        else:
            return None
    except Exception as e:
        logger.warning(f"Ошибка извлечения IP:PORT: {e}")
        return None

def save_proxies(proxies):
    try:
        with open(OUTPUT_FILE, "w") as f:
            for proxy in proxies:
                f.write(proxy + "\n")
        logger.success(f"✅ Прокси сохранены в файл {OUTPUT_FILE}")
    except Exception as e:
        logger.error(f"Ошибка при сохранении прокси в файл: {e}")

def fetch_proxies():
    try:
        driver = init_driver()
        logger.info(f"Открываю {PROXY_URL}")
        driver.get(PROXY_URL)

        # Ждём появления селектора количества прокси
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.ID, "xpp"))
        )
        select = Select(driver.find_element(By.ID, "xpp"))
        select.select_by_value("5")  # "5" соответствует выбору 500 прокси

        logger.info("Выбрано отображение 500 прокси, жду обновления страницы...")
        time.sleep(random.uniform(10, 15))  # Увеличенное ожидание для полной подгрузки 500 прокси


        # Сохраняем HTML после выбора 500 прокси
        with open("debug.html", "w", encoding="utf-8") as f:
            f.write(driver.page_source)

        driver.quit()
        logger.info("HTML сохранён. Начинаю парсинг...")

        # Парсим HTML из файла
        proxies = parse_proxies_from_file("debug.html")

        if proxies:
            save_proxies(proxies)
            logger.success(f"✅ Найдено и сохранено {len(proxies)} прокси")
        else:
            logger.warning("❌ Прокси не найдены!")

    except Exception as e:
        logger.exception(f"❌ Ошибка при сборе прокси: {e}")

if __name__ == "__main__":
    fetch_proxies()
