import requests
from bs4 import BeautifulSoup
import pandas as pd

def scrape(url):
    response = requests.get(url)
    if response.status_code != 200:
        print("Failed to retrieve the page")
        return

    soup = BeautifulSoup(response.content, 'html.parser')

    countryies = soup.find_all('h3', class_='country-name')
    for country in countryies:
        country.text.strip()

    capitals = soup.find_all('span', class_='country-capital')
    for capital in capitals:
        capital.text.strip()

    populations = soup.find_all('span', class_='country-population')
    for population in populations:
        population.text.strip()

    areas = soup.find_all('span', class_='country-area')
    for area in areas:
        area.text.strip()

    data = {
        'Country': [country.text.strip() for country in countryies],
        'Capital': [capital.text.strip() for capital in capitals],
        'Population': [population.text.strip() for population in populations],
        'Area': [area.text.strip() for area in areas]
    }
    df = pd.DataFrame(data)
    
    df.to_csv('scrapper/countries.csv', index=False)
    print("Data saved to countries.csv")
    

scrape("https://www.scrapethissite.com/pages/simple/")
