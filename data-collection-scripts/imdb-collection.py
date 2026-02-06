from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
import time

source = {
    "Movie": "https://www.imdb.com/chart/top/",
    "Tv-series": "https://www.imdb.com/chart/toptv/"
}

driver = webdriver.Chrome(
    service= Service(ChromeDriverManager().install())
)

def get_source_url(source):
    driver.get(source)

    WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.CSS_SELECTOR, "li.ipc-metadata-list-summary-item"))
    )

    data = []
    blocks = driver.find_elements(By.CSS_SELECTOR, "li.ipc-metadata-list-summary-item")

    for block in blocks:
        name = block.find_element(By.CLASS_NAME, "ipc-title__text").text

        a_tag = block.find_element(By.CLASS_NAME, "ipc-title-link-wrapper")
        url = a_tag.get_attribute("href")
        imdb_id = url.split("/title/")[1].split("/")[0]

        year = block.find_elements(By.CLASS_NAME, "cli-title-metadata-item")[0].text

        review_url = f"https://www.imdb.com/title/{imdb_id}/reviews"

        data.append({
            "name": name,
            "year": year,
            "review_url": review_url
        })


    return data

print(get_source_url(source["Movie"]))


