import pandas as pd
import numpy as np
from geopy.distance import geodesic
import geopandas as gpd

# Load data
businesses = pd.read_csv('Data/csv_files/Hospitality_Disinvested_Atlanta_Business_License_Records_2025_no_dups.csv')
reviews = pd.read_csv('reviews_summary.csv')
ridership = pd.read_csv('Data/csv_files/MARTA_Bus_Ridership_2023_20250912.csv')

# Calculate average ridership per route
route_ridership = ridership.groupby('Route')['Total UPT'].mean().to_dict()

# Load real MARTA stops data
marta_stops = gpd.read_file('Data/MARTA_Stops_Shapefiles/MARTA_Stops.shp')
marta_stops['stop_lat'] = marta_stops.geometry.y
marta_stops['stop_lon'] = marta_stops.geometry.x

def calculate_marta_density(lat, lon):
    """Calculate distance to nearest MARTA stop and get ridership density"""
    if pd.isna(lat) or pd.isna(lon):
        return 0
    
    min_distance = float('inf')
    nearest_stop_id = None
    
    for _, stop in marta_stops.iterrows():
        distance = geodesic((lat, lon), (stop['stop_lat'], stop['stop_lon'])).meters
        if distance < min_distance:
            min_distance = distance
            nearest_stop_id = stop['stop_id']
    
    # Use average ridership since we don't have route mapping for all stops
    stop_ridership = np.mean(list(route_ridership.values())) if route_ridership else 5000
    
    # Density score: higher ridership / shorter distance = higher score
    if min_distance > 0:
        density_score = (stop_ridership / min_distance) * 1000  # Scale factor
    else:
        density_score = stop_ridership
    
    return density_score

def calculate_user_rating_score(rating, total_ratings):
    """Calculate weighted rating score"""
    if pd.isna(rating) or pd.isna(total_ratings) or total_ratings == 0:
        return 0
    
    # Weighted score: rating with modest boost for review volume
    return rating * (1 + np.log10(total_ratings + 1) * 0.1)

# Merge business data with reviews
merged_data = businesses.merge(reviews, left_on='company_dba', right_on='company_name', how='left')

# Calculate MARTA density scores
print("Calculating MARTA density scores...")
merged_data['marta_density_score'] = merged_data.apply(
    lambda row: calculate_marta_density(row['latitude'], row['longitude']), axis=1
)

# Calculate user rating scores
print("Calculating user rating scores...")
merged_data['user_rating_score'] = merged_data.apply(
    lambda row: calculate_user_rating_score(row['rating'], row['total_ratings']), axis=1
)

# Normalize scores to 0-1 range
merged_data['marta_density_norm'] = (merged_data['marta_density_score'] - merged_data['marta_density_score'].min()) / (merged_data['marta_density_score'].max() - merged_data['marta_density_score'].min())
merged_data['user_rating_norm'] = (merged_data['user_rating_score'] - merged_data['user_rating_score'].min()) / (merged_data['user_rating_score'].max() - merged_data['user_rating_score'].min())

# Calculate viability score (equal weighting)
merged_data['viability_score'] = (2* merged_data['marta_density_norm'] * merged_data['user_rating_norm']) / merged_data['marta_density_norm'] + merged_data['user_rating_norm']

# Select key columns for output
output_cols = ['company_dba', 'address_concat', 'latitude', 'longitude', 
               'rating', 'total_ratings', 'marta_density_score', 'user_rating_score', 'viability_score']

result = merged_data[output_cols].sort_values('viability_score', ascending=False)

# Save results
result.to_csv('business_viability_analysis.csv', index=False)

print(f"\nTop 10 businesses by viability score:")
print(result.head(10)[['company_dba', 'viability_score', 'rating', 'total_ratings']].to_string(index=False))

print(f"\nAnalysis complete. Results saved to 'business_viability_analysis.csv'")