from selenium import webdriver
from selenium.webdriver.firefox.service import Service as FirefoxService
from webdriver_manager.firefox import GeckoDriverManager
from selenium.webdriver.firefox.options import Options as FirefoxOptions
from selenium import webdriver
from selenium.webdriver.common.by import By
import json
import pandas as pd
from sqlalchemy import create_engine

class Meta_Scraper:
    def __init__(self):
        '''
        Create the Metacritic ps4 games scrapping class.
        '''
        options = FirefoxOptions()
        options.add_argument("--headless")
        self.driver = webdriver.Firefox(service=FirefoxService(GeckoDriverManager().install()), options=options)
        self.score_dict = {}
        self.webpage_string = 'https://www.metacritic.com/browse/games/score/metascore/all/ps4/filtered?page='

    def click_accept(self):
        '''
        click the accept cookie button
        '''
        accept = self.driver.find_element(By.CSS_SELECTOR, 'button[id="onetrust-accept-btn-handler"]')
        accept.click()
    
    def get_all_webpages(self):
        '''
        Get all webpages' url.
        '''
        list = []
        for i in range(0,21):
            list.append(self.webpage_string+str(i))
        return list

    def start(self):
        '''
        start scraping all papes
        '''
        webpages = self.get_all_webpages()
        for webpage in webpages:
            self.scrape_one_page(webpage)
        
        
        
    def scrape_one_page(self, page):
        '''
        scrape the given page
        Args:
            page: the url string to be scraped.
        Returns:
            None
        '''
        self.driver.get(page)
        try:
            self.click_accept()
        except:
            pass
        games = self.driver.find_elements(By.CSS_SELECTOR, 'td[class="clamp-summary-wrap"]')
        for game in games:
            title = game.find_element(By.CSS_SELECTOR, 'a[class="title"]').text
            score = game.find_element(By.CSS_SELECTOR, 'div[class^="metascore_w"]').text
            self.score_dict[title] = int(score)
        return None

    
    def quit(self):
        '''
        Quit the web driver.
        '''
        self.driver.quit()

    def save(self):
        with open('data.json', 'w') as fp:
            json.dump(self.score_dict, fp)
        

def test():
    
    scraper = Meta_Scraper()    
    scraper.get_all_webpages()
    print('starting to scrape.')
    scraper.start()
    scraper.quit()
    df = pd.DataFrame.from_dict(scraper.score_dict,  orient = 'index')
    df.reset_index(inplace = True)
    df.columns  = ['name','meta score']
    print('successful!')
    DATABASE_TYPE = 'postgresql'
    DBAPI = 'psycopg2'
    ENDPOINT = 'database-2.c1smg8vtsvp8.us-east-1.rds.amazonaws.com' # Change it for your AWS endpoint
    USER = 'postgres'
    PASSWORD = '20080555'
    PORT = 5432
    DATABASE = 'postgres'
    engine = create_engine(f"{DATABASE_TYPE}+{DBAPI}://{USER}:{PASSWORD}@{ENDPOINT}:{PORT}/{DATABASE}")
    engine.connect()
    df.to_sql('meta_critics_ps4_data', engine, if_exists='replace')

if __name__ == '__main__':
    test()
