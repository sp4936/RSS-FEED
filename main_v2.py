from bs4 import BeautifulSoup
import requests
import re
import pandas as pd
import os
import time as t
import datetime
import spacy

'''
--> spaCy provides pre-trained models for various languages, which include tokenization, 
    part-of-speech tagging, named entity recognition, and more. 
    These models are trained on large datasets and are ready to use out of the box.
    
--> spaCy excels in NER, identifying and categorizing entities in text such as 
    names, dates, locations, organisation and more.
'''
iteration = 1
# Load spaCy model
nlp = spacy.load('en_core_web_sm')

# Fetch data from URL
def get_url(i):
    if i == 0:
        # PR Newswire RSS Feed
        url = requests.get('https://www.prnewswire.com/apac/rss/news-releases-list.rss')
    elif i == 1:
        # Business Newswire RSS Feed
        url = requests.get('https://www.newswire.com/newsroom/rss/business-business-news')
    elif i == 2:
        # Global Newswire --> Public Companies RSS Feed
        url = requests.get('https://www.globenewswire.com/RssFeed/orgclass/1/feedTitle/GlobeNewswire%20-%20News%20about%20Public%20Companies')
    elif i == 3:
        # Business Newswire --> Industry News
        url = requests.get('https://www.newswire.com/newsroom/rss/industries-industry-news')
    elif i == 4:
        # Global Newswire --> Mergers and Acquisitions
        url = requests.get('https://www.globenewswire.com/RssFeed/subjectcode/27-Mergers%20and%20Acquisitions/feedTitle/GlobeNewswire%20-%20Mergers%20and%20Acquisitions')
    return url

# Extract key terms using spaCy NER
def extract_key_terms(text):
    doc = nlp(text)
    key_terms = [ent.text for ent in doc.ents if ent.label_ in {'ORG', 'PERSON', 'GPE', 'PRODUCT'}]
    return key_terms

# Generate announcement id mapping
announcement_id_map = {}
current_id = 1

# Function to get or create announcement id
def get_announcement_id(title, summary):
    global current_id
    key_terms = tuple(sorted(set(extract_key_terms(title + ' ' + summary))))
    if key_terms not in announcement_id_map:
        announcement_id_map[key_terms] = current_id
        current_id += 1
    return announcement_id_map[key_terms]

# Continuous Run
while True:
    i = 0
    # Loop run for every RSS feed (We have total 5 RSS Feeds)
    while i < 5:
        # Function call
        url = get_url(i)
        soup = BeautifulSoup(url.content, 'xml')

        # Get all news of RSS Feed
        entries = soup.find_all('item')

        # List of Keywords that we want to match in news
        keywords = [
            "merger", "acquisition", "definitive agreement", "takeover", "takeover speculations", "nearing deal", "consider sale", "proposal",
            "proposal to acquire", "non binding offer", "exploring sale", "including sale", "exploring option", "in talks",
            "potential offer", "acquisition target", "buyout", "buyback", "consolidation", "joint venture", "investment",
            "equity investment", "strategic partnership", "strategic alliance", "divestiture", "spin-off", "restructuring",
            "capital infusion", "equity stake", "stake acquisition", "share purchase", "management buyout",
            "leveraged buyout", "private equity", "recapitalization", "asset purchase", "friendly takeover", "hostile takeover",
            "reverse merger", "merger proposal", "asset sale", "partnership deal", "equity transfer", "take-private deal",
            "tender offer", "partnership", "merge", "acquire", "acquires"
        ]

        # Initialize a list to store the filtered entries
        filtered_entries = []

        # now = datetime.now()
        now = datetime.datetime.now()
        # current_time = now.strftime("%H:%M:%S")

        # Get Title, Summary, Link, Time of each News
        for entry in entries:
            title = entry.title.text
            summary = entry.description.text
            link = entry.link.text
            time = entry.pubDate.text

            # Check if any keyword is present in the title or summary
            matched_keywords = [keyword for keyword in keywords if re.search(keyword, title.lower()) or re.search(keyword, summary.lower())]
            if matched_keywords:
                announcement_id = get_announcement_id(title, summary)
                filtered_entries.append({
                    'Announcement ID': announcement_id,
                    'Time': time,
                    'System Time': now,
                    'Keywords': ', '.join(matched_keywords),
                    'Title': title,
                    'Summary': summary,
                    'Link': link
                    
                })
                
       
        # Create a DataFrame from the filtered entries
        new_df = pd.DataFrame(filtered_entries)

        # Define the CSV file path
        csv_file_path = 'filtered_news.csv'

        if os.path.exists(csv_file_path):
            # Read the existing CSV file into a DataFrame
            existing_df = pd.read_csv(csv_file_path)
            # Concatenate the existing DataFrame with the new DataFrame
            combined_df = pd.concat([existing_df, new_df])
            # Drop duplicates based on the 'Link' column
            combined_df = combined_df.drop_duplicates(subset='Link')
            #combined_df['time']= pd.to_datetime(combined_df['time'])
        else:
            # If the CSV file doesn't exist, the combined DataFrame is just the new DataFrame
            combined_df = new_df
            #combined_df['time']= pd.to_datetime(combined_df['time'])

        # Save the updated DataFrame back to the CSV file
        combined_df.to_csv(csv_file_path, index=False)

        # Print the updated DataFrame
        print(combined_df)

        # Increase the iteration to fetch data of the next RSS Feed
        i += 1

    # Program is stopped to run for 5 minutes
    print(iteration,'--------------------------------------------------------------------')
    iteration += 1
    t.sleep(1)
