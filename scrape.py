from utilis import get_urls

import requests
import time
import json
from newspaper import Article 


def extract_article_content(urls =get_urls() ):
    '''
    This function scrape article content and save it as well as the corresponding url.
    '''

    #define a User-Agent string to mimic a real browser's request
    headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/89.0.4389.82 Safari/537.36'
            }
    session = requests.Session()
    pages_content = [] # where we save the scraped articles

    for url in urls:
        try:
            time.sleep(2) # sleep two seconds for gentle scraping
            response = session.get(url, headers=headers, timeout=10) #send a get request to the url

            if response.status_code == 200:
                article = Article(url)
                article.download() # download HTML of webpage
                article.parse() # parse HTML to extract the article text
                pages_content.append({ "url": url, "text": article.text })
            else:
                print(f"Failed to fetch article at {url}")
        except Exception as e:
            print(f"Error occurred while fetching article at {url}: {e}")

    with open("data/article_content.json", "w") as f:
            json.dump(pages_content, f)




if __name__ == "__main__":
    extract_article_content(urls =get_urls())