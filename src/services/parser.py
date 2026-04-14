import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, unquote


def parse_files_from_page(url: str):
    """Парсит страницу и возвращает список файлов"""
    file_extensions = ['.pdf', '.doc', '.docx', '.xls', '.xlsx', '.ppt', '.pptx', '.zip', '.rar']

    try:
        response = requests.get(url, timeout=15)
        response.raise_for_status()
        response.encoding = 'utf-8'

        soup = BeautifulSoup(response.text, 'html.parser')
        files = []

        # Ищем все ссылки на странице
        for link in soup.find_all('a', href=True):
            href = link['href'].strip()
            if not href or href.startswith('#') or href.startswith('javascript:'):
                continue

            full_url = urljoin(url, href)
            lower_href = href.lower()

            # Проверяем, является ли ссылка файлом
            if any(lower_href.endswith(ext) for ext in file_extensions):
                # Получаем текст ссылки (название файла)
                file_name = link.get_text(strip=True)
                if not file_name:
                    file_name = full_url.split('/')[-1]
                    file_name = unquote(file_name)

                files.append({
                    "name": file_name,
                    "url": full_url,
                    "type": "file"
                })

        # Удаляем дубликаты по URL
        unique_files = []
        seen_urls = set()
        for f in files:
            if f["url"] not in seen_urls:
                seen_urls.add(f["url"])
                unique_files.append(f)

        return unique_files

    except Exception as e:
        print(f"Ошибка парсинга {url}: {e}")
        return []