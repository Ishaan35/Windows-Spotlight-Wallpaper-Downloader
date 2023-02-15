from http.server import BaseHTTPRequestHandler, HTTPServer
from selenium.webdriver.common.by import By
from selenium import webdriver
import time
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.chrome.options import Options
from random import randrange
import os
from bs4 import BeautifulSoup

import asyncio
import aiohttp
import uuid


user_agent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/85.0.4183.83 Safari/537.36"

options = Options()
options.headless = True
options.binary_location = os.environ.get("GOOGLE_CHROME_BIN")
options.add_argument('--ignore-certificate-errors')
options.add_argument('--allow-running-insecure-content')
options.add_argument("--disable-extensions")
options.add_argument("--proxy-server='direct://'")
options.add_argument("--proxy-bypass-list=*")
options.add_argument("--start-maximized")
options.add_argument('--log-level=0')
options.add_argument('--no-sandbox')
options.add_argument('--disable-dev-shm-usage')
options.add_argument('--disable-gpu')
options.add_argument("--window-size=1920,1080")
options.add_argument(f'user-agent={user_agent}')

caps = webdriver.DesiredCapabilities.CHROME.copy()
caps['acceptInsecureCerts'] = True
driver = webdriver.Chrome('./chromedriver', options=options, desired_capabilities=caps)


def goToPage():
    driver.get("https://windows10spotlight.com/page/1")


async def download_image(session, url):
    async with session.get(url) as response:
        return await response.read()


async def download_images(image_urls):
    async with aiohttp.ClientSession() as session:
        tasks = [download_image(session, url) for url in image_urls]
        results = await asyncio.gather(*tasks)
        for result in results:
            filename = str(os.path.join(
                "images", f"{uuid.uuid4()}.jpg")) + ".jpg"
            with open(filename, "wb") as f:
                f.write(result)
    



def parsePage():
    soup = BeautifulSoup(driver.page_source, 'html.parser')
    images = soup.find_all('img')
    urls = []
    for image in images:
        # check if the src attribute starts with the desired string
        if 'srcset' in image.attrs and image['srcset'].startswith("https://windows10spotlight.com/wp-content/uploads/"):
            image_sizes = image['srcset'].split(",")
            image = image_sizes[len(image_sizes)-1]
            image = image[:-6]
            image = image[1:]
            print(image)
            urls.append(image)
    
    asyncio.run(download_images(urls))


def findNextButton():
    button = None
    try:
        button = driver.find_element(By.CSS_SELECTOR, ".next.page-numbers")
    except:
        pass
    return button

def startParsingImages():
    btn = findNextButton()
    while not btn is None:
        parsePage()
        btn.click()
        time.sleep(2.5)
        btn = findNextButton()
    
    return




goToPage()
time.sleep(4)
startParsingImages()
exit()
