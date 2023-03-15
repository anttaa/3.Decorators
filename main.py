import os
from datetime import datetime
import requests
import json
from bs4 import BeautifulSoup
from fake_headers import Headers


def logger(old_function):

    def new_function(*args, **kwargs):
        answer = old_function(*args, **kwargs)
        # print(old_function.__name__, answer)
        with open('main.log', 'a') as f:
            f.write(f'{datetime.now().strftime("%d.%m.%Y %H:%M:%S")} {old_function.__name__}({args}, {kwargs}) = {answer}\n')
        return answer
    return new_function


def test_1():
    path = 'main.log'
    if os.path.exists(path):
        os.remove(path)

    @logger
    def hello_world():
        return 'Hello World'

    @logger
    def summator(a, b=0):
        return a + b

    @logger
    def div(a, b):
        return a / b

    assert 'Hello World' == hello_world(), "Функция возвращает 'Hello World'"
    result = summator(2, 2)
    assert isinstance(result, int), 'Должно вернуться целое число'
    assert result == 4, '2 + 2 = 4'
    result = div(6, 2)
    assert result == 3, '6 / 2 = 3'
    assert os.path.exists(path), 'файл main.log должен существовать'

    summator(4.3, b=2.2)
    summator(a=0, b=0)

    with open(path) as log_file:
        log_file_content = log_file.read()

    assert 'summator' in log_file_content, 'должно записаться имя функции'
    for item in (4.3, 2.2, 6.5):
        assert str(item) in log_file_content, f'{item} должен быть записан в файл'


def logger_p(path):

    def __logger(old_function):
        def new_function(*args, **kwargs):
            answer = old_function(*args, **kwargs)
            nonlocal path
            with open(path, 'a') as f:
                f.write(
                    f'{datetime.now().strftime("%d.%m.%Y %H:%M:%S")} {old_function.__name__}({args}, {kwargs}) = {answer}\n')
            return answer
        return new_function
    return __logger


def test_2():
    paths = ('log_1.log', 'log_2.log', 'log_3.log')

    for path in paths:
        if os.path.exists(path):
            os.remove(path)

        @logger_p(path)
        def hello_world():
            return 'Hello World'

        @logger_p(path)
        def summator(a, b=0):
            return a + b

        @logger_p(path)
        def div(a, b):
            return a / b

        assert 'Hello World' == hello_world(), "Функция возвращает 'Hello World'"
        result = summator(2, 2)
        assert isinstance(result, int), 'Должно вернуться целое число'
        assert result == 4, '2 + 2 = 4'
        result = div(6, 2)
        assert result == 3, '6 / 2 = 3'
        summator(4.3, b=2.2)

    for path in paths:
        assert os.path.exists(path), f'файл {path} должен существовать'
        with open(path) as log_file:
            log_file_content = log_file.read()
        assert 'summator' in log_file_content, 'должно записаться имя функции'
        for item in (4.3, 2.2, 6.5):
            assert str(item) in log_file_content, f'{item} должен быть записан в файл'


def test_3():
    HOST = "https://hh.ru/search/vacancy"
    VACANCY = f"{HOST}?text=python&area=1&area=2"

    def get_headers():
        return Headers(browser="firefox", os="win").generate()

    def get_text(url):
        return requests.get(url, headers=get_headers()).text

    @logger
    def main():
        result = {"vacancies": []}
        html = get_text(f"{VACANCY}")
        soup = BeautifulSoup(html, features="html5lib")
        vacancies = soup.find_all(class_="serp-item")  # .find_all("article")
        for item in vacancies:
            a = item.find(class_='serp-item__title')
            title = a.text
            price = item.find(class_='bloko-header-section-3').text
            if 'django' in title.lower() and 'flask' in title.lower() and 'usd' in price.lower():
                result['vacancies'].append({
                    "link": a['href'],
                    "price": price,
                    "company": item.find(class_='bloko-link bloko-link_kind-tertiary').text,
                    "town": item.find(attrs={'data-qa': 'vacancy-serp__vacancy-address'}).text
                })
        return result

    result = main()
    with open('json_data.json', 'w') as f:
        json.dump(result, f)


if __name__ == '__main__':
    test_1()
    test_2()
    test_3()
