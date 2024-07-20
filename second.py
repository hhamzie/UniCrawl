import os
import pandas as pd
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from urllib.parse import urlencode, quote_plus
import json
from itertools import product

def clean_snippet(snippet):
    # Remove unwanted prefixes
    unwanted_prefixes = ['WEB']
    for prefix in unwanted_prefixes:
        if snippet.startswith(prefix):
            snippet = snippet[len(prefix):].strip()
    return snippet

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
suffixes = [
    'entrepreneurship', 'entrepreneurial', 'startup', 'innovation', 'incubator', 
    'accelerator', 'center for entrepreneurship', 'entrepreneurship center', 
    'innovation lab', 'venture', 'entrepreneurship club', 'entrepreneurship program', 
    'business incubator', 'entrepreneurship institute', 'entrepreneurship network', 
    'entrepreneurship organization'
]

# Create combinations of names with prefixes and suffixes
queries = [f"{prefix} {name} {suffix}" for name, prefix, suffix in product(names, prefixes, suffixes)]

# Create base URL
base_url = 'https://www.bing.com/search'

# List to hold the scraped data
results = []

# Set to track processed titles to avoid duplicates
processed_titles = set()

# Define blacklist words
blacklist = ['course', 'class', 'training', 'certificate', 'degree']

def find_newsletter_link(driver):
    # List of keywords to identify newsletter links or forms
    keywords = ['newsletter', 'subscribe', 'email', 'sign up']
    page_source = driver.page_source.lower()
    
    # Look for links and forms
    links = driver.find_elements(By.TAG_NAME, 'a')
    forms = driver.find_elements(By.TAG_NAME, 'form')
    
    for link in links:
        href = link.get_attribute('href')
        if href and any(keyword in link.text.lower() for keyword in keywords):
            return href
    
    for form in forms:
        if any(keyword in form.get_attribute('outerHTML').lower() for keyword in keywords):
            return driver.current_url
    
    return None

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
            try:
                title_element = result.find_element(By.CSS_SELECTOR, 'h2 a')
                snippet_element = result.find_element(By.CSS_SELECTOR, 'div.b_caption p')
                
                title = title_element.text if title_element else 'N/A'
                link = title_element.get_attribute('href') if title_element else 'N/A'
                snippet = snippet_element.text if snippet_element else 'N/A'
                
                snippet = clean_snippet(snippet)
                
                # Check if specific words are in the snippet and blacklist words are not in the title or snippet
                if not any(blacklisted_word in snippet.lower() or blacklisted_word in title.lower() for blacklisted_word in blacklist):
                    if title != 'N/A' and link != 'N/A' and snippet != 'N/A':
                        # Check if the title has already been processed
                        if title not in processed_titles:
                            try:
                                # Navigate to the link to check for a newsletter subscription form or link
                                driver.get(link)
                                newsletter_link = find_newsletter_link(driver)
                                if newsletter_link:
                                    results.append({
                                        'title': title,
                                        'link': link,
                                        'snippet': snippet,
                                        'newsletter_link': newsletter_link,
                                    })
                                    # Add the title to the processed set to avoid duplicates
                                    processed_titles.add(title)
                                else:
                                    print('No newsletter link found on page, skipping result.')
                            except Exception as e:
                                print(f"Error processing link '{link}': {str(e)}")
            except Exception as e:
                print(f"Error processing result: {str(e)}")
    
    except Exception as e:
        print(f"Error processing query '{query}': {str(e)}")

# Save the results to a JSON file
with open('university_newsletters2.json', 'w') as f:
    json.dump(results, f, indent=4)

# Close the WebDriver
driver.quit()

print("Scraping complete. Data saved to university_newsletters.json")
