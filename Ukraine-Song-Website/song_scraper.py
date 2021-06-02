from selenium import webdriver
import json
import bs4
from bs4 import BeautifulSoup
import os
import requests
from time import sleep

# I could check if the intended item is on a line, and if it is I can split at the ':' and collec the information there
def findNextLine(item, array):
    for i, array_item in enumerate(array):
        if array_item == item:
            return array[i + 1]
    
    return None

class Scraper:
    def __init__(self):
        self.driver = webdriver.Chrome()
            
        self.song_urls = []
        self.images = []
        
        self.artist_index = {'avtorski': 'АВТОРСЬКІ ПІСНІ', 'plastovi': 'ПЛАСТОВІ ПІСНІ', 'povstanski': 'ПОВСТАНСЬКІ ПІСНІ', 'kosacki': 'КОЗАЦЬКІ ПІСНІ', 
                             'lemkivski': 'ЛЕМКІВСЬКІ ПІСНІ', 'narodni': 'НАРОДНІ ПІСНІ', 'novacki': 'НОВАЦЬКІ ПІСНІ', 'koladky': 'КОЛЯДКИ / ЩЕДРІВКИ', 
                             'molytvy': 'ГІМНИ / МОЛИТВИ '}
        
        self.domain = 'https://pryvatri.de'
        
        self.driver.get(self.domain)
        src = self.driver.page_source
        
        soup = BeautifulSoup(src, features='html')
        self.tabs = [self.domain + a['href'] for a in soup.find('main', {'id': 'content'}).find_all('a')]
        
        self.json = []
        
    def exit(self):
        self.driver.close()
        
    def collect_urls(self):
        for url in self.tabs:
            self.driver.get(url)
            sleep(1.5)
            
            src = self.driver.page_source
            soup = BeautifulSoup(src, features='html')
            table = soup.find('tbody')
            a_tags = table.find_all('a')
            
            song_urls = [self.domain + a['href'] for a in a_tags]
            for song_url in song_urls:
                if song_url not in self.song_urls:
                    self.song_urls.append(song_url)
    
    def scrape_songs(self):
        for song_url in self.song_urls:
            try:
                self.driver.get(song_url)
                sleep(1.5)

                src = self.driver.page_source
                soup = BeautifulSoup(src, features='html')

        #         Content
                try:
                    div = soup.find('div', {'id': 'akordy'})
                    
                    for br in div.find_all('br'):
                        br.replace_with('\n')
                    
                    div.find('h2').replace_with('')
                    
                    content = div.text.replace('\xa0', ' ')
                        
                except Exception as e:
                    content = None
                
        #         Song title
                try:
                    song_title = soup.find('h2', {'itemprop': 'headline'}).text.strip()
                except:
                    song_title = None

        #         Artist
                try:
                    modlist = soup.find('ul', {'class': 'nav menu nav-pills mod-list'})
                    lis = modlist.find_all('li')
                    for li in lis:
                        if 'active' in li['class']:
                            artist = li.find('a')['href'].split('/')[-1]
                            artist = self.artist_index[artist]
                            break
                except:
                    artist = None
            
            
                try:
                    div = soup.find('div', {'id': 'info'})
                    
                    for br in div.find_all('br'):
                        br.replace_with('\n')
                    
                    div.find('h2').replace_with('')
                    
                    info_lines = [line.strip() for line in div.text.replace('\xa0', ' ').split('\n')]
                    
                except:
                    info_lines = None

                #         Artist second
                try:
                    artist_second = findNextLine('Виконання:', info_lines)
                except:
                    artist_second = None
                    
                #         Lyrics author
                try:
                    lyrics_author = findNextLine('Слова:', info_lines)
                except:
                    lyrics_author = None
                    
                #         Music composer
                try:
                    music_composer = findNextLine('Музика:', info_lines)
                except:
                    music_composer = None

                    
        #         Youtube
                try:
                    youtube = [frame['src'].split('/')[-1] for frame in soup.find('div', {'id': 'video'}).find_all('iframe')]
                except:
                    youtube = None

        #         Graphics
                try:
                    img_name = soup.find('div', {'id': 'noty'}).find('img')['src']
                    img_url = self.domain + img_name
                    tup = (img_name.split('/')[-1], img_url)
                    self.images.append(tup)
                except:
                    img_name = None
                    img_url = None

                json_obj = {'content': content, 'song_title': song_title, 'artist': artist, 'youtube': youtube, 'source': song_url, 
                            'graphics': img_name, 'graphics_source_url': img_url, 'artist_second': artist_second, 'lyrics_author': lyrics_author, 'music_composer': music_composer}
                self.json.append(json_obj)
        
            except:
                print(f"Failed for song: '{song_url}'")
            
    def save(self):
        with open('data.json', 'w', encoding='utf-8') as f:
            json.dump(self.json, f, ensure_ascii=False)
            
        for img_name, img_url in self.images:
            try:
                response = requests.get(img_url, headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.190 Safari/537.36'})
                with open(os.path.join(os.getcwd(), 'images', img_name), 'wb') as f:
                    f.write(response.content)
            except:
                pass

if __name__ == "__main__":
    # Scrape data to json file
    x = Scraper()
    x.collect_urls()
    x.scrape_songs()
    x.save()
    x.exit()

    # Verify scraper worked
    js = json.load(open('data.json', 'rb'))

    print(js[0].keys())

    total = []
    for item in js:
        good = item['content']
        if (good != None) and (len(good) != 0):
            total.append(good)
            print(good[:150])

    print(f"Total: {len(x.json)} | Available: {len(total)}")
