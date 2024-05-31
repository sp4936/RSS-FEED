from bs4 import BeautifulSoup
import requests
import re
import pandas as pd
import os

import time as t

def get_url(i):
    if i == 0:
            url = requests.get('https://www.prnewswire.com/apac/rss/news-releases-list.rss')    # PR Newswire
        
    elif i == 1:
            url = requests.get('https://www.newswire.com/newsroom/rss/business-business-news')  # Business Newswire
            
    elif i == 2:
            url = requests.get('https://www.globenewswire.com/RssFeed/orgclass/1/feedTitle/GlobeNewswire%20-%20News%20about%20Public%20Companies')  # Global Newswire --> Public Companies
    
    elif i == 3:
            url = requests.get('https://www.newswire.com/newsroom/rss/industries-industry-news')  # Business Newswire --> Industry News
            
    elif i == 4:
            url = requests.get('https://www.globenewswire.com/RssFeed/subjectcode/27-Mergers%20and%20Acquisitions/feedTitle/GlobeNewswire%20-%20Mergers%20and%20Acquisitions')  # Global Newswire --> Mergers and Acquisitions
    
            
    return url
        

while True:
    i = 0
    while(i<5):
        url = get_url(i)
            
        soup = BeautifulSoup(url.content, 'xml')
    
        entries = soup.find_all('item')
    
        keywords = [
            "definitive agreement", "takeover", "takeover speculations", "nearing deal", "consider sale", "proposal", 
            "proposal to acquire", "non binding offer", "exploring sale", "including sale", "exploring option", "in talks", 
            "potential offer", "acquisition target", "buyout", "buyback", "consolidation", "joint venture", "investment", 
            "equity investment", "strategic partnership", "strategic alliance", "divestiture", "spin-off", "restructuring", 
            "capital infusion", "equity stake", "stake acquisition", "share purchase", "management buyout", 
            "leveraged buyout", "private equity", "recapitalization", "asset purchase", "friendly takeover", "hostile takeover", 
            "reverse merger", "merger proposal", "asset sale", "partnership deal", "equity transfer", "take-private deal", 
            "tender offer"
            ]

        # Initialize a list to store the filtered entries
        filtered_entries = []

        for entry in entries:
            title = entry.title.text
            summary = entry.description.text
            link = entry.link.text
            time = entry.pubDate.text

        # Check if any keyword is present in the title or summary
            if any(re.search(keyword, title.lower()) or re.search(keyword, summary.lower()) for keyword in keywords):
                filtered_entries.append({
                    'Title': title,
                    'Summary': summary,
                    'Link': link,
                    'Time': time
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
        else:
            # If the CSV file doesn't exist, the combined DataFrame is just the new DataFrame
            combined_df = new_df

        # Save the updated DataFrame back to the CSV file
        combined_df.to_csv(csv_file_path, index=False)

        # Print the updated DataFrame
        print(combined_df)
        
        i += 1

    t.sleep(10)
