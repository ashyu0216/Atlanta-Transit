import pandas as pd
import requests
from bs4 import BeautifulSoup
import time
import json
from urllib.parse import quote_plus

def search_google_reviews(company_name, address):
    """Search for Google reviews using company name and address"""
    try:
        # Create search query
        query = f"{company_name} {address} reviews"
        search_url = f"https://www.google.com/search?q={quote_plus(query)}"
        
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        
        response = requests.get(search_url, headers=headers)
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # Extract basic review info
        review_data = {
            'company_name': company_name,
            'address': address,
            'rating': None,
            'review_count': None,
            'reviews': []
        }
        
        # Look for rating
        rating_elem = soup.find('span', class_='Aq14fc')
        if rating_elem:
            review_data['rating'] = rating_elem.text.strip()
        
        # Look for review count
        count_elem = soup.find('span', string=lambda text: text and 'reviews' in text.lower())
        if count_elem:
            review_data['review_count'] = count_elem.text.strip()
        
        # Extract individual reviews
        review_elements = soup.find_all('div', class_='jftiEf')
        for elem in review_elements[:3]:  # Get first 3 reviews
            review_text = elem.find('span', class_='wiI7pd')
            if review_text:
                review_data['reviews'].append(review_text.text.strip())
        
        return review_data
        
    except Exception as e:
        return {
            'company_name': company_name,
            'address': address,
            'error': str(e)
        }

def main():
    # Read CSV file
    df = pd.read_csv('Data/csv_files/Hospitality_Disinvested_Atlanta_Business_License_Records_2025_no_dups.csv')
    
    results = []
    
    for index, row in df.iterrows():
        company_name = row['company_dba'] if pd.notna(row['company_dba']) else row['company_name']
        address = row['address_api'] if pd.notna(row['address_api']) else row['address_concat']
        
        print(f"Scraping reviews for: {company_name}")
        
        review_data = search_google_reviews(company_name, address)
        results.append(review_data)
        
        # Rate limiting
        time.sleep(2)
        
        # Stop after 5 companies for testing
        if index % 5 == 0:
            with open('google_reviews_data.json', 'a') as f:
                json.dump(results, f, indent=2)
    
    
    # Save results
    
    print(f"Scraped {len(results)} companies. Results saved to google_reviews_data.json")

if __name__ == "__main__":
    main()