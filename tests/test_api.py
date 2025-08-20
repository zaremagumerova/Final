import requests
import allure


base_url_ui = "https://www.kinopoisk.ru/"
base_url_api = "https://api.kinopoisk.dev/v1.4/"
headers = {"X-API-KEY": "VFH6RN7-BZWMJSH-GVDHE7R-5ET1PFQ"}


class TestKinopoiskAPI:
    """Набор тестов для Kinopoisk API."""

    @allure.title("Позитивный: Поиск фильма по жанру и году")
    def test_search_by_genre_and_year(self) -> None:
        """Позитивный: Поиск фильма по ID"""

        with allure.step("Выполнение API запроса"):
            response = requests.get(base_url_api + "movie/1355059", headers=headers)

        with allure.step("Проверка кода статуса ответа"):
            assert response.status_code == 200, f"Код статуса не 200: {response.status_code}, {response.text}"


    @allure.title("Позитивный: Поиск фильма по названию")
    def test_search_by_multiple_genres_and_year(self):
        """Позитивный: Поиск фильма по нескольким жанрам и году."""

        with allure.step("Выполнение API запроса"):
            response = requests.get(base_url_api + "movie/search?page=1&limit=10&query=Форсаж", headers=headers)

        with allure.step("Проверка кода статуса ответа"):
            assert response.status_code == 200, f"Код статуса не 200: {response.status_code}, {response.text}"



    @allure.title("Позитивный: Поиск фильма по одному жанру")
    def test_search_by_single_genre(self) -> None:
        """Позитивный: Поиск фильма по одному жанру."""
        with allure.step("Выполнение API запроса"):
            response = requests.get(base_url_api + "movie?genres.name=боевик&limit=2", headers=headers)

        with allure.step("Проверка кода статуса ответа"):
            assert response.status_code == 200, f"Код статуса не 200: {response.status_code}, {response.text}"



    @allure.title("Позитивный: Поиск фильма по типу")
    def test_search_by_type(self) -> None:
       """Позитивный: Поиск фильма по типу."""

       with allure.step("Выполнение API запроса"):
           response = requests.get(base_url_api + "/movie?type=cartoon&limit=2", headers=headers)

       with allure.step("Проверка кода статуса ответа"):
           assert response.status_code == 200, f"Код статуса не 200: {response.status_code}, {response.text}"


    @allure.title("Негативный: Поиск фильма с невалидным жанром")
    def test_search_with_invalid_genre(self) -> None:
        """Негативный: Поиск фильма с невалидным жанром."""

        with allure.step("Выполнение API запроса"):
            response = requests.get(base_url_api + "/movie?genres.name=invalid", headers=headers)

        with allure.step("Проверка кода статуса ответа"):
            assert response.status_code == 200, f"Код статуса не 200: {response.status_code}, {response.text}"
