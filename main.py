import functools
import os.path
from datetime import datetime
import requests
import bs4


def logger(func):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        current_time = datetime.now()
        result = func(*args, **kwargs)
        with open('simple_log.txt', 'a', encoding='utf-8') as file:
            file.write(current_time.strftime('%d.%m.%Y %H:%M:%S\n'))
            file.write(f'Вызов функции {func.__name__}() с аргументами: {args}, {kwargs}\n')
            file.write(f'Возвращаемое значение: {repr(result)}\n')
        return result
    return wrapper


def path_logger(path=''):
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            current_time = datetime.now()
            result = func(*args, **kwargs)
            with open(os.path.join(path, 'path_log.txt'), 'a', encoding='utf-8') as file:
                file.write(current_time.strftime('%d.%m.%Y %H:%M:%S\n'))
                file.write(f'Вызов функции {func.__name__}() с аргументами: {args}, {kwargs}\n')
                file.write(f'Возвращаемое значение: {repr(result)}\n')
            return result
        return wrapper
    return decorator


# Взял код моей домашней работы по скрапингу и добавил декораторы к функциям
@logger
def get_title(article):
    article_tag_span = article.find('h2').find('a').find('span')
    return article_tag_span.text


@logger
def get_time(article):
    article_tag = article.find('span', class_='tm-article-snippet__datetime-published')
    article_tag_time = article_tag.find('time')
    str_time = article_tag_time.attrs['title']
    return datetime.strptime(str_time, '%Y-%m-%d, %H:%M')


@path_logger('D:\Фильмы\Особые')
def get_url(article):
    article_tag_a = article.find('h2').find('a')
    href = article_tag_a.attrs['href']
    return 'https://habr.com' + href


@path_logger()
def filter_article(words, url):
    article_response = requests.get(url)
    article_code = article_response.text
    article_soap = bs4.BeautifulSoup(article_code, features='html.parser')
    article_tag = article_soap.find('div', class_='tm-article-body')
    for word in words:
        if word in article_tag.text:
            return True
    return False


if __name__ == '__main__':
    KEYWORDS = ['фото']

    response = requests.get('https://habr.com/ru/all/')
    text = response.text

    soap = bs4.BeautifulSoup(text, features='html.parser')
    articles = soap.find_all('article', class_='tm-articles-list__item')

    for article in articles:
        title = get_title(article)
        time = get_time(article)
        url = get_url(article)
        if filter_article(KEYWORDS, url):
            print(time.strftime('%d.%m.%Y'), '////', title, '////' , url)
