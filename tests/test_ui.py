
import pytest
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import allure
from allure_commons.types import AttachmentType

#Фикстура для инициализации и закрытия драйвера.
@pytest.fixture(scope="module")
def driver():
    driver = webdriver.Chrome() # Или webdriver.Firefox(), webdriver.Edge()
    driver.maximize_window()
    yield driver
    driver.quit()

@allure.feature("Поиск на Кинопоиске") #Основная фича тестов

#Все тесты оборачиваем в функцию
@allure.story("Поиск по названию")
def test_search_by_title(driver):
    with allure.step("Перейти на главную страницу"):
        driver.get("https://www.kinopoisk.ru/")
    movie_title = "Интерстеллар"

    with allure.step(f"Ввести название фильма '{movie_title}' в поисковую строку"):
        search_input = driver.find_element(By.NAME, "kp_query")
        search_input.send_keys(movie_title)
        search_input.send_keys(Keys.RETURN)

    with allure.step(f"Проверить, что результат содержит фильм '{movie_title}'"):
        try:
            WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.PARTIAL_LINK_TEXT, movie_title))
            )
            result_link = driver.find_element(By.PARTIAL_LINK_TEXT, movie_title)
            assert movie_title in result_link.text
        except Exception as e:
            allure.attach(driver.get_screenshot_as_png(), name="screenshot", attachment_type=AttachmentType.PNG)
            raise

@allure.story("Поиск по жанру")
def test_search_by_genre(driver):
    with allure.step("Перейти на страницу списков фильмов"):
        driver.get("https://www.kinopoisk.ru/lists/movies/")
    genre = "фантастика"
    year = "2014"

    with allure.step("Выбрать жанр 'Фантастика' и год '2014' в фильтрах"):
        try:
            advanced_search_link = driver.find_element(By.XPATH, "//a[contains(text(), 'Расширенный поиск')]")
            advanced_search_link.click()

            year_input = driver.find_element(By.NAME, "year")
            year_input.send_keys(year)

            genre_checkbox = driver.find_element(By.XPATH, f"//label[contains(text(), '{genre}')]/input[@type='checkbox']")
            genre_checkbox.click()

            search_button = driver.find_element(By.XPATH, "//input[@value='search']")
            search_button.click()

            WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.XPATH, f"//a[contains(text(), '{genre}')]"))
            )
            genre_element = driver.find_element(By.XPATH, f"//a[contains(text(), '{genre}')]")
            assert genre in genre_element.text
        except Exception as e:
            allure.attach(driver.get_screenshot_as_png(), name="screenshot", attachment_type=AttachmentType.PNG)
            raise
@allure.story("Поиск по году")
def test_search_by_year(driver):
     with allure.step("Перейти на страницу списков фильмов"):
         driver.get("https://www.kinopoisk.ru/lists/movies/")
     year = "2014"
     with allure.step("Выбрать год в фильтрах"):
         try:
            advanced_search_link = driver.find_element(By.XPATH, "//a[contains(text(), 'Расширенный поиск')]")
            advanced_search_link.click()
            year_input = driver.find_element(By.NAME, "year")
            year_input.send_keys(year)
            search_button = driver.find_element(By.XPATH, "//input[@value='search']")
            search_button.click()
            WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.XPATH, f"//div[contains(text(), '{year}')]"))
            )
            genre_element = driver.find_element(By.XPATH, f"//div[contains(text(), '{year}')]")
            assert year in genre_element.text
         except Exception as e:
             allure.attach(driver.get_screenshot_as_png(), name="screenshot", attachment_type=AttachmentType.PNG)
             raise
@allure.story("Поиск по нескольким критериям")
def test_search_by_multiple_criteria(driver):
   with allure.step("Перейти на страницу списков фильмов"):
       driver.get("https://www.kinopoisk.ru/lists/movies/")
   genre = "фантастика"
   year = "2014"

   with allure.step("Выбрать жанр 'Фантастика' и год '2014' в фильтрах"):
       try:
           advanced_search_link = driver.find_element(By.XPATH, "//a[contains(text(), 'Расширенный поиск')]")
           advanced_search_link.click()

           year_input = driver.find_element(By.NAME, "year")
           year_input.send_keys(year)

           genre_checkbox = driver.find_element(By.XPATH, f"//label[contains(text(), '{genre}')]/input[@type='checkbox']")
           genre_checkbox.click()

           search_button = driver.find_element(By.XPATH, "//input[@value='search']")
           search_button.click()

           WebDriverWait(driver, 10).until(
               EC.presence_of_element_located((By.XPATH, f"//a[contains(text(), '{genre}')]"))
           )
           genre_element = driver.find_element(By.XPATH, f"//a[contains(text(), '{genre}')]")
           assert genre in genre_element.text
       except Exception as e:
           allure.attach(driver.get_screenshot_as_png(), name="screenshot", attachment_type=AttachmentType.PNG)
           raise

@allure.story("Поиск по невалидным данным в названии")
def test_search_by_invalid_title(driver):
    with allure.step("Перейти на главную страницу"):
        driver.get("https://www.kinopoisk.ru/")
    invalid_title = "asdfghjklqwertyuiop"

    with allure.step(f"Ввести невалидное название '{invalid_title}' в поисковую строку"):
        search_input = driver.find_element(By.NAME, "kp_query")
        search_input.send_keys(invalid_title)
        search_input.send_keys(Keys.RETURN)

    with allure.step("Проверить, что отображается сообщение об отсутствии результатов"):
        try:
            WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.XPATH, "//p[contains(text(), 'К сожалению, по вашему запросу ничего не найдено')]"))
            )
            error_message = driver.find_element(By.XPATH, "//p[contains(text(), 'К сожалению, по вашему запросу ничего не найдено')]")
            assert "К сожалению, по вашему запросу ничего не найдено" in error_message.text
        except Exception as e:
            allure.attach(driver.get_screenshot_as_png(), name="screenshot", attachment_type=AttachmentType.PNG)
            raise
@allure.story("Поиск по невалидным данным в названии и году")
def test_search_by_invalid_title_and_year(driver):
  with allure.step("Перейти на страницу списков фильмов"):
      driver.get("https://www.kinopoisk.ru/lists/movies/")
  invalid_title = "asdfghjklqwertyuiop"
  year = "3000" #Невалидный год

  with allure.step(f"Ввести невалидное название '{invalid_title}' и год '{year}' в фильтры"):
      try:
          advanced_search_link = driver.find_element(By.XPATH, "//a[contains(text(), 'Расширенный поиск')]")
          advanced_search_link.click()
          year_input = driver.find_element(By.NAME, "year")
          year_input.send_keys(year)
          search_input = driver.find_element(By.NAME, "kp_query") #Вводим название фильма в поле поиска
          search_input.send_keys(invalid_title)
          search_button = driver.find_element(By.XPATH, "//input[@value='search']")
          search_button.click()

          WebDriverWait(driver, 10).until(
              EC.presence_of_element_located((By.XPATH, "//p[contains(text(), 'К сожалению, по вашему запросу ничего не найдено')]"))
          )
          error_message = driver.find_element(By.XPATH, "//p[contains(text(), 'К сожалению, по вашему запросу ничего не найдено')]")
          assert "К сожалению, по вашему запросу ничего не найдено" in error_message.text

      except Exception as e:
          allure.attach(driver.get_screenshot_as_png(), name="screenshot", attachment_type=AttachmentType.PNG)
          raise
