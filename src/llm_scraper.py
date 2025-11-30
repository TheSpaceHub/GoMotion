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

load_dotenv() 
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY") 
client = genai.Client(api_key=GEMINI_API_KEY)

EventType = [
    "Sporting Event",
    "Concert/Music Festival",
    "Trade Show/Exhibition",
    "Traditional Festival"
]

class Event(BaseModel):
    """A single event extracted from the web page text."""
    
    event_date: str = Field(
        description="The exact dates of the event in YYYY-MM-DD format, which must match the target interval. If an event happens for a few days, you must create a new row for each days it takes place."
    )
    event_type: str = Field(
        description=f"The category of the event. Must be one of: {EventType}."
    )
    name_of_event: str = Field(
        description="The full, descriptive name of the event."
    )
    neighborhood: str = Field(
        description="The neighborhood where the event takes place. If the event takes place in several neighbourhoods concatenate neighbourhoods with '|'. Use 'all' if the event covers all neighborhoods in Barcelona."
    )

class EventList(BaseModel):
    """The root container for all extracted events."""
    events: list[Event] = Field(
        description="A list of all events found that occur on the target interval."
    )

def extract_events(text: str, today: datetime.date, end_date: datetime.date, more_info: str) -> list[dict]:
    """Extracts events that happen within the date interval from the text using Gemini."""

    prompt = f"""You are an expert event data extraction system. Your task is to analyze the provided web page text and identify all events that occur within a specified time interval.

    Strictly adhere to the following rules:
    1.  **Target Interval:** You must extract ALL events that occur between the start date, **{today.strftime('%Y-%m-%d')}**, and the end date, **{end_date.strftime('%Y-%m-%d')}**, inclusive.
        * **Inference:** You must use your natural language understanding to correctly parse dates, regardless of the text format (e.g., '25 de septiembre', 'tomorrow', 'next week').
        * **Exclusions:** Ignore any events that fall outside of this interval.
    2.  **Event Date Field:** For the 'event_date' field in the JSON, you MUST convert the date you find to the standard **YYYY-MM-DD** format.
    3.  **Output Format:** Return the results as a JSON array strictly conforming to the provided schema.
    4.  **Neighborhood:** You must return valid official Barcelona neighbourhood names, not district names. If the event takes place in several neighbourhoods, concatenate neighbourhood names with '|'. If the event occurs across all neighborhoods in Barcelona, set the value for 'neighborhood' to 'all'.
    5.  **Event Type:** Categorize the event into one of the following official types: {EventType}.

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
        print(f"--- Warning: LLM extraction failed. Error: {e} ---")
        return []
    
async def scrape_web_with_context(context: BrowserContext, url: str) -> str:
    """Uses an existing browser context to scrape a single URL and clean the HTML."""
    
    page = await context.new_page()
    print(f"Navigating to {url}...")
    
    try:
        await page.goto(url, wait_until="domcontentloaded") 
        await asyncio.sleep(2) 
        raw_html = await page.content()
        
    except PlaywrightError as e:
        print(f"Playwright error on {url}: {e}")
        return ""
        
    finally:
        await page.close()

    print("Cleaning HTML content...")
    
    soup = BeautifulSoup(raw_html, 'html.parser')
    body_tag = soup.find('body')

    if not body_tag:
        return soup.get_text(separator=' ', strip=True) 

    unwanted_tags = [
                "script", 
                "style", 
                "noscript", 
                "nav", 
                "footer", 
                "form", 
                "iframe"
            ]

    for element in body_tag(unwanted_tags):
        element.decompose()
        
    clean_content = body_tag.get_text(separator=' ', strip=True)
    return clean_content

async def scrape_and_extract_all(target_webs: list[str], more_info: dict, today: datetime.date, end_date: datetime.date) -> list[dict]:
    """Returns a list[dict] with all events in time interval. Perofrms Browser launch, scraping loop, and LLM extraction."""
    events_list: list[dict] = []
    
    async with async_playwright() as p:

        browser = await p.chromium.launch(headless=True)
        print("Browser launched successfully.")
        
        context = await browser.new_context(
            user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36',
            extra_http_headers={"Accept-Language": "en-US,en;q=0.9"},
            viewport={'width': 1280, 'height': 800}
        )

        for url in target_webs:
            
            url_specific_info = more_info.get(url, "No additional information")
            text = await scrape_web_with_context(context, url)
            if text:
                url_events = extract_events(text, today, end_date, url_specific_info)
                events_list.extend(url_events)
                
            else:
                print(f"Skipping extraction for {url} due to empty content.")
                
        await browser.close()
        print("Scraping complete.")
        
    return events_list


def scrape_week_ahead() -> pd.DataFrame:
    """Main function to orchestrate the scraping and extraction."""
    
    day_interval = 7
    #today = datetime.date.today()
    #end_date = today + datetime.timedelta(days=day_interval)
    today = datetime.date(2025, 11, 30)
    end_date = datetime.date(2026, 2, 1)
    target_webs = [
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
        target_webs[0]: "Extract only home games played in Spotify Camp Nou. Spotify Camp Nou is in the 'les Corts' neighbourhood.",
        target_webs[1]: "All events from this text are in the 'el Poble-sec' neighbourhood.",
        target_webs[2]: "Any event in venue 'Gran Via' must not be extracted. The venue Montjuïc is located in 'el Poble-sec' neighbourhood and the venue CCIB is located in 'el Besòs i el Maresme' neighbourhood.",
        target_webs[3]: "Extract only 'Primavera Sound' music festival, no concerts. 'El Parc del Fòrum' is located in the 'el Besòs i el Maresme' neighbourhood.",
        target_webs[4]: "The Sonar Festival venue 'Fira Gran Via' is located in the 'la Marina de Port' neighbourhood.", 
        target_webs[5]: "The Cruïlla Festival venue 'El Parc del Fòrum' is located in the 'el Besòs i el Maresme' neighbourhood.", 
        target_webs[6]: "No additional information",
        target_webs[7]: "The El Corte Inglés Race runs through the 'les Corts', 'la Nova Esquerra de l'Eixample' and 'l'Antiga Esquerra de l'Eixample' neighbourhoods.", 
        target_webs[8]: "Sant Jordi is a Traditional Festival that covers 'all' neighborhoods.", 
        target_webs[9]: "Extract only the 'Manifestació' events that take place on September 11th. Get all the neighbourhoods the 'Manifestació' goes through", 
        target_webs[10]: "La Mercè is a Traditional Festival that covers 'all' neighborhoods."
    }
    

    events_list = asyncio.run(scrape_and_extract_all(target_webs, more_info, today, end_date))
    df_events = pd.DataFrame(events_list)

    print(df_events.to_markdown(index=False))
    return df_events


scrape_week_ahead()