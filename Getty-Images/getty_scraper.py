from selenium import webdriver
from bs4 import BeautifulSoup
import requests
import sys
import os
from time import sleep

class Scraper: # Create the scraper class
    def __init__(self): # Define the contructor
        self.driver = webdriver.Chrome(executable_path='..\\chromedriver.exe') # Create the webdriver

        self.url = None # Set the base url to be none on initialization

        self.img_urls = [] # Create the list that stores the urls of the images

    def set_url(self, url): # Create the method that will set the url to be scraped (no trailing queries)
        self.url = url # Set the URL to the one specified as the argument of the method
    
    def scrape_url(self): # Scrape the set url
        page = 1 # Set the page to initially be true

        while True: # Loop until we break manually
            try: # If there are no errors
                url = f"{self.url}?page={page}" # Set the page of the URL to scrape
                self.driver.get(url) # Navigate to that url
                sleep(2) # Wait 2 seconds
                
                articles_html = self.driver.execute_script('return document.querySelector("#gallery > div").innerHTML') # Return the html
                soup = BeautifulSoup(articles_html, parser='html5lib') # Load the HTML into a bs4 object
                article_urls = soup.find_all('img', {'class': 'gallery-asset__thumb gallery-mosaic-asset__thumb'}) # Find all images within the HTML
                for article_url in article_urls: # Iterate over the image soup objects
                    src = article_url['src'] # Get the url to the image
                    if src not in self.img_urls: # If the image url is not already in the img urls list
                        self.img_urls.append(src) # Add the image url to the list

                page += 1 # Increment the page number so the driver will try and scrape the next page
            
            except: # If there is an error scraping the page it means there musnt be any content on the page
                break # Break the loop as there is no more content

    def exit(self): # Create the function that will close the web driver
        self.driver.close() # Close the web driver
    
    def save_images(self, save_dir): # Create the function that will save the images from the urls
        for i, url in enumerate(self.img_urls): # Enumerate over the image urls
            save_path = os.path.join(save_dir, f"{i}.jpg") # Specify the name and file type of the saved image and the location to save it to
            img_data = requests.get(url).content # Load the content from the image
            with open(save_path, 'wb') as file: # Open a new file in the location specified and with the name and file type specified
                file.write(img_data) # Write the contents of the image to the file

def main(): # Create the function that will contain the main code
    save_dir = sys.argv[1] # The first command line argument will be the directory to save the images to
    raw_url = sys.argv[2] # The second command line argument will be the URL to scrape the images from

    bot = Scraper() # Initialize the scraper

    bot.set_url(raw_url) # Set the url of the bot

    bot.scrape_url() # Scrape the url

    bot.exit() # Close the bot

    bot.save_images(save_dir) # Save the images the bot has scraped to the directory specified

if __name__ == '__main__': # If this file is run directly
    main() # Call the main function
