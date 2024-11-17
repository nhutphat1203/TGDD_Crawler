
import requests
from bs4 import BeautifulSoup
from time import sleep
from Common import REAL_PATH, PREFIX_PRODUCT_URL, SLEEP_TIME, SAVE_DIR, PRODUCT_INFO_NEED
from os import makedirs
import json
from playwright.sync_api import sync_playwright


class TGDD_Crawler:
    
    def __init__(self):

        self.headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3'
                } 
        self.ignore = ['javascript:;']
    
    @staticmethod
    def run_playwright(playwright, url):
        browser = playwright.chromium.launch(headless=True)
        page = browser.new_page()
        page.goto(url)
        content = page.content()
        browser.close()
        return content
    
    @staticmethod
    def getHtmlPlayWright(url):
        with sync_playwright() as playwright:
            html = TGDD_Crawler.run_playwright(playwright, url)
            return html

    def _getSoup(self, url):
                
        try:
            response = requests.get(url, headers=self.headers)
            response.raise_for_status()
        except Exception as e:
            print(e)
            return None
        soup = BeautifulSoup(response.content, 'html.parser')
        return soup

    def _crawlLinkProduct(self, url):
        soup = BeautifulSoup(TGDD_Crawler.getHtmlPlayWright(url),'html.parser')
        return [item.get('href') for  item in (soup.find('div', class_='container-productbox').find('ul', class_='listproduct').find_all('a')) if item.get('href') not in self.ignore][0: PRODUCT_INFO_NEED]
    
    def _crawlProductInfo(self, url):
        res = {}
        soup = self._getSoup(url)
        boxs = soup.find_all('div', class_='box-specifi')
        for box in boxs:
            title = box.find_next('a').get_text();
            container = {}
            ul = box.find_next('ul', class_="text-specifi")
            lis = ul.find_all('li')
            for li in lis:
                asides = li.find_all('aside')
                sub_title = asides[0].find_next('strong').get_text();
                list = []
                for content in asides[1]:
                    if content == '\n':
                        continue
                    list.append(content.get_text())
                container[sub_title] = list
            res[title] = container
        return res

    def _crawlProductsInfo(self, url):
        res = {}
        urls = self._crawlLinkProduct(url)
        n = len(urls)
        for idx, url in enumerate(urls):
            url = PREFIX_PRODUCT_URL + url
            res[url] = self._crawlProductInfo(url)
            percent = (idx + 1) / n * 100
            print("Đã hoàn thành:", str(percent)+"%")
            sleep(SLEEP_TIME)
            print(n)
        return res
        
    def _saveData(self, data):
        makedirs(SAVE_DIR, exist_ok=True)
        file = SAVE_DIR + "//data.json"
        with open (file, 'w') as f:
            json.dump(data, f, ensure_ascii=False, indent=4)
    def run(self) -> None:
        self._saveData(self._crawlProductsInfo(REAL_PATH))

