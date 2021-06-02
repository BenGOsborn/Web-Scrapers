import requests
from bs4 import BeautifulSoup
import os
from csv import DictWriter
import time
import pandas as pd
from datetime import datetime as dt
import hashlib
import sqlite3

class Scraper:
    def __init__(self, csv_dir):
        self.__field_names = ['name_english', 'name_japanese', 'show_type', 'episodes', 'status', 'aired', 'broadcast_time', 'producers', 
                       'licensors', 'studios', 'source', 'genres', 'episode_length', 'rating', 'score_and_scorers', 
                       'members', 'favorites', 'description']

        self.__csv_dir = csv_dir
        self.__date = dt.today().strftime(r'%d-%m-%Y')

    def __parseList(self, element):
        ret_list = [a.text for a in element.find_all('a')]
        
        return ", ".join(ret_list)

    def __parseLabel(self, element):
        string = element.text
        
        split_colens = string.split(':')
        removed_label = split_colens[1:]
        
        for i, label in enumerate(removed_label):
            removed_label[i] = label.replace('\n', '').strip()
        
        joined = " ".join(removed_label)
        
        return joined

    def __createRow(self, url):
        ret_dict = {field_name: '' for field_name in self.__field_names}

        req = requests.get(url)
        soup = BeautifulSoup(req.content, 'html.parser')

        side_panel = soup.find('td', class_='borderClass')
        side_panel_subdiv = side_panel.find('div')
        side_panel_divs = side_panel_subdiv.find_all('div')

        try:
            ret_dict['description'] = soup.find('p', itemprop='description').text

        except Exception as e:
            print(f"Encountered an error '{e}' for description at '{url}'.")

        for panel in side_panel_divs:
            try:
                split = str(panel.text.split(':')[0].strip())

                if split == "English":
                    ret_dict['name_english'] = self.__parseLabel(panel)

                if split == "Japanese":
                    ret_dict['name_japanese'] = self.__parseLabel(panel)

                if split == "Type":
                    ret_dict['show_type'] = self.__parseLabel(panel)

                if split == "Episodes":
                    ret_dict['episodes'] = self.__parseLabel(panel)

                if split == "Status":
                    ret_dict['status'] = self.__parseLabel(panel)

                if split == "Aired":
                    ret_dict['aired'] = self.__parseLabel(panel)

                if split == "Broadcast":
                    ret_dict['broadcast_time'] = self.__parseLabel(panel)

                if split == "Producers":
                    ret_dict['producers'] = self.__parseList(panel)

                if split == "Licensors":
                    ret_dict['licensors'] = self.__parseList(panel)

                if split == "Studios":
                    ret_dict['studios'] = self.__parseList(panel)

                if split == "Source":
                    ret_dict['source'] = self.__parseLabel(panel)

                if split == "Genres":
                    ret_dict['genres'] = self.__parseList(panel)

                if split == "Duration":
                    ret_dict['episode_length'] = self.__parseLabel(panel)

                if split == "Rating":
                    ret_dict['rating'] = self.__parseLabel(panel).split(' ')[0]

                if split == "Score":
                    ret_dict['score_and_scorers'] = ", ".join([part.text for part in panel.find_all('span')][1:])

                if split == "Members":
                    ret_dict['members'] = "".join(self.__parseLabel(panel).split(','))

                if split == "Favorites":
                    ret_dict['favorites'] = "".join(self.__parseLabel(panel).split(','))

            except Exception as e:
                print(f"Encountered an error '{e}' at '{url}'.")

        return ret_dict

    def buildCSV(self, end_page, start_page=0):
        link = 'Unknown'
                
        for i in range(start_page, end_page):
            
            print(f"Scraping page {i}...")

            csv_filename = f"anime-{self.__date}-{i}.csv"
            csv_path = os.path.join(self.__csv_dir, csv_filename)

            with open(csv_path, 'w', newline='', encoding='utf-8') as csvfile:
                writer = DictWriter(csvfile, fieldnames=self.__field_names)
                
                writer.writeheader()

                url_page = f"https://myanimelist.net/topanime.php?limit={i*50}"
                req_list = requests.get(url_page)
                soup_list = BeautifulSoup(req_list.content, 'html.parser')
                shows = soup_list.find_all('tr', class_='ranking-list')

                for show in shows:
                    try:
                        link = show.find('a').get('href')
                        data_row = self.__createRow(link)
                        writer.writerow(data_row)

                        time.sleep(2) # These are required to stop the website from blocking us

                    except Exception as e:
                        print(f"Encountered error '{e}' at '{link}'.")
                        
                        time.sleep(2)
        
        print("Dataset creation completed successfully.")

    def __parseRatingCol(self, rating):
        if rating == 'None':
            return 'R+' # We do this because if a show is unlabelled, then only people who can watch any show, being R+ can watch this unclassified rating

    # This will parse our episode length column and return the amount of minutes the show lasted for
    def __parseEpLenCol(self, ep_len_raw):
        try:
            ep_len_split = ep_len_raw.split(' ')

            # This will be the condition if it contains a sec
            if ep_len_split[1] == 'sec.':
                return 1

            # This will be our condition if it contains a min
            elif ep_len_split[1] == 'min.':
                return int(ep_len_split[0])

            # These will be the conditions if it contains an hr
            elif ep_len_split[1] == 'hr.':

                if len(ep_len_split) > 2:

                    if ep_len_split[3] == 'min.':
                        return 60 * int(ep_len_split[0]) + int(ep_len_split[2])

                return 60 * int(ep_len_split[0])

        except:
            return pd.NA

    def __binEpLenCol(self, ep_length):
        try:
            # Categories: <30 | 30 | 60 | 90 | 120 | >120 | 
            if ep_length < 30:
                return '<30'

            elif (ep_length >= 30) and (ep_length < 30 + 15):
                return '30'

            elif (ep_length >= 30 + 15) and (ep_length < 60 + 15):
                return '60'

            elif (ep_length >= 60 + 15) and (ep_length < 90 + 15):
                return '90'
            
            elif (ep_length >= 90 + 15) and (ep_length < 120 + 15):
                return '120'

            elif (ep_length >= 120 + 15):
                return '>120'

        except:
            return pd.NA

    def __parseEpisodesCol(self, episodes):
        try:
            return int(episodes)
        
        except:
            return pd.NA

    def __binEpCountCol(self, count):
        try:
            # <30 | 30 | 60 | 90 | 120 | 150 | 180 | 210 | >210
            if count < 30:
                return '<30'

            elif (count >= 30) and (count < 30 + 15):
                return '30'
            
            elif (count >= 30 + 15) and (count < 60 + 15):
                return '60'

            elif (count >= 60 + 15) and (count < 90 + 15):
                return '90'

            elif (count >= 90 + 15) and (count < 120 + 15):
               return '120' 

            elif (count >= 120 + 15) and (count < 150 + 15):
                return '150'

            elif (count >= 150 + 15) and (count < 180 + 15):
                return '180'

            elif (count >= 180 + 15) and (count < 210 + 15):
                return '210'

            elif count >= 210 + 15:
                return '>210'

        except:
            return pd.NA

    def __scoreColParse(self, score_and_scorers):
        try:
            score = float(score_and_scorers.split(', ')[0])

            return score

        except:
            return pd.NA

    def __scorersColParse(self, score_and_scorers):
        try:
            scorers = int(score_and_scorers.split(', ')[1])

            return scorers

        except:
            return pd.NA

    # This is going to want to be updated at some point in time - how are we going to do this update?
    def compileSQL(self, sql_dir):
        dfs = []
        for csv in os.listdir(self.__csv_dir):
            dfs.append(pd.read_csv(os.path.join(self.__csv_dir, csv)))

        df = pd.concat(dfs)

        df = df.dropna(how='all')

        kept_columns = ['name_english', 'name_japanese', 'show_type', 'source', 'episodes', 'producers', 
                        'licensors', 'studios', 'genres', 'episode_length', 'rating', 'description', 'score_and_scorers'] # Maybe I should go and add source in there too
        df = df[kept_columns]

        df['anime_id'] = df['name_japanese'].astype(str) + '+' + df['name_english'].astype(str)
        df['anime_id'] = df['anime_id'].apply(lambda x: hashlib.md5(x.encode()).hexdigest())

        df = df.drop_duplicates(subset=['anime_id'])
        df = df.reset_index()

        df['episode_length'] = df['episode_length'].apply(self.__parseEpLenCol)
        df['episode_length_bins'] = df['episode_length'].apply(self.__binEpLenCol)

        df['episodes'] = df['episodes'].apply(self.__parseEpisodesCol)
        df['episodes_bins'] = df['episodes'].apply(self.__binEpCountCol)

        df['score'] = df['score_and_scorers'].apply(self.__scoreColParse)
        df['scorers'] = df['score_and_scorers'].apply(self.__scorersColParse)
        df = df.drop('score_and_scorers', axis=1)

        df['score_percentage'] = df['score'] / 10
        df['std'] = (df['score_percentage'] * (-1 * df['score_percentage'] + 1) / df['scorers']) ** 0.5
        df['weighted_score'] = df['score_percentage'] - 2 * df['std']
        df = df.drop(['score_percentage', 'std'], axis=1)

        rearranged_cols = ['anime_id', 'name_japanese', 'name_english', 'show_type', 'source', 'rating', 'licensors', 'producers', 
                           'studios', 'genres', 'episodes', 'episodes_bins', 'episode_length', 'episode_length_bins', 
                           'score', 'scorers', 'weighted_score', 'description']
        df = df[rearranged_cols]

        conn = sqlite3.connect(sql_dir)
        df.to_sql('anime', conn)
        conn.close()

        return df

if __name__ == '__main__':
    csv_dir = os.path.join(os.getcwd(), 'backend/data/scraped_data/csv')
    sql_dir = os.path.join(os.getcwd(), 'backend/data/scraped_data/anime.db')

    data_scraper = Scraper(csv_dir)

    df = data_scraper.compileSQL(sql_dir)
    
    print(df.head(3))
