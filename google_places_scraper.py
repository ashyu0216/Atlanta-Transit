import pandas as pd
import requests
import json
import time

class GooglePlacesReviewScraper:
    def __init__(self, api_key):
        self.api_key = api_key
        self.base_url = "https://maps.googleapis.com/maps/api/place"
    
    def search_place(self, company_name, address):
        """Search for place using Google Places API"""
        query = f"{company_name} {address}"
        url = f"{self.base_url}/textsearch/json"
        
        params = {
            'query': query,
            'key': self.api_key
        }
        
        response = requests.get(url, params=params)
        return response.json()
    
    def get_place_details(self, place_id):
        """Get detailed place information including reviews"""
        url = f"{self.base_url}/details/json"
        
        params = {
            'place_id': place_id,
            'fields': 'name,rating,user_ratings_total,reviews,formatted_address',
            'key': self.api_key
        }
        
        response = requests.get(url, params=params)
        return response.json()
    
    def scrape_reviews(self, company_name, address):
        """Main method to scrape reviews for a company"""
        try:
            # Search for the place
            search_result = self.search_place(company_name, address)
            
            if not search_result.get('results'):
                return {
                    'company_name': company_name,
                    'address': address,
                    'status': 'not_found'
                }
            
            place = search_result['results'][0]
            place_id = place['place_id']
            
            # Get detailed information
            details = self.get_place_details(place_id)
            
            if 'result' not in details:
                return {
                    'company_name': company_name,
                    'address': address,
                    'status': 'details_not_found'
                }
            
            result = details['result']
            
            return {
                'company_name': company_name,
                'google_name': result.get('name'),
                'address': address,
                'google_address': result.get('formatted_address'),
                'rating': result.get('rating'),
                'total_ratings': result.get('user_ratings_total'),
                'reviews': [
                    {
                        'author': review.get('author_name'),
                        'rating': review.get('rating'),
                        'text': review.get('text'),
                        'time': review.get('time')
                    }
                    for review in result.get('reviews', [])
                ],
                'status': 'success'
            }
            
        except Exception as e:
            return {
                'company_name': company_name,
                'address': address,
                'error': str(e),
                'status': 'error'
            }

def main():
    # You need to get a Google Places API key from Google Cloud Console
    API_KEY = "YOUR_GOOGLE_PLACES_API_KEY"  # Replace with your actual API key
    
    if API_KEY == "YOUR_GOOGLE_PLACES_API_KEY":
        print("Please set your Google Places API key in the script")
        return
    
    scraper = GooglePlacesReviewScraper(API_KEY)
    
    # Read CSV file
    df = pd.read_csv('Data/csv_files/Hospitality_Disinvested_Atlanta_Business_License_Records_2025_no_dups.csv')
    
    results = []
    
    for index, row in df.iterrows():
        company_name = row['company_dba'] if pd.notna(row['company_dba']) else row['company_name']
        address = row['address_api'] if pd.notna(row['address_api']) else row['address_concat']
        
        print(f"Scraping reviews for: {company_name}")
        
        review_data = scraper.scrape_reviews(company_name, address)
        results.append(review_data)
        
        # Rate limiting (Google Places API has quotas)
        time.sleep(1)
        
        # Process first 10 companies for testing
        if index % 9 == 0:
            print("Saved 10 companies")
            with open('google_places_reviews.json', 'a') as f:
                json.dump(results, f, indent=2)

    
    # Save results
    with open('google_places_reviews.json', 'w') as f:
        json.dump(results, f, indent=2)
    
    # Create summary CSV
    summary_data = []
    for result in results:
        summary_data.append({
            'company_name': result['company_name'],
            'google_name': result.get('google_name', ''),
            'rating': result.get('rating', ''),
            'total_ratings': result.get('total_ratings', ''),
            'review_count': len(result.get('reviews', [])),
            'status': result.get('status', '')
        })
    
    summary_df = pd.DataFrame(summary_data)
    summary_df.to_csv('reviews_summary.csv', index=False)
    
    print(f"Scraped {len(results)} companies.")
    print("Results saved to google_places_reviews.json and reviews_summary.csv")

if __name__ == "__main__":
    main()