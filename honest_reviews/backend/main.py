from honest_reviews.backend.app.scrapping.yandex_reviews_parser import YandexReviewsParser
from honest_reviews.backend.app.secondary_functions.proxy_manager import ProxyManager
from loguru import logger

from honest_reviews.backend.config.config_loader import ConfigLoader

if __name__ == "__main__":
    logger.add("logs/review_scraper.log", rotation="1 MB", level="DEBUG")
    try:
        config = ConfigLoader.load_config("config.ini")
        proxy_manager = ProxyManager(config)
        proxy = proxy_manager.get_random_proxy()
        if proxy:
            logger.info(f"Используется прокси: {proxy}")
            parser = YandexReviewsParser(config, proxy)
            org_id = "170837487282"
            if parser.parse_reviews(org_id):
                logger.info("Парсинг завершен успешно")
            else:
                logger.error("Не удалось получить данные")
        else:
            logger.warning("Не удалось получить рабочий прокси. Останавливаем программу.")
    except Exception as e:
        logger.error(f"Критическая ошибка: {e}")
