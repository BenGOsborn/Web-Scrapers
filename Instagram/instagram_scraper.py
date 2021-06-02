from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from bs4 import BeautifulSoup
from time import sleep
import requests
import os
import sys

class InstagramImageScraper: # Create the instagram scraper class
    def __init__(self): # Create the constructor
        self.driver = webdriver.Chrome(executable_path='..\\chromedriver.exe') # Load the web driver

        self.insta_user = None # Initialize the instagram user to be none

        self.posts = [] # Create the list where the users posts will be stored 
        self.img_urls = [] # Create the list where the urls for the images scraped will be stored
    
    def set_user(self, insta_user): # Create the function that will set the user to be the argument specified
        self.insta_user = insta_user # Set the insta user to the user specified by the argument
        self.posts = [] # Set the posts list to be empty
        self.img_urls = [] # Set the img urls list to be etmpy
    
    def login(self, username, password): # Create the function that will log into to the scrapers own instagram account
        self.driver.get('https://www.instagram.com/accounts/login/') # Navigate to the login page
        sleep(1) # Sleep for 1 second
        self.driver.find_element_by_xpath('/html/body/div[1]/section/main/div/div/div[1]/div/form/div/div[1]/div/label/input').send_keys(username) # Enter the username
        sleep(0.5) # Sleep for 0.5 seconds
        self.driver.find_element_by_xpath('/html/body/div[1]/section/main/div/div/div[1]/div/form/div/div[2]/div/label/input').send_keys(password) # Enter the password
        sleep(0.5) # Sleep for 0.5 seconds
        self.driver.find_element_by_xpath('/html/body/div[1]/section/main/div/div/div[1]/div/form/div/div[3]/button').click() # Click the login button
        sleep(3) # Sleep for 3 seconds

    def __load_current_posts(self): # Create the private member that will load the posts on the page
        article_html = self.driver.execute_script('return document.querySelector("#react-root > section > main > div > div._2z6nI").innerHTML') # Get the HTML of the page
        soup = BeautifulSoup(article_html, features='html5lib') # Load the HTML into a beautiful soup object

        posts = soup.find_all('div', {'class': 'v1Nh3 kIKUG _bz0w'}) # Find all the posts
        for post in posts: # Iterate over each post beautiful soup object
            post_url = f"https://www.instagram.com{post.find('a')['href']}" # Find the url of the post
            if post_url not in self.posts: # If the post is not already in the posts list
                self.posts.append(post_url) # Add the post to the posts list

    def load_posts(self): # Create the method that will load the instagram page and load all the posts
        page_url = f"https://www.instagram.com/{self.insta_user}/" # Create the url where the users profile is
        self.driver.get(page_url) # Go to the users profile
        sleep(2) # Sleep for 2 seconds

        profile_pic_html = self.driver.execute_script('return document.querySelector("#react-root > section > main > div > header > div > div > span").innerHTML') # Get the HTML of the page
        pp_soup = BeautifulSoup(profile_pic_html, features='html5lib') # Create a soup object out of the HTML
        profile_pic = pp_soup.find('img', {'class': '_6q-tv'})['src'] # Find the profile picture
        self.img_urls.append(profile_pic) # Add the profile picture to the img urls list

        scroll_height = self.driver.execute_script('return this.document.body.scrollHeight') # Get the scroll height
        while True: # Loop continuously under we break
            self.__load_current_posts() # Scrape the articles for the current scroll
            self.driver.find_element_by_tag_name('body').send_keys(Keys.END) # Scroll down
            sleep(2) # Sleep for 2 seconds
            new_scroll_height = self.driver.execute_script('return this.document.body.scrollHeight') # Get the new scroll height
            if (new_scroll_height == scroll_height): # If the new scroll height is the same as the previous scroll height
                break # Break the while loop
            scroll_height = new_scroll_height # Set the scroll height equal to the new scroll height

    def __scrape_post(self, post_url): # Create the function that will scrape the posts from a post page
        self.driver.get(post_url) # Navigate to the posts url
        sleep(1) # Sleep for 1 second

        while True: # Loop continuously until we break
            try: # If there are no errors
                self.driver.find_element_by_class_name('_6CZji').click() # Click on the next button
                sleep(0.5) # Sleep for 0.5 seconds
                post_src_html = self.driver.execute_script('return document.querySelector("#react-root > section > main > div > div.ltEKP > article > div._97aPb.wKWK0 > div > div.pR7Pc > div.Igw0E.IwRSH.eGOV_._4EzTm.O1flK.D8xaz.fm1AK.TxciK.yiMZG > div > div > div > ul").innerHTML') # Get the HTML of the element
                soup = BeautifulSoup(post_src_html, features='html5lib') # Convert the HTML to a beautiful soup object

                pictures = soup.find_all('img', {'class': 'FFVAD'}) # Find all the images in the HTML
                for img in pictures: # Iterate over the images
                    img_url = img['src'] # Get the url of the image
                    if img_url not in self.img_urls: # If the img url is not in the img urls list
                        self.img_urls.append(img_url) # Add the image url to the img urls list
                    
            except: # If we encounter an error
                break # Break the while loop

    def scrape_posts(self): # Create the function that will scrape the posts
        for post_url in self.posts: # Iterate over the posts in the posts list
            self.__scrape_post(post_url) # Perform the scrape post function on the post url

    def download_images(self, save_dir): # Create the function that will download the images to the directory we specify
        for i, img_url in enumerate(self.img_urls): # Enumerate over the images
            img_name = f"{self.insta_user}-{i}.jpg" # Create the name of the image and specify its file type
            try: # If there are no errors
                img_data = requests.get(img_url).content # Read the contents of the image from the url
                img_path = os.path.join(save_dir, img_name) # Specify the name and filetype of the file and where it will be saved to
                with open(img_path, 'wb') as file: # Create a new image or read an existing image from the image path
                    file.write(img_data) # Write the contents of the image to this file

            except Exception as e: # If there is an error
                print(f"Failed to download image '{img_name}'. Reason: '{e}'.") # Print out the error that occured when trying to download the image as well as the image the error occured with

    def exit(self): # Create the function that will close the web driver
        self.driver.close() # Close the web driver

def main(): # The function that will contain the main code for the task
    insta_username = sys.argv[1] # The first command line argument will be the scrapers Instagram username
    insta_password = sys.argv[2] # The second command line argument will be the scrapers Instagram password
    save_dir = sys.argv[3] # The third command line argument will be the directory to save the images to
    insta_accounts = sys.argv[4:] # The fourth and nonwards arguments will be the usernames of the profiles to be scraped

    insta_bot = InstagramImageScraper() # Initialize the scraper
    insta_bot.login(insta_username, insta_password) # Login

    for insta_user in insta_accounts: # Iterate over the instagram profiles to be scraped
        try: # If there are no errors
            print(f"Scraping user '{insta_user}'...") # Print out that the scraper has begun scraping the current users profile

            insta_bot.set_user(insta_user) # Set the instagram bot to scrape the current users profile

            insta_bot.load_posts() # Load the posts from the page

            insta_bot.scrape_posts() # Scrape the image urls from all of the posts

            custom_save_dir = os.path.join(save_dir, insta_user) # Specify the directory to save the images for this user to
            if not os.path.exists(custom_save_dir): # If the save directory doesnt exist
                os.mkdir(custom_save_dir) # Create the new save directory
            insta_bot.download_images(custom_save_dir) # Download the images to the save directory
        
        except Exception as e: # If there is an error
            print(f"Failed for user '{insta_user}'. Reason: '{e}'.") # Print the error and the instagram user the error was encountered for

    insta_bot.exit() # Close the scraper
    print("Exiting. Goodbye!") # Print a goodbye message

if __name__ == '__main__': # If this file is run directly
    main() # Call the main function
