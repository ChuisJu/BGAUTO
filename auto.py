import requests
import os
import urllib.parse
from bs4 import BeautifulSoup
from dotenv import load_dotenv
import json
import math

load_dotenv()

class GlobalExam:
    def __init__(self):
        self.__session = requests.Session()

    def __getMinimalHeaders(self):
        return {
            "User-Agent": 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/117.0.5938.63 Safari/537.36',
            "Referer": "https://global-exam.com/",
        }


    def login(self):
        res = self.__session.get('https://auth.global-exam.com/login',headers=self.__getMinimalHeaders())
        assert res.status_code == 200
        soup = BeautifulSoup(res.content, 'html.parser')

        input = soup.find('input',{'name':'_token'})
        if input:
            _token = input.get('value',False)
            res = self.__session.post(
                "https://auth.global-exam.com/login",
                headers=self.__getMinimalHeaders() | {
                    "Content-Type": "application/x-www-form-urlencoded",
                },
                data=urllib.parse.urlencode({
                    "_token": _token,
                    "email": os.getenv('EMAIL'),
                    "password": os.getenv('PASSWORD'),
                    "timezone": "Europe/Paris"
                }),
                allow_redirects=False
            )
            return res.headers.get('Location', None) == "https://business.global-exam.com"
        return False


    def getAllArticles(self):
        res = self.__session.get("https://business.global-exam.com/api/article/paginate") 
        data = json.loads(res.content)
        meta = data.get("meta",{})
        total = meta.get("total",0)
        size = meta.get("per_page",0)

        ids = []
        for x in range(1,math.ceil(total / size)+1):
            res = self.__session.get("https://business.global-exam.com/api/article/paginate?page="+str(x)) 
            ids.extend(map(lambda x: x.get('id', None),json.loads(res.content).get("data",[])))

        return ids

    def completeArticle(self, id: int):
        res = self.__session.post(
            "https://business.global-exam.com/api/article/user-activity/create",
            json={"article_id": id},
            headers=self.__getMinimalHeaders() | {
                "Content-Type": "application/json",
            },
        )
        print(res.status_code)

    def autoComplete(self):
        if self.login():
            ids = self.getAllArticles()
            for id in ids[:os.getenv('MAX_READ')]:
                self.completeArticle(id)
        else:
            print('Identifiants invalides')


def main():
    GlobalExam().autoComplete()

if __name__ == '__main__':
    main()