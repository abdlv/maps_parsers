import json
import pyautogui
from bs4 import BeautifulSoup
import requests_html
from selenium.webdriver.common.by import By
import time
from datetime import datetime
import undetected_chromedriver
import random

class YandexMapsParser:
    def __init__(self):
        self.session = requests_html.HTMLSession()
        self.url = "https://yandex.ru/maps/org/165/163061835171/reviews"
        self.authors_list = []
        self.reviews_list = []

    @staticmethod
    def page_scroll(driver, max_reviews):
        pyautogui.scroll(-10, x=100, y=200)
        while True:
            pyautogui.scroll(-70)
            time.sleep(random.uniform(1, 2))
            reviews_containers = driver.find_elements(By.CLASS_NAME, 'business-reviews-card-view__review')
            if len(reviews_containers) == max_reviews:
                break

    @staticmethod
    def create_driver():
        driver = undetected_chromedriver.Chrome(version_main=105)
        driver.maximize_window()
        return driver

    def get_json(self):
        response = self.session.get(self.url)
        html = response.text

        start = html.find('reviewResults')
        end = html.find(',"reviewPollData')
        str_json = html[start + 12:end][3:]
        info = json.loads(str_json)

        return info

    def unpacking_json(self, info):
        reviews = info['reviews']
        for review in reviews:
            author_info = review['author']
            author_id = author_info['publicId']
            author_name = author_info['name']
            author_url = author_info['profileUrl']
            author_ava = author_info['avatarUrl']
            self.authors_list.append((author_id, author_name, author_url, author_ava))

            print('------------------------------------')
            print('[id автора]: ', author_id)
            print('[Имя автора]: ', author_name)
            print('[Ссылка на профиль]: ', author_url)
            print('[Ссылка на аву]: ', author_ava)
            print()

            review_id = review['reviewId']
            review_text = review['text']
            review_rating = review['rating']
            review_date = review['updatedTime']
            review_likes = review['reactions']['likes']
            review_dislikes = review['reactions']['dislikes']
            self.reviews_list.append((review_id, review_text, review_rating, review_date, review_likes, review_dislikes))

            print('[id отзыва]: ', review_id)
            print('[Текст отзыва]: ', review_text)
            print('[Оценка]: ', review_rating)
            print('[Дата публикации]: ', review_date)
            print('[Лайки]: ', review_likes)
            print('[Дизлайки]: ', review_dislikes)
            print('------------------------------------')
            print()

    def unpacking_html(self, data_containers: list):
        for data_container in data_containers:
            author_info = data_container.find('div', {'class': 'business-review-view__author-row'})
            author_name = author_info.find('span', {'itemprop': 'name'}).text
            author_url = author_info.find('a', {'class': 'business-review-view__user-icon'})['href']
            try:
                author_ava = author_info.find('div', {'class': 'user-icon-view__icon'})['style']
            except KeyError:
                author_ava = 'Нет авы'
            author_id = author_url.split('/')[-1]
            self.authors_list.append((author_id, author_name, author_url, author_ava))

            print('------------------------------------')
            print('[id автора]: ', author_id)
            print('[Имя автора]: ', author_name)
            print('[Ссылка на профиль]: ', author_url)
            print('[Ссылка на аву]: ', author_ava)
            print()

            review_id = 0
            review_text = data_container.find('div', {'class': 'business-review-view__body'}).find('span', {'class': 'business-review-view__body-text'}).text
            review_rating = data_container.find('div', {'class': 'business-review-view__header'}).find('div', {'class': 'business-review-view__rating'}).find('meta', {'itemprop': 'ratingValue'})['content']
            review_date = datetime.strptime(data_container.find('div', {'class': 'business-review-view__header'}).find('span', {'class': 'business-review-view__date'}).find('meta')['content'].split('.')[0].replace('T', ' '), "%Y-%m-%d %H:%M:%S")
            review_reactions = data_container.find_all('div', {'class': 'business-reactions-view__container'})
            try:
                review_likes = review_reactions[0].find('div', {'class': 'business-reactions-view__counter'}).text
            except AttributeError:
                review_likes = 0
            try:
                review_dislikes = review_reactions[1].find('div', {'class': 'business-reactions-view__counter'}).text
            except AttributeError:
                review_dislikes = 0
            self.reviews_list.append(
                (review_id, review_text, review_rating, review_date, review_likes, review_dislikes))

            print('[id отзыва]: ', review_id)
            print('[Текст отзыва]: ', review_text)
            print('[Оценка]: ', review_rating)
            print('[Дата публикации]: ', review_date)
            print('[Лайки]: ', review_likes)
            print('[Дизлайки]: ', review_dislikes)
            print('------------------------------------')
            print()

    def runner(self):
        info = self.get_json()
        about_reviews = info['params']
        reviews_count = about_reviews['count']
        loaded_reviews = about_reviews['loadedReviewsCount']
        page_count = about_reviews['totalPages']

        print('------------------------------------')
        print('[Кол-во отзывов]: ', reviews_count)
        print('[Спаршено отзывов]: ', loaded_reviews)
        print('[Кол-во страниц]: ', page_count)
        print('------------------------------------')
        print()

        if reviews_count <= 50:
            self.unpacking_json(info)
        else:
            driver = self.create_driver()
            driver.get(self.url)
            time.sleep(3)
            scroll_place = driver.find_element(By.XPATH, "//div[@class='business-card-view__section']")
            print(scroll_place)

            self.page_scroll(driver=driver, max_reviews=reviews_count)
            time.sleep(3)
            page = driver.page_source

            driver.close()
            driver.quit()

            soup = BeautifulSoup(page, 'html.parser')
            data_containers = soup.find_all('div', {'class': 'business-reviews-card-view__review'})
            print(len(data_containers))
            print()
            self.unpacking_html(data_containers)

a = YandexMapsParser()
a.runner()
