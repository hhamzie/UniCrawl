import os
import pandas as pd
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from urllib.parse import urlencode, quote_plus
from itertools import product
import json

# Path to your ChromeDriver executable
chrome_driver_path = '/Users/hamzehhammad/Documents/02_PersonalProjects/UniCrawl/chrome-mac-arm64/chromedriver'  # Ensure this is the correct path to the chromedriver executable

# Configure Selenium options
chrome_options = Options()
chrome_options.add_argument('--headless')  # Run in headless mode
chrome_options.add_argument('--disable-gpu')
chrome_options.add_argument('--no-sandbox')
chrome_options.add_argument('--disable-dev-shm-usage')

# Initialize WebDriver
service = Service(chrome_driver_path)
driver = webdriver.Chrome(service=service, options=chrome_options)

# Construct the absolute path to the CSV file
csv_path = '/Users/hamzehhammad/Documents/02_PersonalProjects/UniCrawl/documents/colleges2.csv'
# Load only the 'NAME' column and skip bad lines
df = pd.read_csv(csv_path, usecols=['NAME'], on_bad_lines='skip')

# Ensure there's a column named 'NAME' with university/college names and convert them to lowercase
names = df['NAME'].str.lower().tolist()

# Define prefixes and suffixes for the search terms
prefixes = ['university', 'college']
suffixes = ['entrepreneurship', 'entrepreneurial', 'startup', "startups", "entrepreneurs"]

# Create combinations of names with prefixes and suffixes
queries = [f"{prefix} {name} {suffix}" for name, prefix, suffix in product(names, prefixes, suffixes)]

# Create base URL
base_url = 'https://www.bing.com/search'

# List to hold the scraped data
results = []

for query in queries:
    params = {'q': query}
    query_string = urlencode(params, quote_via=quote_plus)
    url = f"{base_url}?{query_string}"

    driver.get(url)
    
    try:
        # Wait for search results to load
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, 'li.b_algo'))
        )
        
        # Parse the search results
        search_results = driver.find_elements(By.CSS_SELECTOR, 'li.b_algo')
        for result in search_results:
            title = result.find_element(By.CSS_SELECTOR, 'h2 a').text
            link = result.find_element(By.CSS_SELECTOR, 'h2 a').get_attribute('href')
            snippet = result.find_element(By.CSS_SELECTOR, 'div.b_caption p').text
            
            if title and link and snippet:
                results.append({
                    'title': title,
                    'link': link,
                    'snippet': snippet,
                })
            else:
                print('Missing data, skipping result.')
    
    except Exception as e:
        print(f"Error processing query '{query}': {str(e)}")

# Save the results to a JSON file
with open('university_newsletters.json', 'w') as f:
    json.dump(results, f, indent=4)

# Close the WebDriver
driver.quit()

print("Scraping complete. Data saved to university_newsletters.json")
