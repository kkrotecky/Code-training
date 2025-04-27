import requests
from bs4 import BeautifulSoup
import csv

def scrape(url):
    r = requests.get(
        url="https://www.scrapethissite.com/pages/simple/",
    )

soup = BeautifulSoup(r.content, 'html.parser')


