#!/usr/bin/env python
# coding: utf-8

# In[1]:


import requests
from bs4 import BeautifulSoup
import urllib
from urllib.parse import quote
from datetime import datetime
import re
from datetime import datetime, timedelta
import time  # Import the time module
from newspaper import Article
import random


# In[2]:


def similarity_score(a, b):
    words_a = a.lower().split()
    words_b = b.lower().split()

    # Handle cases where either input is empty
    if len(words_a) == 0 or len(words_b) == 0:
        return 0.0

    matching_words = 0

    for word_a in words_a:
        for word_b in words_b:
            if word_a in word_b or word_b in word_a:
                matching_words += 1
                break

    similarity = matching_words / min(len(words_a), len(words_b))
    return similarity


# In[3]:


def url_encode_string(input_string):
    encoded_string = urllib.parse.quote(input_string)
    return encoded_string


# In[4]:


def scrape_seeking_alpha_article_page(url, subject):
    try:
        news_id = url.split('/')[-1].split('-')[0] 
        # Prepare query parameters
        query_params = {"id": news_id}
        # Define the RapidAPI endpoint and API key
        rapidapi_url = "https://seeking-alpha.p.rapidapi.com/news/get-details"  # Update with the correct endpoint
        headers = {
            'x-rapidapi-key': "api-key-hidden-for-security-reasons",
            'x-rapidapi-host': "seeking-alpha.p.rapidapi.com"
            }
        # Make the GET request to the RapidAPI endpoint
        response = requests.get(rapidapi_url, headers=headers, params=query_params)
        # Check for a successful response
        if response.status_code == 200:
            data = response.json()
            #print(data)
            if data and similarity_score(subject, data["data"]["attributes"]["title"]) > 0.8 :
                data_content = data["data"]["attributes"]["content"]
                
                soup = BeautifulSoup(data_content, "html.parser")
                
                # Remove invisible content (e.g., paywall or unnecessary tags)
                #for invisible in soup.select(".paywall-full-content, .invisible"):
                    #invisible.decompose()
                
                content_text = soup.get_text().strip()
                
                #content_text = soup.get_text(separator="\n").strip()
                
                #print("Context:", content_text)
                return url, subject + ". With full context: " + content_text
            else:
                print("Not relevant")
                return "N/A", subject
        else:
            print("Unable to fetch info from ", url)
            return "N/A", subject
        
    except Exception as e:
        print("Exception in scrape_seeking_alpha_article_page:", e)
        return "N/A", subject


# In[5]:


def scrape_reuters(url, subject):
    try:
        # Prepare payload
        payload = [{ "url": url }]
        # Define the RapidAPI endpoint and API key
        rapidapi_url = "https://reuters-scraper.p.rapidapi.com/api/news/reuters-scraper/news"
        headers = {
                "x-rapidapi-key": "api-key-hidden-for-security-reasons",
                "x-rapidapi-host": "reuters-scraper.p.rapidapi.com",
                "Content-Type": "application/json"
                }
        # Make the POST request to the RapidAPI endpoint
        response = requests.post(rapidapi_url, json=payload, headers=headers)
        print(response.status_code)
        # Check for a successful response
        if response.status_code == 200:
            data = response.json()
            #print(data)
            #print(similarity_score(subject, data[0]['headline']))
            if data and similarity_score(subject, data[0]['headline']) > 0.8 :
                content_text = data[0]['content']
                
                #print("Context:", content_text)
                return url, subject + ". With full context: " + content_text
            else:
                print("Not relevant")
                return "N/A", subject
        else:
            print("Unable to fetch info from ", url)
            return "N/A", subject
        
    except Exception as e:
        print("Exception in scrape_seeking_alpha_article_page:", e)
        return "N/A", subject


# In[6]:


def scrape_yahoo_finance_article_page(url, subject):
    try:
        article = Article(url)
        article.download()
        article.parse()

        similarity = similarity_score(subject, article.title)
        print(similarity)
        if similarity >= 0.8:
            article_text = article.text
            content_text = article_text.replace('\n', ' ').replace('  ', ' ')
            return url, subject + ". With full context: " + content_text
        else:
            print("Not relevant")
            return "N/A", subject

    except Exception as e:
        print("Exception in scrape_yahoo_finance_article_page:", e)
        return "N/A", subject


# In[7]:


def scrape_business_wire_article_page(url, subject):
    try:
        article = Article(url)
        article.download()
        article.parse()

        similarity = similarity_score(subject, article.title)
        print(similarity)
        if similarity > 0.8:
            article_text = article.text
            content_text = article_text.replace('\n', ' ').replace('  ', ' ')
            return url, subject + ". With full context: " + content_text
        else:
            print("Not relevant")
            return "N/A", subject

    except Exception as e:
        print("Exception in scrape_business_wire_article_page:", e)
        return "N/A", subject


# In[8]:


def scrape_cnbc_article_page(url, subject):
    try:
        article = Article(url)
        article.download()
        article.parse()

        similarity = similarity_score(subject, article.title)
        print(similarity)
        if similarity > 0.8:
            article_text = article.text
            content_text = article_text.replace('\n', ' ').replace('  ', ' ')
            return url, subject + ". With full context: " + content_text
        else:
            print("Not relevant")
            return "N/A", subject

    except Exception as e:
        print("Exception in scrape_cnbc_article_page:", e)
        return "N/A", subject


# In[23]:


def scraping_by_url(link, subject):
    if "yahoo.com" in link:
        #print("Found 1 Yahoo Finance link:", link)
        url, subject = scrape_yahoo_finance_article_page(link, subject)
        return url, subject
    elif "seekingalpha.com" in link:
        #print("Found 1 Seeking Alpha link:", link)
        url, subject = scrape_seeking_alpha_article_page(link, subject)
        return url, subject
    elif "cnbc.com" in link:
        #print("Found 1 CNBC link:", link)
        url, subject = scrape_cnbc_article_page(link, subject)
        return url, subject
    elif "businesswire.com" in link:
        #print("Found 1 BusinessWire link:", link)
        url, subject = scrape_business_wire_article_page(link, subject)
        return url, subject
    elif "reuters.com" in link:
        #print("Found 1 Reuters link:", link)
        url, subject = scrape_reuters(link, subject)
        return url, subject
    #else:
        #print("Unrecognized link type: " + link)

    return "N/A", subject


# In[10]:


def parse_date_from_text(text):
    """
    Extract and parse a date from text.
    Handles relative times (e.g., '2 hours ago') and absolute dates (e.g., 'Jan 27, 2023').
    """
    try:
        # Define date patterns
        date_patterns = [
            r'(\d{1,2}\s\w+\s\d{4})',  # e.g., 14 December 2024
            r'(\w+\s\d{1,2},\s\d{4})',  # e.g., Jan 27, 2023
            r'(\d{1,2}\s(?:January|February|March|April|May|June|July|August|September|October|November|December)\s\d{4})',
            r'(\d{1,2}\s(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)\s\d{4})',
            r'(\d{1,2}\s(?:January|February|March|April|May|June|July|August|September|October|November|December))',
            r'(\d+)\s+(hour|minute|day|week|month|year)s?\s+ago',  # Relative dates like '2 hours ago'
        ]

        for pattern in date_patterns:
            match = re.search(pattern, text)
            if match:
                if "ago" in text:  # Handle relative dates
                    number = match.group(1)  # The numerical value (e.g., 2)
                    unit = match.group(2)  # The time unit (e.g., 'hours')

                    # Parse number as int
                    number = int(number)

                    if unit.startswith("hour"):
                        return datetime.now() - timedelta(hours=number)
                    elif unit.startswith("minute"):
                        return datetime.now() - timedelta(minutes=number)
                    elif unit.startswith("day"):
                        return datetime.now() - timedelta(days=number)
                    elif unit.startswith("week"):
                        return datetime.now() - timedelta(weeks=number)
                    elif unit.startswith("month"):
                        return datetime.now() - timedelta(days=number * 30)
                    elif unit.startswith("year"):
                        return datetime.now() - timedelta(days=number * 365)

                else:  # Handle absolute dates
                    date_str = match.group(1).replace(',', '')  # Remove any commas

                    # Try different date formats
                    for fmt in ['%d %B %Y', '%d %b %Y', '%d %B', '%d %b', '%b %d %Y']:
                        try:
                            parsed_date = datetime.strptime(date_str, fmt)

                            # Handle missing year by assuming the current year
                            if '%Y' not in fmt:
                                parsed_date = parsed_date.replace(year=datetime.now().year)
                            return parsed_date
                        except ValueError:
                            continue
        return None
    except Exception as e:
        print(f"Date parsing error: {e}")
        return None


# In[24]:


def scrape_google_with_dates(subject, subject_timestamp):
    def fetch_google_results(api_key, search_engine_id, subject, start=1):
        """
        Fetch Google search results for a specific page.
        """
        url = "https://www.googleapis.com/customsearch/v1"
        #print(api_key)
        params = {
            "key": api_key,
            "cx": search_engine_id,
            "q": subject,  # Search query
            "start": start,  # Results start index (1-100)
            #"sort":"date",
            }
        
        time.sleep(1)
    
        response = requests.get(url, params=params)

        if response.status_code != 200:
            print(f"Failed to fetch Google Search results. Status code: {response.status_code}")
            return None
        #print(response.json())

        return response.json()

    def process_search_results(data):
        links_with_dates = []

        for item in data.get("items", []):
            # Extract title, description, and link
            title_element = item['title']
            description_element = item['snippet']
            link_element = item['link']

            if title_element and description_element and link_element:
                title = title_element.strip()
                description = description_element.strip()
                link = link_element

                # Combine title and description for similarity scoring
                google_result = f"{title}. {description}"
                similarity = similarity_score(subject, google_result)
                #title_similarity = similarity_score(subject, title)
                #print(f"Google result: {google_result}")
                #print(f"Similarity: {similarity}")
                #print(f"link: {link}")

                # Extract timestamp from description
                timestamp = parse_date_from_text(description)
                #print(f"timestamp: {timestamp}")

                if timestamp:
                    # Skip the link if the subject timestamp is before the link timestamp
                    if subject_timestamp < timestamp:
                        #print(f"Skipping link: {link} (subject timestamp: {subject_timestamp}, link timestamp: {timestamp})")
                        continue

                    # Check similarity and add valid results
                    if similarity >= 0.75:
                        #print("Appending Link")
                        links_with_dates.append((link, timestamp))

        return sorted(
            links_with_dates,
            key=lambda x: abs((x[1] - subject_timestamp).total_seconds())
        )

    try:
        api_key="api-key-hidden-for-security-reasons"
        search_engine_id = "engine-id-hidden-for-security-reason"
        # Fetch google search results
        response_data = fetch_google_results(api_key, search_engine_id, subject, 1)
        if not response_data :
            return subject, False

        sorted_links = process_search_results(response_data)

        # Check sorted_links and attempt scraping
        for link, timestamp in sorted_links:
            url, scraped_subject = scraping_by_url(link, subject)
            if url != "N/A":
                #print(f"Valid result found. URL: {url}, Subject: {scraped_subject}")
                return scraped_subject, True
            #else:
                #print(f"Invalid URL ('N/A') for link: {link}, trying next link.")
        
        # Fetch google search results
        response_data = fetch_google_results(api_key, search_engine_id, subject, 1)
        if not response_data :
            return subject, False

        sorted_links = process_search_results(response_data)

        # Check sorted_links and attempt scraping
        for link, timestamp in sorted_links:
            url, scraped_subject = scraping_by_url(link, subject)
            if url != "N/A":
                #print(f"Valid result found. URL: {url}, Subject: {scraped_subject}")
                return scraped_subject, True
            #else:
                #print(f"Invalid URL ('N/A') for link: {link}, trying next link.")
        
        # Fetch google search results
        response_data = fetch_google_results(api_key, search_engine_id, subject, 1)
        if not response_data :
            return subject, False

        sorted_links = process_search_results(response_data)

        # Check sorted_links and attempt scraping
        for link, timestamp in sorted_links:
            url, scraped_subject = scraping_by_url(link, subject)
            if url != "N/A":
                #print(f"Valid result found. URL: {url}, Subject: {scraped_subject}")
                return scraped_subject, True
            #else:
                #print(f"Invalid URL ('N/A') for link: {link}, trying next link.")

        # If no valid links found even on the next page, return the original subject
        #print("No valid links found on both pages. Returning the original subject.")
        return subject, False

    except Exception as e:
        #print("Exception in scrape_google_with_dates:", e)
        return subject, False  # Return the original subject in case of any exception


# In[27]:

def scrape_google(subject):
    def fetch_google_results(api_key, search_engine_id, subject, start=1):
        """
        Fetch Google search results for a specific page.
        """
        url = "https://www.googleapis.com/customsearch/v1"
        #print(api_key)
        params = {
            "key": api_key,
            "cx": search_engine_id,
            "q": subject,  # Search query
            "start": start,  # Results start index (1-100)
            #"sort":"date",
            }
        
        time.sleep(1)
    
        response = requests.get(url, params=params)

        if response.status_code != 200:
            print(f"Failed to fetch Google Search results. Status code: {response.status_code}")
            return None
        #print(response.json())

        return response.json()

    def process_search_results(data):
        searched_links = []

        for item in data.get("items", []):
            # Extract title, description, and link
            title_element = item['title']
            description_element = item['snippet']
            link_element = item['link']

            if title_element and description_element and link_element:
                title = title_element.strip()
                description = description_element.strip()
                link = link_element

                # Combine title and description for similarity scoring
                google_result = f"{title}. {description}"
                similarity = similarity_score(subject, google_result)
                #title_similarity = similarity_score(subject, title)
                #print(f"Google result: {google_result}")
                #print(f"Similarity: {similarity}")
                #print(f"link: {link}")

                if similarity >= 0.75:
                        #print("Appending Link")
                        searched_links.append((link))

        return searched_links

    try:
        api_key="api-key-hidden-for-security-reasons"
        search_engine_id = "engine-id-hidden-for-security-reasons"
        # Fetch google search results
        response_data = fetch_google_results(api_key, search_engine_id, subject, 1)
        if not response_data :
            return subject, False

        fetched_links = process_search_results(response_data)

        # Check sorted_links and attempt scraping
        for link in fetched_links:
            url, scraped_subject = scraping_by_url(link, subject)
            if url != "N/A":
                #print(f"Valid result found. URL: {url}, Subject: {scraped_subject}")
                return scraped_subject, True
            #else:
                #print(f"Invalid URL ('N/A') for link: {link}, trying next link.")
        

        # If no valid links found even on the next page, return the original subject
        #print("No valid links found on both pages. Returning the original subject.")
        return subject, False

    except Exception as e:
        #print("Exception in scrape_google_with_dates:", e)
        return subject, False  # Return the original subject in case of any exception


def enrich_dataset_with_contextual_text(dataset):
    """
    Adds a new column 'contextual_text' to the dataset.
    Handles missing 'publishedTime' or invalid/null values by using the current time.
    If 'publishedTime' is valid, adds 7 days to the parsed timestamp.
    """
    def add_contextual_text(row):
        subject = row['text']
        current_time = datetime.now()
        
        try:
            # Handle missing or invalid 'publishedTime'
            if 'publishedTime' not in row or not row['publishedTime'] or row['publishedTime'].strip() == "":
                subject_timestamp = current_time
            else:
                # Parse 'publishedTime' and add 7 days
                subject_timestamp = datetime.strptime(row['publishedTime'], "%Y-%m-%dT%H:%M:%SZ")
                subject_timestamp += timedelta(days=45)
        except Exception as e:
            print(f"Error parsing publishedTime: {e}")
            subject_timestamp = current_time  # Fallback to current time

        # Call the scraping function
        contextual_subject, context_fetched = scrape_google_with_dates(subject, subject_timestamp)
        return {"contextual_text": contextual_subject, "context_fetched": context_fetched}

    # Apply the function to the dataset
    return dataset.map(add_contextual_text)
    

def scrape_google_context(dataset):
    def add_google_contextual_text(row):
        subject = row['text']

        # Call the scraping function
        contextual_subject, context_fetched = scrape_google(subject)
        return {"google_context": contextual_subject, "google_context_fetched": context_fetched}

    # Apply the function to the dataset
    return dataset.map(add_google_contextual_text)


# In[ ]:




