import requests
from bs4 import BeautifulSoup


# Basically sents a request to the specified URL and returns the HTML content of the page
def get_page_content(url):
    try:
        response = requests.get(url)
        response.raise_for_status()  # this will raise an exception if the response status code is not 200 (errors)
        return response.text
    except requests.exceptions.RequestException as e:
        print(f"An error occurred: {e}")
        return None

# Parses the HTML content using BeautifulSoup, and returns the parsed content as a BeautifulSoup object which is just a wrapper around the HTML content
def parse_html(html_content):
    soup = BeautifulSoup(html_content, 'html.parser')
    return soup

# Seaerch for university-affiliated websites using Google
def perform_search(keywords):
    """
    Performs a search using the given keywords and returns the URLs of the top search results.
    
    Parameters:
    keywords (list): A list of keywords or phrases to search for.
    
    Returns:
    list: A list of URLs of the top search results.
    """
    search_url = "https://www.google.com/search?q=" + "+".join(keywords)
    html_content = get_page_content(search_url)
    
    if html_content:
        soup = parse_html(html_content)
        search_results = soup.find_all('div', class_='yuRUbf')
        urls = [result.find('a')['href'] for result in search_results]
        return urls
    
    return []

# Search for newsletter links within the parsed HTML using BeautifulSoup
def find_newsletter_links(soup):
    
    newsletter_links = []
    
    # Find newsletter links based on common patterns or CSS classes
    newsletter_elements = soup.select('a[href*="newsletter"], a[href*="subscribe"]')
    
    for element in newsletter_elements:
        link = element['href']
        newsletter_links.append(link)
    
    return newsletter_links

# Extract the university name from the parsed HTML using BeautifulSoup
def find_university_name(soup):
    university_name = ""
    
    # Find the university name based on common patterns or CSS classes
    university_elements = soup.select('h1, h2, h3, .university-name, .institution-name')
    
    if university_elements:
        university_name = university_elements[0].get_text(strip=True)
    
    return university_name


# Extract the entrepreneurship group name from the parsed HTML using BeautifulSoup
def find_entrepreneurship_group(soup):
    group_name = ""
    
    # Find the entrepreneurship group name based on common patterns or CSS classes
    group_elements = soup.select('.entrepreneurship-group, .startup-club, .innovation-center')
    
    if group_elements:
        group_name = group_elements[0].get_text(strip=True)
    
    return group_name

