import os
import asyncio
import datetime
import json
import pandas as pd
from pydantic import BaseModel, Field
from google import genai
from google.genai import types
from dotenv import load_dotenv
from bs4 import BeautifulSoup
from playwright.async_api import async_playwright, BrowserContext, Error as PlaywrightError
from typing import List, Tuple, Dict, Any

load_dotenv() 
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY") 
client = genai.Client(api_key=GEMINI_API_KEY)

EventType = [
    "Sporting Event",
    "Concert/Music Festival",
    "Trade Show/Exhibition",
    "Traditional Festival"
]

class Holiday(BaseModel):
    """A single holiday from the web page text."""
    date: str = Field(
        description="The exact date of the holiday in YYYY-MM-DD format, which must match the target interval."
    )
    description: str = Field(
        description="Brief, descriptive name of the event."
    )

class HolidayList(BaseModel):
    """The root container for all extracted events."""
    holidays: list[Holiday] = Field(
        description="A list of all holidays found that occur on the target interval."
    )

class Event(BaseModel):
    """A single event extracted from the web page text."""
    date: str = Field(
        description="The exact dates of the event in YYYY-MM-DD format, which must match the target interval. If an event happens for a few days, you must create a new row for each days it takes place."
    )
    category: str = Field(
        description=f"The category of the event. Must be one of: {EventType}."
    )
    description: str = Field(
        description="Brief, descriptive name of the event."
    )
    barris: str = Field(
        description="The neighborhood where the event takes place. If the event takes place in several neighbourhoods concatenate neighbourhoods with '|'. Use 'all' if the event covers all neighborhoods in Barcelona."
    )
    impact: int = Field(
        description="""The estimated impact level of the event on the local area and/or city traffic/crowds, rated on a scale of 1 to 5:
    - **1:** Very Low (Minimal impact, small local gathering, no traffic disruption.)
    - **2:** Low (Minor event, regular small-scale event, very limited neighborhood-level disruption.)
    - **3:** Medium (Standard large event, such as a regular league match or concert, causing noticeable neighborhood-level traffic or crowd disruption.)
    - **4:** High (Major event, such as a high-profile European match, large conference, or significant festival, causing considerable disruption in a large area.)
    - **5:** Very High (Maximum impact, such as a 'Clásico' football match, a large city-wide festival, or an event causing massive, city-wide disruption or widespread traffic closure.)
    """
    )

class EventList(BaseModel):
    """The root container for all extracted events."""
    events: list[Event] = Field(
        description="A list of all events found that occur on the target interval."
    )

def extract_festius(text: str, today: datetime.date, end_date: datetime.date, more_info: str) -> list[dict]:
    """Extracts festius that happen within the date interval from the text using Gemini."""

    prompt = f"""You are an expert holidays data extraction system. Your task is to analyze the provided web page text and identify all events that occur within a specified time interval.
    **Target Interval:** You must extract ALL holidays that occur between the start date, **{today.strftime('%Y-%m-%d')}**, and the end date, **{end_date.strftime('%Y-%m-%d')}**, inclusive.
        **Exclusions:** You must ignore any events that fall outside of this interval.
    **URL-SPECIFIC EXTRACTION INSTRUCTIONS:** {more_info}
    **WEB PAGE TEXT:**
    {text}"""
    
    config = types.GenerateContentConfig(
        response_mime_type="application/json",
        response_schema=HolidayList,
    )

    try:
        response = client.models.generate_content(
            model='gemini-2.5-flash',
            contents=prompt,
            config=config
        )
        data_dict = json.loads(response.text)
        return data_dict.get('holidays', [])
    
    except (json.JSONDecodeError, Exception) as e:
        print(f"--- Warning: LLM (Festius) extraction failed. Error: {e} ---")
        return []

def extract_events(text: str, today: datetime.date, end_date: datetime.date, more_info: str) -> list[dict]:
    """Extracts events that happen within the date interval from the text using Gemini."""

    prompt = f"""You are an expert event data extraction system. Your task is to analyze the provided web page text and identify all events that occur within a specified time interval.

    Strictly adhere to the following rules:
    1.  **Target Interval:** You must extract ALL events that occur between the start date, **{today.strftime('%Y-%m-%d')}**, and the end date, **{end_date.strftime('%Y-%m-%d')}**, inclusive.
        * **Inference:** You must use your natural language understanding to correctly parse dates, regardless of the text format (e.g., '25 de septiembre', 'tomorrow', 'next week').
        * **Exclusions:** You must ignore any events that fall outside of this interval.
    2.  **Event Date Field:** For the 'event_date' field in the JSON, you MUST convert the date you find to the standard **YYYY-MM-DD** format.
    3.  **Output Format:** Return the results as a JSON array strictly conforming to the provided schema.
    4.  **Neighborhood:** You must return valid official Barcelona neighbourhood names, not district names. If the event takes place in several neighbourhoods, concatenate neighbourhood names with '|'. If the event occurs across all neighborhoods in Barcelona, set the value for 'neighborhood' to 'all'.
    5.  **Event Type:** Categorize the event into one of the following official types: {EventType}.
    6.  **Impact Score:** Use the following scale to determine the integer value for the 'impact' field:
        * 1: Very Low (Minimal impact, no traffic disruption.)
        * 2: Low (Minor event, limited neighborhood disruption.)
        * 3: Medium (Standard large event, noticeable neighborhood traffic/crowd disruption.)
        * 4: High (Major event, considerable disruption in a large area.)
        * 5: Very High (Maximum impact, massive, city-wide disruption.)
    **URL-SPECIFIC EXTRACTION INSTRUCTIONS:** {more_info}

    **WEB PAGE TEXT:**
    {text}"""
    
    config = types.GenerateContentConfig(
        response_mime_type="application/json",
        response_schema=EventList,
    )

    try:
        response = client.models.generate_content(
            model='gemini-2.5-flash',
            contents=prompt,
            config=config
        )
        data_dict = json.loads(response.text)
        return data_dict.get('events', [])
    
    except (json.JSONDecodeError, Exception) as e:
        print(f"--- Warning: LLM (Events) extraction failed. Error: {e} ---")
        return []

async def scrape_web_with_context(context: BrowserContext, url: str) -> str:
    """
    Uses an existing browser context to scrape a single URL and clean the HTML.
    Includes special handling for highly dynamic sites like Primavera Sound.
    """
    
    page = await context.new_page()
    print(f"Navigating to {url}...")
    
    try:
        await page.goto(url, wait_until="domcontentloaded", timeout=30000) # Aumentar a 60s

        if "primaverasound.com" in url:     # This url gave anti-bot problems so perform human like behaviour
            content_selector = "body" 
            print(f"Aplicando espera Cloudflare/SPA para {url}...")
            await asyncio.sleep(5) 
            await page.mouse.wheel(0, 500) # Desplazarse 500 píxeles hacia abajo
            await asyncio.sleep(1) # Espera post-scroll
            await page.wait_for_selector(content_selector, state="visible", timeout=30000)
            await asyncio.sleep(2) 
        
        else:
            await asyncio.sleep(2) 

        raw_html = await page.content() # Scrape content
        
    except PlaywrightError as e:
        print(f"Playwright error on {url}: {e}")
        return ""
        
    finally:
        await page.close()

    print(f"Cleaning HTML content for {url}...")
    
    soup = BeautifulSoup(raw_html, 'html.parser')
    body_tag = soup.find('body')
         
    if not body_tag:
        return soup.get_text(separator=' ', strip=True) 

    unwanted_tags = [   # Remove everything with these tags for more efficient extraction
        "script", 
        "style", 
        "noscript", 
        "nav", 
        "footer", 
        "form", 
        "iframe"
    ]

    for element in body_tag.find_all(unwanted_tags):
        element.decompose()
        
    clean_content = body_tag.get_text(separator=' ', strip=True)
    return clean_content

async def scrape_and_extract_all(event_webs: List[str], festius_webs: List[str], more_info: Dict[str, str], today: datetime.date, end_date: datetime.date) -> Tuple[List[Dict[str, Any]], List[Dict[str, Any]]]:
    """
    Orchestrates browser launch and concurrently runs all scraping tasks.
    """
    all_urls = event_webs + festius_webs
    
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        print("Browser launched successfully.")
        
        context = await browser.new_context(    # Create context
            user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36',
            extra_http_headers={"Accept-Language": "en-US,en;q=0.9"},
            viewport={'width': 1280, 'height': 800}
        )
        
        all_scrape_tasks = []
        for url in all_urls:
            all_scrape_tasks.append(
                scrape_web_with_context(context, url)
            )

        scraped_texts = await asyncio.gather(*all_scrape_tasks) # Runs all tasks in list concurrently

        await browser.close()
        print("Scraping complete.")

        events_list = []
        festius_list = []
        
        for i, text in enumerate(scraped_texts):
            url = all_urls[i]
            url_specific_info = more_info.get(url, "No additional information") # Get added personalized info for url

            if text and text.strip():
                if url in event_webs:
                    url_events = extract_events(text, today, end_date, url_specific_info)
                    events_list.extend(url_events)
                elif url in festius_webs:
                    url_events = extract_festius(text, today, end_date, url_specific_info)
                    festius_list.extend(url_events)
            else:
                print(f"Skipping extraction for {url} due to empty or stripped content.")

        return events_list, festius_list

def scrape_week_ahead(end_date: datetime.date = None) -> Tuple[pd.DataFrame,pd.DataFrame]:
    """Returns two dataframes, one with events, the other with holidays. 
    Main function to orchestrate the scraping and extraction of events and holidays"""
    
    start_date = datetime.date.today()
    if end_date is None:
        day_interval = 7
        end_date = start_date + datetime.timedelta(days=day_interval)

    assert end_date >= start_date, "end_date must be later than today"

    event_webs = [
        "https://www.fcbarcelona.es/es/futbol/primer-equipo/calendario", 
        "https://estadiolimpic.barcelona/en/events", 
        "https://www.firabarcelona.com/es/calendario/",
        "https://www.primaverasound.com/en/home", 
        "https://sonar.es/es", 
        "https://www.cruillabarcelona.com/es/festival-cruilla/",
        "https://www.zurichmaratobarcelona.es/", 
        "https://cursaelcorteingles.cat/presentacio/", 
        "https://www.barcelona.cat/culturapopular/es/fiestas-y-tradiciones/sant-jordi",
        "https://www.barcelona.cat/es/vivir-en-bcn/diada", 
        "https://www.barcelona.cat/lamerce/es/preguntas-frecuentes"
    ]
                        
    more_info = {
        event_webs[0]: "Extract only home games played in Spotify Camp Nou. Spotify Camp Nou is in the 'les Corts' neighbourhood.",
        event_webs[1]: "All events from this text are in the 'el Poble-sec' neighbourhood.",
        event_webs[2]: "The venue Gran Via is in the 'la Marina del Prat Vermell' nighbourhood, the venue Montjuïc is located in 'el Poble-sec' neighbourhood and the venue CCIB is located in 'el Besòs i el Maresme' neighbourhood.",
        event_webs[3]: "Extract only 'Primavera Sound' music festival, no concerts. 'El Parc del Fòrum' is located in the 'el Besòs i el Maresme' neighbourhood.",
        event_webs[4]: "The Sonar Festival venue 'Fira Gran Via' is located in the 'la Marina de Port' neighbourhood.", 
        event_webs[5]: "The Cruïlla Festival venue 'El Parc del Fòrum' is located in the 'el Besòs i el Maresme' neighbourhood.", 
        event_webs[6]: "No additional information",
        event_webs[7]: "The El Corte Inglés Race runs through the 'les Corts', 'la Nova Esquerra de l'Eixample' and 'l'Antiga Esquerra de l'Eixample' neighbourhoods.", 
        event_webs[8]: "Sant Jordi is a Traditional Festival that covers 'all' neighborhoods.", 
        event_webs[9]: "Extract only the 'Manifestació' event that takes place on September 11th. Get all the neighbourhoods the 'Manifestació' goes through. Important, extract event if and only if 11th september (YYYY/09/11) is in the given date range.", 
        event_webs[10]: "La Mercè is a Traditional Festival that covers 'all' neighborhoods."
    }
    
    festius_webs = ["https://ajuntament.barcelona.cat/calendarifestius/ca/"]

    events_list, festius_list = asyncio.run(scrape_and_extract_all(event_webs, festius_webs, more_info, start_date, end_date))
    
    event_cols = ["date", "category", "description", "barris", "impact"]
    festius_cols = ["date", "description"]


    if events_list:
        df_events = pd.DataFrame(events_list)[event_cols] # Runs ONLY if list has data
    else:
        print("No events extracted.")
        df_events = pd.DataFrame(columns=event_cols) # Runs ONLY if list is empty

    if festius_list:
        df_festius = pd.DataFrame(festius_list)[festius_cols] # Runs ONLY if list has data
    else:
        print("No festius extracted.")
        df_festius = pd.DataFrame(columns=festius_cols) # Runs ONLY if list is empty

    print(df_events.to_markdown(index=False))
    print(df_festius.to_markdown(index=False))
    
    return df_events, df_festius
