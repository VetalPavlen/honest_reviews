from bs4 import BeautifulSoup
from loguru import logger
import re
import json


def parse_org_info(html_path: str):
    logger.info(f"Начинаем парсинг файла: {html_path}")

    try:
        with open(html_path, "r", encoding="utf-8") as f:
            soup = BeautifulSoup(f, "html.parser")
    except Exception as e:
        logger.error(f"Ошибка при чтении HTML файла: {e}")
        return

    try:
        # Получаем данные из meta-тегов
        title_tag = soup.find("meta", property="og:title")
        description_tag = soup.find("meta", property="og:description")

        title_raw = title_tag["content"] if title_tag else ""
        description_raw = description_tag["content"] if description_tag else ""

        # Удаляем "Отзывы о "
        title_clean = re.sub(r"^Отзывы о\s+", "", title_raw)

        # Извлекаем название и адрес
        name_match = re.search(r"«(.+?)»", title_clean)
        address_match = re.search(r"» на (.+?)(?: —|$)", title_clean)

        org_name = name_match.group(1) if name_match else "Не найдено"
        address = address_match.group(1) if address_match else "Не найдено"

        # Чистим описание
        description_clean = re.sub(r"Напишите свой отзыв.*", "", description_raw).strip()

        # Обрезаем первую часть описания
        short_desc_pattern = rf"«{re.escape(org_name)}»[^.]+"  # шаблон для краткого описания
        short_description_match = re.search(short_desc_pattern, description_clean)

        short_description = short_description_match.group(0) if short_description_match else ""
        short_description = re.split(r",\s*Москва|,\s*г\.\s*Москва", short_description)[0].strip()

        # Извлекаем номер телефона
        phone = "Не указан"
        phone_tag = soup.find("script", string=re.compile(r'"phones":\['))  # Ищем script с телефонами

        if phone_tag:
            try:
                json_data = phone_tag.string
                # Извлекаем и парсим JSON
                phone_data_match = re.search(r'"phones":(\[.*?\])', json_data)
                if phone_data_match:
                    phones_json = phone_data_match.group(1)
                    phones = json.loads(phones_json)  # Преобразуем строку в объект
                    if phones and isinstance(phones, list):
                        phone = phones[0].get("number", "Не указан")  # Извлекаем первый номер телефона
            except json.JSONDecodeError:
                logger.warning("Ошибка при парсинге JSON с телефонами.")

        # Рейтинг, оценки, отзывы
        rating_match = re.search(r"Рейтинг\s([\d,\.]+)", description_clean)
        rating = rating_match.group(1).replace(",", ".") if rating_match else "?"

        votes_match = re.search(r"на основе\s(\d+)\sоцен", description_clean)
        votes = votes_match.group(1) if votes_match else "?"

        reviews_match = re.search(r"и\s(\d+)\sотзыв", description_clean)
        reviews = reviews_match.group(1) if reviews_match else "?"

        # Что нравится
        likes_match = re.search(r"Посетителям нравятся\s(.+?)\.", description_clean)
        likes = likes_match.group(1).strip() if likes_match else "Не указано"

        # Выводим информацию
        logger.info("Парсинг завершён успешно")
        print("Название организации:")
        print(org_name)

        print("\nАдрес:")
        print(address)

        print("\nТелефон:")
        print(phone)

        print("\nОписание:")
        print(short_description)

        print(f"\nРейтинг: {rating}")
        print(f"Оценок: {votes}")
        print(f"Отзывов: {reviews}")

        print("\nЧто нравится:")
        print(likes)

    except Exception as e:
        logger.exception(f"Ошибка при парсинге HTML: {e}")


if __name__ == "__main__":
    parse_org_info(r"C:\Users\wangr\PycharmProjects\pythonProject64\debug_yandex.html")
