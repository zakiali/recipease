import requests
from bs4 import BeautifulSoup
import re

HEADERS = {
#     'User-Agent': 'Mozilla/5.0 (Windows; U; Windows NT 5.1; en-US; rv:1.9.0.7) Gecko/2009021910 Firefox/3.0.7'
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_13_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/68.0.3440.106 Safari/537.36'
}

# set some cookies to maneuver over:
# - EU Consent in allrecipes.com.br
COOKIES = {
    'euConsentFailed': 'true',
    'euConsentID': 'e48da782-e1d1-0931-8796-d75863cdfa15',
}

class SimplyRecipeScraper(object):
    '''Get ingredients/comments from a single recipe'''

    def __init__(self, url):
        self.url = url
        self.soup = BeautifulSoup(requests.get(self.url, headers=HEADERS, cookies=COOKIES).content, "html.parser")
        self.get_ingredients()
        self.get_instructions()
        self.get_reviews()
        self.get_image_url()
        self.get_title()
        
    def get_ingredients(self):
        self.ingredient_list = [str(li) for li in self.soup.find_all('li', class_='ingredient')]
        
    def get_instructions(self):
        self.instructions = []
        _inst = self.soup.find_all('div', {'id': "sr-recipe-method"})[0].find_all('p')
        for k in _inst:
            if k.find_next().name != 'img':
                self.instructions.append(str(k))
    
    def get_reviews(self):
        comment_url = self.url + '/comments'
        comment_soup = BeautifulSoup(requests.get(comment_url, headers=HEADERS, cookies=COOKIES).content, "html.parser")
        comments_html = comment_soup.find_all('div', {"class":["comment-content", "comment-text"]})
        self.comments = [com.text for com in comments_html]

    def get_image_url(self):
        self.image_url = self.soup.find_all('meta', class_='image')[0]['content']

    def get_title(self):
        title = self.soup.title.text.strip().split('|')[0]
        self.title =  re.sub(r'\{[^}]*\}', '', title).strip()
