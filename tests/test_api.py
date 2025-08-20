
import pytest
import requests
import json
import allure
from typing import Dict, Any, List, Optional


# API_TOKEN = "YOUR_API_KEY"

@allure.step("Загрузка Postman коллекции из JSON файла: {collection_file}")
def get_collection_data(collection_file: str) -> Dict[str, Any]:
    """
    Загружает Postman коллекцию из JSON файла.

    Аргументы:
        collection_file: Путь к JSON файлу.

    Возвращает:
        Словарь, представляющий Postman коллекцию.
    """
    with open(collection_file, 'r', encoding='utf-8') as f:
        collection_data = json.load(f)
    return collection_data


@pytest.fixture(scope="session")
def collection() -> Dict[str, Any]:
    """Фикстура для загрузки Postman коллекции один раз за сессию."""
    return get_collection_data("kinopoisk_collection.json")  # Путь к сохраненной Postman коллекции в формате JSON


@pytest.fixture
def base_url(collection: Dict[str, Any]) -> Optional[str]:
    """Фикстура для получения базового URL из переменных коллекции."""
    for variable in collection['variable']:
        if variable['key'] == 'base_url':
            return variable['value']
    return None  # Или вызвать исключение, если base_url не найден


@pytest.fixture
def api_token(collection: Dict[str, Any]) -> Optional[str]:
    """Фикстура для получения API токена из переменных коллекции."""
    for variable in collection['variable']:
        if variable['key'] == 'api_token':
            return variable['value']
    return None  # Или вызвать исключение, если api_token не найден


@allure.step("Выполнение API запроса к {endpoint} методом {method} с параметрами {params}")
def make_request(base_url: str, endpoint: str, method: str = "GET", params: Optional[Dict[str, Any]] = None,
                 headers: Optional[Dict[str, str]] = None, api_token: Optional[str] = None) -> requests.Response:
    """
    Вспомогательная функция для выполнения API запросов.

    Аргументы:
        base_url: Базовый URL API.
        endpoint: Эндпоинт API для вызова.
        method: HTTP метод для использования (GET или POST). По умолчанию GET.
        params: Словарь параметров запроса. По умолчанию None.
        headers: Словарь HTTP заголовков. По умолчанию None.
        api_token: API токен для аутентификации. По умолчанию None.

    Возвращает:
        Объект requests.Response.
    """
    if headers is None:
        headers = {}

    if api_token:
        headers["X-API-KEY"] = api_token  # API ключ в заголовке

    url = f"{base_url}{endpoint}"
    if method == "GET":
        response = requests.get(url, params=params, headers=headers)
    elif method == "POST":
        response = requests.post(url, params=params, headers=headers)  # Добавлено для POST
    else:
        raise ValueError(f"Неподдерживаемый метод: {method}")

    return response


class TestKinopoiskAPI:
    """Набор тестов для Kinopoisk API."""

    @allure.title("Позитивный: Поиск фильма по жанру и году")
    def test_search_by_genre_and_year(self, base_url: str, api_token: str, collection: Dict[str, Any]) -> None:
        """Позитивный: Поиск фильма по жанру и году."""
        item = next((item for item in collection['item'][0]['item'] if item['name'] == "Поиск фильма по жанру и году"), None)
        assert item is not None, "Тест-кейс 'Поиск фильма по жанру и году' не найден"

        request_data = item['request']
        endpoint = request_data['url']['path'][0] + "/" + request_data['url']['path'][1]
        params = {q['key']: q['value'] for q in request_data['url']['query']}

        with allure.step("Выполнение API запроса"):
            response = make_request(base_url, endpoint, params=params, api_token=api_token)

        with allure.step("Проверка кода статуса ответа"):
            assert response.status_code == 200, f"Код статуса не 200: {response.status_code}, {response.text}"

        with allure.step("Обработка данных ответа"):
            data = response.json()
            assert 'docs' in data and isinstance(data['docs'], list) and len(data['docs']) > 0, "Фильмы не найдены"

        with allure.step("Проверка данных фильма"):
            for movie in data['docs']:
                assert movie['year'] == int(params['year']), "Неверный год"
                genres = [genre['name'].lower() for genre in movie['genres']]
                assert params['genres.name'].lower() in genres, "Неверный жанр"

    @allure.title("Позитивный: Поиск фильма по нескольким жанрам и году")
    def test_search_by_multiple_genres_and_year(self, base_url: str, api_token: str, collection: Dict[str, Any]) -> None:
        """Позитивный: Поиск фильма по нескольким жанрам и году."""
        item = next((item for item in collection['item'][0]['item'] if item['name'] == "Поиск фильма по нескольким жанрам и году"), None)
        assert item is not None, "Тест-кейс 'Поиск фильма по нескольким жанрам и году' не найден"

        request_data = item['request']
        endpoint = request_data['url']['path'][0] + "/" + request_data['url']['path'][1]
        params = {q['key']: q['value'].replace("%2B", "") for q in request_data['url']['query']}  # Удаление %2B (кодировка знака плюс)

        with allure.step("Выполнение API запроса"):
            response = make_request(base_url, endpoint, params=params, api_token=api_token)

        with allure.step("Проверка кода статуса ответа"):
            assert response.status_code == 200, f"Код статуса не 200: {response.status_code}, {response.text}"

        with allure.step("Обработка данных ответа"):
            data = response.json()
            assert 'docs' in data and isinstance(data['docs'], list) and len(data['docs']) > 0, "Фильмы не найдены"

        expected_genres = [q['value'].replace("%2B", "").lower() for q in request_data['url']['query'] if q['key'] == 'genres.name']

        with allure.step("Проверка данных фильма"):
            for movie in data['docs']:
                assert movie['year'] == int(params['year']), "Неверный год"

                movie_genres = [genre['name'].lower() for genre in movie['genres']]
                for expected_genre in expected_genres:
                    assert expected_genre in movie_genres, f"Жанр '{expected_genre}' не найден в жанрах фильма."

    @allure.title("Позитивный: Поиск фильма по одному жанру")
    def test_search_by_single_genre(self, base_url: str, api_token: str, collection: Dict[str, Any]) -> None:
        """Позитивный: Поиск фильма по одному жанру."""
        item = next((item for item in collection['item'][0]['item'] if item['name'] == "Поиск фильма только по одному жанру"), None)
        assert item is not None, "Тест-кейс 'Поиск фильма только по одному жанру' не найден"

        request_data = item['request']
        endpoint = request_data['url']['path'][0] + "/" + request_data['url']['path'][1]
        params = {q['key']: q['value'] for q in request_data['url']['query']}

        with allure.step("Выполнение API запроса"):
            response = make_request(base_url, endpoint, params=params, api_token=api_token)

        with allure.step("Проверка кода статуса ответа"):
            assert response.status_code == 200, f"Код статуса не 200: {response.status_code}, {response.text}"

        with allure.step("Обработка данных ответа"):
            data = response.json()
            assert 'docs' in data and isinstance(data['docs'], list) and len(data['docs']) > 0, "Фильмы не найдены"

        with allure.step("Проверка данных фильма"):
            for movie in data['docs']:
                genres = [genre['name'].lower() for genre in movie['genres']]
                assert params['genres.name'].lower() in genres, "Неверный жанр"

    @allure.title("Позитивный: Поиск фильма по типу")
    def test_search_by_type(self, base_url: str, api_token: str, collection: Dict[str, Any]) -> None:
        """Позитивный: Поиск фильма по типу."""
        item = next((item for item in collection['item'][0]['item'] if item['name'] == "Поиск по типу"), None)
        assert item is not None, "Тест-кейс 'Поиск по типу' не найден"

        request_data = item['request']
        endpoint = request_data['url']['path'][0] + "/" + request_data['url']['path'][1]
        params = {q['key']: q['value'] for q in request_data['url']['query']}

        with allure.step("Выполнение API запроса"):
            response = make_request(base_url, endpoint, params=params, api_token=api_token)

        with allure.step("Проверка кода статуса ответа"):
            assert response.status_code == 200, f"Код статуса не 200: {response.status_code}, {response.text}"

        with allure.step("Обработка данных ответа"):
            data = response.json()
            assert 'docs' in data and isinstance(data['docs'], list) and len(data['docs']) > 0, "Фильмы не найдены"

        with allure.step("Проверка данных фильма"):
            for movie in data['docs']:
                assert movie['type'].lower() == params['type'].lower(), "Неверный тип"

    @allure.title("Негативный: Поиск фильма с невалидным жанром")
    def test_search_with_invalid_genre(self, base_url: str, api_token: str, collection: Dict[str, Any]) -> None:
        """Негативный: Поиск фильма с невалидным жанром."""
        item = next((item for item in collection['item'][1]['item'] if item['name'] == "Поиск фильма с невалидным жанром"), None)
        assert item is not None, "Тест-кейс 'Поиск фильма с невалидным жанром' не найден"

        request_data = item['request']
        endpoint = request_data['url']['path'][0] + "/" + request_data['url']['path'][1]
        params = {q['key']: q['value'] for q in request_data['url']['query']}

        with allure.step("Выполнение API запроса"):
            response = make_request(base_url, endpoint, params=params, api_token=api_token)

        with allure.step("Проверка кода статуса ответа"):
            assert response.status_code == 200, f"Код статуса не 200: {response.status_code}, {response.text}"

        with allure.step("Обработка данных ответа"):
            data = response.json()
            assert 'docs' in data and isinstance(data['docs'], list), "Docs не является массивом"
            assert len(data['docs']) == 0, "Найдены фильмы с невалидным жанром"
            assert data['total'] == 0, "Total не равен 0"
            assert data['pages'] == 0, "Pages не равен 0"
            assert data['limit'] == 10, "Limit не равен 10"
            assert data['page'] == 1, "Page не равен 1"

    @allure.title("Негативный: Поиск фильма с невалидным годом")
    def test_search_with_invalid_year(self, base_url: str, api_token: str, collection: Dict[str, Any]) -> None:
        """Негативный: Поиск фильма с невалидным годом."""
        item = next((item for item in collection['item'][1]['item'] if item['name'] == "Поиск фильма с невалидным годом"), None)
        assert item is not None, "Тест-кейс 'Поиск фильма с невалидным годом' не найден"

        request_data = item['request']
        endpoint = request_data['url']['path'][0] + "/" + request_data['url']['path'][1]
        params = {q['key']: q['value'] for q in request_data['url']['query']}

        with allure.step("Выполнение API запроса"):
            response = make_request(base_url, endpoint, params=params, api_token=api_token)

        with allure.step("Проверка кода статуса ответа"):
            assert response.status_code == 400, f"Код статуса не 400: {response.status_code}, {response.text}"

        with allure.step("Обработка данных ответа"):
            data = response.json()
            assert 'message' in data and isinstance(data['message'], list), "Message не является списком"
            assert "Значение поля year должно быть в диапазоне от 1874 до 2050!" in data['message'][0], "Неверное сообщение об ошибке"
            assert data['error'] == "Bad Request", "Неверный тип ошибки"
            assert data['statusCode'] == 400, "Неверный код статуса в теле ответа"

    @allure.title("Негативный: Поиск фильма с годом из будущего в пределах диапазона")
    def test_search_with_future_year_in_range(self, base_url: str, api_token: str, collection: Dict[str, Any]) -> None:
        """Негативный: Поиск фильма с годом из будущего в пределах диапазона."""
        item = next((item for item in collection['item'][1]['item'] if item['name'] == "Поиск фильма с годом из будущего в пределах диапазона"), None)
        assert item is not None, "Тест-кейс 'Поиск фильма с годом из будущего в пределах диапазона' не найден"

        request_data = item['request']
        endpoint = request_data['url']['path'][0] + "/" + request_data['url']['path'][1]
        params = {q['key']: q['value'] for q in request_data['url']['query']}

        with allure.step("Выполнение API запроса"):
            response = make_request(base_url, endpoint, params=params, api_token=api_token)

        with allure.step("Проверка кода статуса ответа"):
            assert response.status_code == 200, f"Код статуса не 200: {response.status_code}, {response.text}"

        with allure.step("Обработка данных ответа"):
            data = response.json()
            assert 'docs' in data and isinstance(data['docs'], list), "Docs не является массивом"
            assert len(data['docs']) == 0, "Найдены фильмы с годом из будущего"
            assert data['total'] == 0, "Total не равен 0"
            assert data['pages'] == 0, "Pages не равен 0"
            assert data['limit'] == 10, "Limit не равен 10"
            assert data['page'] == 1, "Page не равен 1"

    @allure.title("Негативный: Поиск фильма с пустым запросом")
    def test_search_with_empty_query(self, base_url: str, api_token: str, collection: Dict[str, Any]) -> None:
        """Негативный: Поиск фильма с пустым запросом."""
        item = next((item for item in collection['item'][1]['item'] if item['name'] == "Поиск фильма с пустым запросом"), None)
        assert item is not None, "Тест-кейс 'Поиск фильма с пустым запросом' не найден"

        request_data = item['request']
        endpoint = request_data['url']['path'][0] + "/" + request_data['url']['path'][1] + "/" + request_data['url']['path'][2]
        params = {q['key']: q['value'] for q in request_data['url']['query']}

        with allure.step("Выполнение API запроса"):
            response = make_request(base_url, endpoint, params=params, api_token=api_token)

        with allure.step("Проверка кода статуса ответа"):
            assert response.status_code == 200, f"Код статуса не 200: {response.status_code}, {response.text}"

        with allure.step("Обработка данных ответа"):
            data = response.json()
            assert 'docs' in data and isinstance(data['docs'], list), "Docs не является массивом"
            assert len(data['docs']) > 0, "Не найдены фильмы с пустым запросом"
            assert data['total'] > 0, "Total не больше 0"
            assert data['limit'] > 0, "Limit не больше 0"
            assert data['page'] == 1, "Page не равен 1"
            assert data['pages'] > 0, "Pages не больше 0"
            assert len(data['docs']) <= data['limit'], "Количество docs превышает limit"

    @allure.title("Негативный: Поиск фильма с пустым жанром")
    def test_search_with_empty_genre(self, base_url: str, api_token: str, collection: Dict[str, Any]) -> None:
        """Негативный: Поиск фильма с пустым жанром."""
        item = next((item for item in collection['item'][1]['item'] if item['name'] == "Поиск фильма с пустым жанром"), None)
        assert item is not None, "Тест-кейс 'Поиск фильма с пустым жанром' не найден"

        request_data = item['request']
        endpoint = request_data['url']['path'][0] + "/" + request_data['url']['path'][1]
        params = {q['key']: q['value'] for q in request_data['url']['query']}

        with allure.step("Выполнение API запроса"):
            response = make_request(base_url, endpoint, params=params, api_token=api_token)

        with allure.step("Проверка кода статуса ответа"):
            assert response.status_code == 200, f"Код статуса не 200: {response.status_code}, {response.text}"

        with allure.step("Обработка данных ответа"):
            data = response.json()
            assert 'docs' in data and isinstance(data['docs'], list), "Docs не является массивом"
            assert len(data['docs']) == 0, "Найдены фильмы с пустым жанром"
            assert data['total'] == 0, "Total не равен 0"
            assert data['pages'] == 0, "Pages не равен 0"
            assert data['limit'] == 10, "Limit не равен 10"
            assert data['page'] == 1, "Page не равен 1"

    @allure.title("Негативный: Поиск фильма с неподдерживаемым методом POST")
    def test_search_with_post_method(self, base_url: str, api_token: str, collection: Dict[str, Any]) -> None:
        """Негативный: Поиск фильма с неподдерживаемым методом POST."""
        item = next((item for item in collection['item'][1]['item'] if item['name'] == "Поиск фильма с не поддерживаемым методом POST"), None)
        assert item is not None, "Тест-кейс 'Поиск фильма с не поддерживаемым методом POST' не найден"

        request_data = item['request']
        endpoint = request_data['url']['path'][0] + "/" + request_data['url']['path'][1] + "/" + request_data['url']['path'][2]
        params = {q['key']: q['value'] for q in request_data['url']['query'] if q['value'] is not None}  # Обработка нулевых значений в запросе
        # Удаляем пустые параметры

        with allure.step("Выполнение API запроса"):
            response = make_request(base_url, endpoint, method="POST", params=params, api_token=api_token)

        with allure.step("Проверка кода статуса ответа"):
            assert response.status_code == 404, f"Код статуса не 404: {response.status_code}, {response.text}"

        with allure.step("Обработка данных ответа"):
            data = response.json()
            assert 'message' in data, "Отсутствует сообщение"
            assert "Cannot POST" in data['message'], "Неверное сообщение об ошибке"
            assert data['error'] == "Not Found", "Неверный тип ошибки"
            assert data['statusCode'] == 404, "Неверный код статуса в теле ответа"
