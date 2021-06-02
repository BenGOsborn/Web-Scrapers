from selenium import webdriver
from bs4 import BeautifulSoup
import time
import pandas as pd

class GeniusBot:
    def __init__(self, url):
        self.driver = webdriver.Chrome()
        self.driver.get(url)
        
    def collect_songs(self, scroll_num):
        self.driver.find_element_by_xpath('/html/body/routable-page/ng-outlet/routable-profile-page/ng-outlet/routed-page/profile-page/div[3]/div[2]/artist-songs-and-albums/div[3]').click()
        self.driver.find_element_by_xpath('/html/body/div[5]/div[1]').click()
        for _ in range(scroll_num):
            self.driver.find_element_by_tag_name('body').send_keys(webdriver.common.keys.Keys.END)
            time.sleep(1.5)
        
        source = self.driver.page_source
        soup = BeautifulSoup(source, features='html')
        
        songs = soup.find_all('transclude-injecting-local-scope', {'class': 'u-display_block'})
        urls = []
        for tag in songs:
            a_tags = tag.find_all('a', href=True)
            for a_tag in a_tags:
                href = a_tag['href']
                if str(href)[-6:] == 'lyrics':
                    urls.append(href)

        self.song_urls = list(set(urls))
        
        print(f"URL's to scrape: {self.song_urls}")
        
    def scrape_song(self, song_url):
        self.driver.get(song_url)
            
        lyrics = []

        soup = BeautifulSoup(self.driver.page_source, features='html')

        title = soup.find('h1', {'class': 'header_with_cover_art-primary_info-title'}).text.strip()

        section_tag = soup.find('section')
        for a_tag in section_tag.find_all('a'):
            lyric = a_tag.get_text(separator='\n')
            lyrics.append(lyric)
            
        lyrics_string = "\n".join(lyrics)
                
        print(f"Title: {title}\nURL:{song_url}\nLyrics: {lyrics_string[:15]}...")
        
        return title, song_url, lyrics_string
        
    def scrape_songs(self):
        self.song_data = []
        
        for song_url in self.song_urls:
            try:
                song_tup = self.scrape_song(song_url)
                self.song_data.append(song_tup)
            except:
                pass
            
        print("Done scraping!")
            
    def to_csv(self, csv_dir):
        titles = [tup[0] for tup in self.song_data]
        urls = [tup[1] for tup in self.song_data]
        lyrics = [tup[2] for tup in self.song_data]
        
        df = pd.DataFrame({'title': titles, 'url': urls, 'lyrics': lyrics})
        df.to_csv(csv_dir)
            
    def close(self):
        self.driver.close()

if __name__ == "__main__":
    bot = GeniusBot('https://genius.com/artists/Eminem')
    bot.collect_songs(100)
    bot.scrape_songs()
    bot.to_csv('./eminem-data.csv')
    bot.close()
