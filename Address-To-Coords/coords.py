from selenium import webdriver # Try and do this with requests-html instead so it doesnt need selenium
from time import sleep

def address_to_coords(address, retries=100):
    formatted_address = "+".join(address.strip().split(" "))
    BASE_URL = f"https://www.google.com/maps/place/{formatted_address}"

    options = webdriver.ChromeOptions()
    options.add_argument('--headless')

    driver = webdriver.Chrome(options=options)
    driver.get(BASE_URL)

    changed = False
    while not changed and retries > 0:
        if (BASE_URL != driver.current_url):
            changed = True
            
        else:
            retries -= 1
            sleep(0.5)

    assert not (retries == 0 and not changed), "Failed to get coordinates for given address!"

    raw_url = driver.current_url
    coords = [float(coord) for coord in raw_url.split("/")[6][1:].split(",")[:2]]

    driver.close()

    return coords

if __name__ == "__main__":
    ADDRESS = "address"
    coords = address_to_coords(ADDRESS)

    print(coords)
