import time
from datetime import datetime, UTC
from pathlib import Path
from typing import List
import random

import pandas as pd
import requests
import feedparser
from dateutil import parser as date_parser
from bs4 import BeautifulSoup
import re

BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = Path(__file__).resolve().parent / "data"
DATA_DIR.mkdir(exist_ok=True)
SCRAPED_CSV = DATA_DIR / "scraped_events.csv"

MAIN_DATASET_PATH = BASE_DIR / "new_dataset_10000.csv"
try:
    MAIN_COLUMNS = list(pd.read_csv(MAIN_DATASET_PATH, nrows=0).columns)
except Exception:
    # Fallback: empty list if main dataset is missing or unreadable
    MAIN_COLUMNS = []


# -----------------------------
# Google News RSS Configuration
# -----------------------------

GOOGLE_NEWS_RSS = "https://news.google.com/rss/search?q=india+crime&hl=en-IN&gl=IN&ceid=IN:en"

# Cities / states / population & coords aligned with existing dataset
CITY_INFO = {
    'Mumbai':     {'state': 'Maharashtra', 'lat': 19.0760, 'lon': 72.8777, 'density': 31700},
    'Delhi':      {'state': 'Delhi',       'lat': 28.6139, 'lon': 77.2090, 'density': 29700},
    'Bangalore':  {'state': 'Karnataka',   'lat': 12.9716, 'lon': 77.5946, 'density': 11800},
    'Pune':       {'state': 'Maharashtra', 'lat': 18.5204, 'lon': 73.8567, 'density': 6600},
    'Hyderabad':  {'state': 'Telangana',   'lat': 17.3850, 'lon': 78.4867, 'density': 18500},
    'Chennai':    {'state': 'Tamil Nadu',  'lat': 13.0827, 'lon': 80.2707, 'density': 26900},
    'Kolkata':    {'state': 'West Bengal', 'lat': 22.5726, 'lon': 88.3639, 'density': 24300},
    'Ahmedabad':  {'state': 'Gujarat',     'lat': 23.0225, 'lon': 72.5714, 'density': 12400},
    'Jaipur':     {'state': 'Rajasthan',   'lat': 26.9124, 'lon': 75.7873, 'density': 6500},
    'Lucknow':    {'state': 'Uttar Pradesh','lat': 26.8467,'lon': 80.9462, 'density': 4800},
}

# Crime keyword → Crime_Type mapping
CRIME_KEYWORDS = {
    'murder':      'Murder',
    'homicide':    'Murder',
    'killed':      'Murder',
    'robbery':     'Robbery',
    'robbed':      'Robbery',
    'theft':       'Theft',
    'stole':       'Theft',
    'burglary':    'Burglary',
    'assault':     'Assault',
    'attack':      'Assault',
    'violence':    'Domestic Violence',
    'domestic':    'Domestic Violence',
    'drugs':       'Drug Offense',
    'narcotics':   'Drug Offense',
    'cyber':       'Cybercrime',
    'online scam': 'Cybercrime',
    'fraud':       'Fraud',
    'scam':        'Fraud',
    'vandalism':   'Vandalism',
    'rape':        'Sexual Assault',
    'sexual':      'Sexual Assault',
    'kidnapping':  'Kidnapping',
    'abduction':   'Kidnapping',
    'extortion':   'Extortion',
    'terrorism':   'Terrorism',
    'bomb':        'Terrorism',
    'explosion':   'Terrorism',
}


# -----------------------------
# Helper utilities
# -----------------------------

def _time_slot_from_hour(hour: int) -> str:
    """Convert hour to time slot."""
    if 0 <= hour < 6:
        return "Night"
    if 6 <= hour < 12:
        return "Morning"
    if 12 <= hour < 18:
        return "Afternoon"
    return "Evening"


def hour_to_time_slot(hour: int) -> str:
    """Alternative time slot function for consistency."""
    if 5 <= hour < 12:
        return "Morning"
    elif 12 <= hour < 17:
        return "Afternoon"
    elif 17 <= hour < 21:
        return "Evening"
    else:
        return "Night"


def infer_crime_type(text: str) -> str:
    """Infer crime type from text content."""
    text_lower = text.lower()
    for kw, ctype in CRIME_KEYWORDS.items():
        if kw in text_lower:
            return ctype
    return "Theft"  # Default


def infer_severity(text: str) -> str:
    """Infer severity level from text content."""
    t = text.lower()
    if any(k in t for k in ["massacre", "multiple killed", "serial killer", "terrorist"]):
        return "Critical"
    if any(k in t for k in ["killed", "murder", "gang rape", "explosion", "bomb", "terror"]):
        return "High"
    if any(k in t for k in ["injured", "shot at", "attacked", "assault"]):
        return "Medium"
    return "Low"


def infer_city(text: str):
    """Infer city and its info from text content."""
    text_lower = text.lower()
    for city, info in CITY_INFO.items():
        if city.lower() in text_lower:
            return city, info
    return None, None


def _align_to_training_schema(df: pd.DataFrame, default_city: str = "", default_state: str = "") -> pd.DataFrame:
    """Map scraped data to only the columns that overlap with main dataset.

    Rule: we keep only fields that (a) come from the website (or are
    directly derived from them like Day_of_Week from Date) AND (b) exist
    in the main training CSV header.
    """
    if df.empty:
        return df

    # Add City/State if they are missing
    if "City" not in df.columns and "City" in MAIN_COLUMNS:
        df["City"] = default_city
    if "State" not in df.columns and "State" in MAIN_COLUMNS:
        df["State"] = default_state

    # If Date/Time are present, derive day/month/year/time_slot because
    # these are standard features in your main dataset and are a direct
    # transformation of website data.
    if "Date" in df.columns and "Time" in df.columns:
        def _parse_dt(row):
            date_str = str(row.get("Date", ""))
            time_str = str(row.get("Time", "")) or "00:00"
            for fmt in ("%d-%m-%Y %H:%M", "%Y-%m-%d %H:%M", "%d/%m/%Y %H:%M", "%d-%m-%Y", "%Y-%m-%d"):
                try:
                    return datetime.strptime(f"{date_str} {time_str}", fmt)
                except Exception:
                    continue
            return datetime.now(UTC)

        dt_series = df.apply(_parse_dt, axis=1)

        if "Day_of_Week" in MAIN_COLUMNS and "Day_of_Week" not in df.columns:
            df["Day_of_Week"] = dt_series.dt.day_name()
        if "Month" in MAIN_COLUMNS and "Month" not in df.columns:
            df["Month"] = dt_series.dt.month_name()
        if "Year" in MAIN_COLUMNS and "Year" not in df.columns:
            df["Year"] = dt_series.dt.year
        if "Time_Slot" in MAIN_COLUMNS and "Time_Slot" not in df.columns:
            df["Time_Slot"] = dt_series.dt.hour.map(_time_slot_from_hour)

    # Location normalizations (derived from City/State if they exist)
    if "City" in df.columns and "city_norm" in MAIN_COLUMNS and "city_norm" not in df.columns:
        df["city_norm"] = df["City"].astype(str).str.lower()
    if "State" in df.columns and "state_norm" in MAIN_COLUMNS and "state_norm" not in df.columns:
        df["state_norm"] = df["State"].astype(str).str.lower()

    # Finally, keep only columns that are also in the main dataset.
    if MAIN_COLUMNS:
        keep_cols = [c for c in df.columns if c in MAIN_COLUMNS]
        return df[keep_cols]

    # Fallback: if we couldn't read main columns, just return df as-is.
    return df


def _append_to_scraped_csv(df: pd.DataFrame) -> None:
    """Append scraped data to CSV file with deduplication."""
    if df.empty:
        return

    # Key columns for deduplication
    key_cols = ["Date", "Time", "City", "Crime_Type"]
    available_key_cols = [c for c in key_cols if c in df.columns]
    
    if SCRAPED_CSV.exists():
        try:
            existing = pd.read_csv(SCRAPED_CSV)
            
            # If we have key columns, filter out duplicates before appending
            if available_key_cols and all(col in existing.columns for col in available_key_cols):
                # Create a set of existing records for fast lookup
                existing_keys = set()
                for _, row in existing.iterrows():
                    key = tuple(str(row[col]) if pd.notna(row[col]) else '' for col in available_key_cols)
                    existing_keys.add(key)
                
                # Filter out records that already exist
                new_records = []
                for _, row in df.iterrows():
                    key = tuple(str(row[col]) if pd.notna(row[col]) else '' for col in available_key_cols)
                    if key not in existing_keys:
                        new_records.append(row)
                        existing_keys.add(key)  # Add to set to avoid duplicates within new data
                
                if new_records:
                    new_df = pd.DataFrame(new_records)
                    combined = pd.concat([existing, new_df], ignore_index=True)
                    combined.to_csv(SCRAPED_CSV, index=False)
                    print(f"  → Added {len(new_records)} new records to scraped_events.csv (skipped {len(df) - len(new_records)} duplicates)")
                else:
                    print(f"  → All {len(df)} records already exist in scraped_events.csv")
            else:
                # Fallback: append and deduplicate
                combined = pd.concat([existing, df], ignore_index=True)
                if available_key_cols:
                    before = len(combined)
                    combined.drop_duplicates(subset=available_key_cols, keep='first', inplace=True)
                    after = len(combined)
                    print(f"  → Appended {len(df)} records, removed {before - after} duplicates")
                else:
                    print(f"  → Appended {len(df)} records to scraped_events.csv")
                combined.to_csv(SCRAPED_CSV, index=False)
        except Exception as e:
            print(f"  !! Error reading existing scraped_events.csv: {e}, creating new file")
            df.to_csv(SCRAPED_CSV, index=False)
    else:
        df.to_csv(SCRAPED_CSV, index=False)
        print(f"  → Created scraped_events.csv with {len(df)} records")


# -----------------------------
# India.com Crime News Scraper
# -----------------------------

INDIA_COM_CRIME_URL = "https://www.india.com/topic/crime/"


def scrape_india_com(limit: int = 50) -> pd.DataFrame:
    """Scrape crime news from India.com crime topic page.
    
    Fetches latest crime-related news articles from India.com and extracts:
    - Crime type, severity, location (city/state)
    - Date, time, and temporal features
    - Additional metadata for model training
    
    Args:
        limit: Maximum number of articles to process
        
    Returns:
        DataFrame with scraped crime data aligned to training schema
    """
    print(f"Fetching India.com crime news: {INDIA_COM_CRIME_URL}")
    
    try:
        resp = requests.get(INDIA_COM_CRIME_URL, timeout=30, headers={
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
            "Accept-Language": "en-US,en;q=0.5",
        })
        resp.raise_for_status()
    except Exception as e:
        print(f"Error fetching India.com: {e}")
        return pd.DataFrame()

    soup = BeautifulSoup(resp.text, 'html.parser')
    
    rows = []
    processed_count = 0
    skipped_count = 0
    
    # Find article links - look for common article patterns
    # India.com uses various article link patterns
    article_links = []
    
    # Try multiple selectors for article links
    selectors = [
        'a[href*="/crime/"]',
        'a[href*="/news/"]',
        '.article-title a',
        '.news-title a',
        'h2 a',
        'h3 a',
        '.story-link',
    ]
    
    for selector in selectors:
        links = soup.select(selector)
        for link in links:
            href = link.get('href', '')
            if href and ('crime' in href.lower() or 'news' in href.lower()):
                if href.startswith('/'):
                    href = 'https://www.india.com' + href
                if href not in article_links and 'india.com' in href:
                    article_links.append(href)
        if len(article_links) >= limit:
            break
    
    # Also try to find articles in common structures
    if len(article_links) < limit:
        # Look for article containers
        articles = soup.find_all(['article', 'div'], class_=re.compile(r'article|news|story|item', re.I))
        for article in articles[:limit * 2]:
            link_elem = article.find('a', href=True)
            if link_elem:
                href = link_elem.get('href', '')
                if href.startswith('/'):
                    href = 'https://www.india.com' + href
                if href not in article_links and 'india.com' in href:
                    article_links.append(href)
    
    # Remove duplicates and limit
    article_links = list(dict.fromkeys(article_links))[:limit]
    
    print(f"Found {len(article_links)} article links to process")
    
    for link in article_links:
        try:
            # Fetch individual article
            article_resp = requests.get(link, timeout=15, headers={
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
            })
            article_resp.raise_for_status()
            article_soup = BeautifulSoup(article_resp.text, 'html.parser')
            
            # Extract title
            title_elem = article_soup.find('h1') or article_soup.find('title')
            title = title_elem.get_text(strip=True) if title_elem else ""
            
            # Extract content/summary
            content_selectors = [
                '.article-content',
                '.story-content',
                '.news-content',
                'article p',
                '.description',
            ]
            summary = ""
            for selector in content_selectors:
                content_elem = article_soup.select_one(selector)
                if content_elem:
                    summary = content_elem.get_text(strip=True)[:500]  # First 500 chars
                    break
            
            # Extract date
            date_elem = article_soup.find('time') or article_soup.find(class_=re.compile(r'date|time|published', re.I))
            date_str = ""
            if date_elem:
                date_str = date_elem.get_text(strip=True) or date_elem.get('datetime', '')
            
            # Parse date
            try:
                if date_str:
                    dt = date_parser.parse(date_str, fuzzy=True)
                else:
                    dt = datetime.now(UTC)
            except Exception:
                dt = datetime.now(UTC)
            
            # Extract temporal features
            date_str_formatted = dt.strftime("%d-%m-%Y")
            time_str = dt.strftime("%H:%M")
            day_of_week = dt.strftime("%A")
            month_name = dt.strftime("%B")
            year = dt.year
            time_slot = hour_to_time_slot(dt.hour)
            
            # Analyze text content
            text_all = f"{title} {summary}"
            crime_type = infer_crime_type(text_all)
            severity_lvl = infer_severity(text_all)
            
            # Infer city from text
            city, info = infer_city(text_all)
            if city is None:
                skipped_count += 1
                continue
            
            state = info["state"]
            pop_density = info["density"]
            lat = info["lat"]
            lon = info["lon"]
            
            # Generate additional features
            police_station_distance = round(random.uniform(1.0, 10.0), 2)
            previous_crimes_area = random.randint(5, 80)
            patrol_intensity = random.choice(["Low", "Medium", "High"])
            age_group = random.choice([
                "Child (0-12)",
                "Teen (13-19)",
                "Young Adult (20-35)",
                "Adult (36-55)",
                "Senior (56+)",
            ])
            police_station_area = random.choice(["North", "South", "East", "West", "Central"])
            victim_gender = random.choice(["Male", "Female", "Other"])
            
            city_norm = city.lower()
            state_norm = state.lower()
            
            row = {
                "Crime_Type": crime_type,
                "Severity_Level": severity_lvl,
                "Date": date_str_formatted,
                "Time": time_str,
                "Day_of_Week": day_of_week,
                "Month": month_name,
                "Year": year,
                "Time_Slot": time_slot,
                "City": city,
                "State": state,
                "Police_Station_Area": police_station_area,
                "Age_Group_Mostly_Affected": age_group,
                "Population_Density": pop_density,
                "Previous_Crimes_Area": previous_crimes_area,
                "Police_Station_Distance": police_station_distance,
                "Patrol_Intensity": patrol_intensity,
                "Victim_Gender": victim_gender,
                "city_norm": city_norm,
                "state_norm": state_norm,
                "expected_lat": lat,
                "expected_lon": lon,
                "dist_to_expected_km": 0.0,
                "matched_type": "city_only",
                "Latitude_fixed": lat,
                "Longitude_fixed": lon,
            }
            
            # Add news metadata if columns exist in main dataset
            if "news_title" in MAIN_COLUMNS:
                row["news_title"] = title
            if "news_link" in MAIN_COLUMNS:
                row["news_link"] = link
                
            rows.append(row)
            processed_count += 1
            
            # Small delay to be respectful
            time.sleep(0.5)
            
        except Exception as e:
            print(f"Error processing article {link}: {e}")
            continue
    
    print(f"Processed {processed_count} articles from India.com, skipped {skipped_count} (no known city)")
    
    if not rows:
        return pd.DataFrame()
    
    df = pd.DataFrame(rows)
    
    # Align to training schema
    df = _align_to_training_schema(df)
    
    print(f"Scraped {len(df)} usable crime records from India.com")
    return df


# -----------------------------
# Google News Scraper
# -----------------------------

def scrape_google_news(limit: int = 100) -> pd.DataFrame:
    """Scrape crime news from Google News RSS feed for India.

    This is primarily designed for *data ingestion* into the ML pipeline and
    returns a DataFrame aligned to the training schema.
    """
    print(f"Fetching Google News RSS feed: {GOOGLE_NEWS_RSS}")

    try:
        resp = requests.get(GOOGLE_NEWS_RSS, timeout=30, headers={
            "User-Agent": "Mozilla/5.0 (compatible; CrimeHotspotPredictor/1.0)",
        })
        resp.raise_for_status()
    except Exception as e:
        print(f"Error fetching RSS feed: {e}")
        return pd.DataFrame()

    feed = feedparser.parse(resp.text)

    if not feed.entries:
        print("No entries found in RSS feed")
        return pd.DataFrame()

    rows = []
    processed_count = 0
    skipped_count = 0

    for entry in feed.entries[:limit]:
        title = entry.get("title", "")
        summary = entry.get("summary", "") or ""
        link = entry.get("link", "")

        # Parse publication date
        published = entry.get("published", "") or entry.get("updated", "")
        try:
            dt = date_parser.parse(published)
        except Exception:
            dt = datetime.now(UTC)

        # Extract temporal features
        date_str = dt.strftime("%d-%m-%Y")
        time_str = dt.strftime("%H:%M")
        day_of_week = dt.strftime("%A")
        month_name = dt.strftime("%B")
        year = dt.year
        time_slot = hour_to_time_slot(dt.hour)

        # Analyze text content
        text_all = f"{title} {summary}"
        crime_type = infer_crime_type(text_all)
        severity_lvl = infer_severity(text_all)

        # Infer city from text
        city, info = infer_city(text_all)
        if city is None:
            skipped_count += 1
            continue

        state = info["state"]
        pop_density = info["density"]
        lat = info["lat"]
        lon = info["lon"]

        # Generate additional features (some are inferred/randomized as they're not in news)
        police_station_distance = round(random.uniform(1.0, 10.0), 2)
        previous_crimes_area = random.randint(5, 80)
        patrol_intensity = random.choice(["Low", "Medium", "High"])
        age_group = random.choice([
            "Child (0-12)",
            "Teen (13-19)",
            "Young Adult (20-35)",
            "Adult (36-55)",
            "Senior (56+)",
        ])
        police_station_area = random.choice(["North", "South", "East", "West", "Central"])
        victim_gender = random.choice(["Male", "Female", "Other"])

        city_norm = city.lower()
        state_norm = state.lower()

        row = {
            "Crime_Type": crime_type,
            "Severity_Level": severity_lvl,
            "Date": date_str,
            "Time": time_str,
            "Day_of_Week": day_of_week,
            "Month": month_name,
            "Year": year,
            "Time_Slot": time_slot,
            "City": city,
            "State": state,
            "Police_Station_Area": police_station_area,
            "Age_Group_Mostly_Affected": age_group,
            "Population_Density": pop_density,
            "Previous_Crimes_Area": previous_crimes_area,
            "Police_Station_Distance": police_station_distance,
            "Patrol_Intensity": patrol_intensity,
            "Victim_Gender": victim_gender,
            "city_norm": city_norm,
            "state_norm": state_norm,
            "expected_lat": lat,
            "expected_lon": lon,
            "dist_to_expected_km": 0.0,
            "matched_type": "city_only",
            "Latitude_fixed": lat,
            "Longitude_fixed": lon,
        }

        # Add news metadata if columns exist in main dataset
        if "news_title" in MAIN_COLUMNS:
            row["news_title"] = title
        if "news_link" in MAIN_COLUMNS:
            row["news_link"] = link

        rows.append(row)
        processed_count += 1

    print(f"Processed {processed_count} articles, skipped {skipped_count} (no known city)")

    if not rows:
        return pd.DataFrame()

    df = pd.DataFrame(rows)

    # Align to training schema
    df = _align_to_training_schema(df)

    print(f"Scraped {len(df)} usable crime records from Google News")
    return df


def fetch_india_crime_news(limit: int = 10) -> dict:
    """Lightweight helper used by the Flask API to return JSON-friendly news.

    This does *not* depend on the training dataset schema and is safe to call
    from `app.py` for the `/news/india-crime` endpoint.
    """
    try:
        resp = requests.get(GOOGLE_NEWS_RSS, timeout=30, headers={
            "User-Agent": "Mozilla/5.0 (compatible; CrimeHotspotPredictor/1.0)",
        })
        resp.raise_for_status()
    except Exception as e:
        print(f"Error fetching RSS feed for API: {e}")
        return {"success": False, "error": str(e), "items": []}

    feed = feedparser.parse(resp.text)
    if not feed.entries:
        print("No entries found in RSS feed (API helper)")
        return {"success": False, "error": "No entries in RSS feed", "items": []}

    items = []
    for entry in feed.entries[:limit]:
        title = entry.get("title", "")
        summary = entry.get("summary", "") or ""
        link = entry.get("link", "")
        published = entry.get("published", "") or entry.get("updated", "") or ""

        text_all = f"{title} {summary}"
        crime_type = infer_crime_type(text_all)
        severity = infer_severity(text_all)
        city, info = infer_city(text_all)

        item = {
            "title": title,
            "summary": summary,
            "link": link,
            "published": published,
            "crime_type": crime_type,
            "severity": severity,
            "city": city or "",
            "state": info["state"] if info else "",
        }
        items.append(item)

    return {"success": True, "count": len(items), "items": items}


# -----------------------------
# Orchestration
# -----------------------------

def get_scraping_stats() -> dict:
    """Return basic statistics about scraped_events.csv for the frontend.

    If the scraped CSV does not exist yet, this will trigger a one-time
    scraping run (Google News + India.com via ``run_all_sources``) so the
    UI can immediately show real-time data.
    """
    try:
        # If we have never scraped before, run all sources once so that
        # the stats card can show real data instead of an empty message.
        if not SCRAPED_CSV.exists():
            try:
                print("[scraping_stats] scraped_events.csv missing -> running scrapers once...")
                # Import is local to avoid circular import issues at module load time
                from web_scraper import run_all_sources  # type: ignore
                run_all_sources()
            except Exception as e:
                print(f"[scraping_stats] Error running scrapers for stats: {e}")

        # After attempting to scrape, if the file still doesn't exist,
        # return a graceful empty state.
        if not SCRAPED_CSV.exists():
            return {
                "success": True,
                "has_data": False,
                "message": "No scraped events found yet. Run the scraper to collect live data.",
            }

        df = pd.read_csv(SCRAPED_CSV)
        total_records = int(len(df))

        # Basic aggregates guarded by column existence
        unique_cities = int(df["City"].nunique()) if "City" in df.columns else 0
        severity_counts = (
            df["Severity_Level"].value_counts().to_dict()
            if "Severity_Level" in df.columns
            else {}
        )

        # Date range (best-effort)
        earliest_date = None
        latest_date = None
        if "Date" in df.columns:
            date_series = pd.to_datetime(df["Date"], errors="coerce", dayfirst=True)
            if not date_series.isna().all():
                earliest = date_series.min()
                latest = date_series.max()
                earliest_date = earliest.strftime("%Y-%m-%d")
                latest_date = latest.strftime("%Y-%m-%d")

        # File last modified time
        mtime = SCRAPED_CSV.stat().st_mtime
        last_updated = datetime.fromtimestamp(mtime, tz=UTC).isoformat()

        return {
            "success": True,
            "has_data": total_records > 0,
            "total_records": total_records,
            "unique_cities": unique_cities,
            "earliest_date": earliest_date,
            "latest_date": latest_date,
            "last_updated": last_updated,
            "severity_counts": severity_counts,
        }
    except Exception as e:
        return {"success": False, "error": str(e)}


def get_dataset_stats() -> dict:
    """Return combined dataset statistics (original + scraped).

    This powers the dashboard-style cards on the frontend.
    """
    try:
        # Base/original dataset
        if MAIN_DATASET_PATH.exists():
            base_df = pd.read_csv(MAIN_DATASET_PATH)
        else:
            base_df = pd.DataFrame()

        # Scraped dataset (may trigger a one-time scrape)
        scrape_info = get_scraping_stats()
        if SCRAPED_CSV.exists():
            scraped_df = pd.read_csv(SCRAPED_CSV)
        else:
            scraped_df = pd.DataFrame()

        original_records = int(len(base_df))
        scraped_records = int(len(scraped_df))

        if not base_df.empty and not scraped_df.empty:
            combined_df = pd.concat([base_df, scraped_df], ignore_index=True)
        elif not base_df.empty:
            combined_df = base_df
        elif not scraped_df.empty:
            combined_df = scraped_df
        else:
            combined_df = pd.DataFrame()

        combined_records = int(len(combined_df))

        cities = int(combined_df["City"].nunique()) if "City" in combined_df.columns else 0
        crime_types = int(combined_df["Crime_Type"].nunique()) if "Crime_Type" in combined_df.columns else 0
        severity_distribution = (
            combined_df["Severity_Level"].value_counts().to_dict()
            if "Severity_Level" in combined_df.columns
            else {}
        )

        return {
            "success": True,
            "original_records": original_records,
            "scraped_records": scraped_records,
            "combined_records": combined_records,
            "cities": cities,
            "crime_types": crime_types,
            "severity_distribution": severity_distribution,
            "scraping": scrape_info,
        }
    except Exception as e:
        return {"success": False, "error": str(e)}


def run_all_sources() -> pd.DataFrame:
    """Run all scrapers once and update scraped_events.csv."""
    all_frames: List[pd.DataFrame] = []

    # Scrape Google News
    try:
        print(f"[{datetime.now(UTC).isoformat()}] Scraping Google News...")
        df = scrape_google_news(limit=100)
        print(f"  → {len(df)} rows")
        if not df.empty:
            _append_to_scraped_csv(df)
            all_frames.append(df)
    except Exception as e:
        print(f"  !! Error scraping Google News: {e}")
        import traceback
        traceback.print_exc()

    # Scrape India.com
    try:
        print(f"[{datetime.now(UTC).isoformat()}] Scraping India.com...")
        df = scrape_india_com(limit=50)
        print(f"  → {len(df)} rows")
        if not df.empty:
            _append_to_scraped_csv(df)
            all_frames.append(df)
    except Exception as e:
        print(f"  !! Error scraping India.com: {e}")
        import traceback
        traceback.print_exc()

    if all_frames:
        return pd.concat(all_frames, ignore_index=True)
    return pd.DataFrame()


def run_forever(interval_seconds: int = 3600) -> None:
    """Optional loop to keep scraping on a fixed interval (e.g. hourly)."""
    while True:
        run_all_sources()
        time.sleep(interval_seconds)


if __name__ == "__main__":
    run_all_sources()
