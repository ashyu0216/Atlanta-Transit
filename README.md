# Atlanta Mega-Event Economic & Transit Impact Analysis

A data analytics project conducted in partnership with **Invest Atlanta** through the AI.Data Lab 2025 program. This project analyzes how Atlanta's upcoming mega-events — the **2026 FIFA World Cup**, **2028 Super Bowl**, and NCAA championships — can benefit local businesses in historically disinvested neighborhoods, not just large franchises.

---

## Research Question

> How can Atlanta maximize the positive economic impacts of upcoming mega-events while ensuring local businesses, especially in disinvested neighborhoods, benefit alongside major franchises?

---

## Project Overview

Atlanta is set to host millions of visitors over the next several years. This project identifies which local hospitality businesses are best positioned to benefit from that surge, and where transit access gaps could limit their reach.

The analysis combines three data sources:
- **Google Places API** — customer ratings and reviews for 160,000+ Atlanta businesses
- **MARTA bus and rail ridership data (2023)** — transit stop locations and ridership patterns
- **ONE ATL Mobility Scores** — neighborhood-level mobility and accessibility scores

---

## Key Findings

- **273 hospitality businesses** identified in disinvested Atlanta neighborhoods
- Hospitality businesses and MARTA stops are **concentrated in central Atlanta**, giving those areas strong accessibility
- Disinvested neighborhoods on the **outskirts have fewer businesses and fewer transit stops**, limiting their ability to benefit from event-driven demand
- Several hospitality clusters in disinvested areas **lack convenient MARTA access**, reducing foot traffic and employee mobility
- Top-performing businesses were ranked using a **composite viability score**

---

## Methodology

### 1. Data Collection — Google Places API Scraper
A two-stage Python pipeline using the Google Places API:
1. **Text search** — finds each business by name and address
2. **Place details** — retrieves ratings, review count, and customer reviews

Outputs a deduplicated `reviews_summary.csv` and full `google_places_reviews.json`.

### 2. Transit Density Scoring
MARTA stop shapefiles and ONE ATL Mobility Scores were used to compute an **inverse-distance weighted transit density score** per business — higher scores indicate closer proximity to more transit stops.

### 3. Viability Scoring
A **composite viability score** combining:
- **Log-normalized user rating score** — based on Google rating × log(review count)
- **MARTA density score** — inverse-distance weighted transit accessibility

Businesses are ranked by this score to surface those best positioned to benefit from mega-event tourism.

---

## Repository Structure

```
├── google_places_scraper.py      # Google Places API pipeline (text search → place details)
├── google_reviews_scraper.py     # Lightweight web scraper (BeautifulSoup fallback)
├── requirements.txt              # Python dependencies
├── data/
│   ├── Atlanta_Business_License_Records_2025.xlsx   # Source business list
│   ├── MARTA_Bus_Ridership_2023.xlsx                # MARTA bus ridership
│   ├── MARTA_Train_Ridership_2023.xlsx              # MARTA rail ridership
│   ├── MARTA_Stops.*                                # Geospatial shapefiles
│   └── ONE_ATL_Mobility_Scores_by_NSA.*             # Neighborhood mobility scores
├── output/
│   ├── google_places_reviews.json    # Full review data per business
│   ├── reviews_summary.csv           # Ratings and review counts
│   └── business_viability_analysis.csv  # Final ranked businesses with scores
```

---

## Setup & Usage

### Requirements
```bash
pip install -r requirements.txt
```

Dependencies: `pandas`, `requests`, `beautifulsoup4`, `lxml`

### Running the Scraper
1. Obtain a **Google Places API key** from [Google Cloud Console](https://console.cloud.google.com/)
2. Add your key to `google_places_scraper.py`:
   ```python
   API_KEY = "YOUR_GOOGLE_PLACES_API_KEY"
   ```
3. Run:
   ```bash
   python google_places_scraper.py
   ```

Output files will be saved as `google_places_reviews.json` and `reviews_summary.csv`.

---

## Data Sources

| Dataset | Source | Description |
|---|---|---|
| Atlanta Business License Records 2025 | City of Atlanta | Licensed hospitality businesses |
| MARTA Bus & Rail Ridership 2023 | MARTA | Stop-level ridership data |
| MARTA Stops Shapefiles | MARTA | Geospatial stop locations |
| ONE ATL Mobility Scores | Invest Atlanta | Neighborhood mobility index by NSA |
| Google Places Reviews | Google Places API | Business ratings and customer reviews |

---

## Future Directions

- Expand analysis to include **retail and entertainment** sectors
- Incorporate **walking-distance or travel-time** measures between businesses and MARTA stops
- Compare business performance **before and after** major events to measure actual economic impact
- Integrate **population and income metrics** to locate the most underserved communities

---
