from playwright.sync_api import sync_playwright, Browser, Page
import pandas as pd
import logging
import re

logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')
logger = logging.getLogger(__name__)

TWO_WEEKS = pd.Timedelta(weeks=2)
VENUE_BARRI: dict[str,str] = {"Spotify Camp Nou": "les Corts", 
                            "Palau Sant Jordi": "el Poble-sec",
                            "Sant Jordi Club": "el Poble-sec",
                            "Estadi Olímpic": "el Poble-sec",
                            "Montjuïc": "el Poble-sec",
                            "CCIB": "el Besòs i el Maresme"}

def create_browser(playwright) -> Browser:
    """Launches a single Chromium browser"""

    return playwright.chromium.launch(
        headless=False,
        args=[
            "--disable-gpu",
            "--no-sandbox",
            "--ozone-platform=x11"]
      )

def scrape_fc_barcelona_schedule(browser: Browser) -> pd.DataFrame:
    """Scrapes FC Barcelona's scheduled events (home matches) within the next two weeks."""
    
    page = browser.new_page()
    url = "https://www.fcbarcelona.com/en/club/club-schedule"
    logger.info(f"Scraping FC Barcelona Schedule from: {url}")
    
    page.goto(url, wait_until="domcontentloaded")
    
    data_list: list[dict] = []
    today = pd.Timestamp.today().normalize()
    two_weeks_later = today + TWO_WEEKS

    try:
        event_locator = page.locator('.static-page__content p:has-text("Spotify Camp Nou")')
        raw_texts = event_locator.all_inner_texts()
    
        for raw_text in raw_texts:
            date_match = re.search(r'^(\w{3,9},\s*\d{1,2}\s*\w{3,9})', raw_text, re.DOTALL)
            day_month = date_match.group(1).strip()              
            date = pd.to_datetime(f"{day_month} {today.year}", errors='coerce')
            
            if date < today:
                date = pd.to_datetime(f"{day_month} {today.year + 1}")

            if today <= date <= two_weeks_later:
                data_list.append({
                    "day": date,
                    "impact": 0,
                    "barri": VENUE_BARRI["Spotify Camp Nou"],
                    "description": raw_text
                })
            else: break

    except:
        logger.error(f"Error scraping FC Barcelona events")
        
    page.close()
    return pd.DataFrame(data_list)

def scrape_anellolimpic_events(browser: Browser) -> pd.DataFrame:
    """Scrapes music events from the Anell Olímpic in the next two weeks"""
    
    page = browser.new_page()
    url = "https://estadiolimpic.barcelona/en/events"
    logger.info(f"Scraping Anell Olímpic events from: {url}")
    
    data_list: list[dict] = []
    today = pd.Timestamp.today().normalize()

    two_weeks_later = today + TWO_WEEKS
    keep_looking = True

    try:
        
        page.goto(url, wait_until="domcontentloaded")
        apply_music_filter(page)
        while keep_looking:
            
            page.wait_for_selector(".views-row")
            event_locator = page.locator(".views-row")
            events = event_locator.all()
            for event in events:
    
                name = event.locator("span.field--name-title").inner_text().strip()
                place = event.locator("div.field--name-field-place").inner_text().strip()
                date_str = event.locator("div.events-list__content-date").inner_text().strip()
                date = pd.to_datetime(date_str, errors="coerce")

                if today <= date <= two_weeks_later:
                    data_list.append({
                        "day": date,
                        "impact": 0,
                        "barri": VENUE_BARRI[place],
                        "description": name
                    })
                else:
                    keep_looking = False
                    break

            next_link = page.locator("a[title='Go to next page']")
            if next_link.count() > 0 and keep_looking:
                next_link.click()
            else:
                keep_looking = False
                
    except:
        logger.error(f"Error during Anell Olímpic scraping process")
        
    page.close()
    return pd.DataFrame(data_list)


def apply_music_filter(page: Page) -> None:
    """Applies a filter in Estadi Olimpic web to only get music events"""
    
    logger.info("Starting filter application process.")
    label_element = page.locator('label:has-text("Música")')
    
    if label_element.count() == 0:
        raise Exception("Could not find 'Música' label element.")
        
    label_element.scroll_into_view_if_needed()
    label_element.click(force=True)
    page.wait_for_timeout(500) 
    form_selector = "form#views-exposed-form-event-list-agenda"
    
    if page.locator(form_selector).count() == 0:
        raise Exception(f"Could not find the filter form with selector: {form_selector}")

    with page.expect_navigation(wait_until="domcontentloaded", timeout=30000):
        # Execute JavaScript to find the form element and call its submit() method.
        page.evaluate(f"document.querySelector('{form_selector}').submit()")
        
    page.wait_for_selector(".views-row", timeout=15000)

def scrape_lafira_events(browser: Browser) -> pd.DataFrame:
    """Scrapes events from La Fira filtering events in the coming two weeks."""
    
    page = browser.new_page()
    url = "https://www.firabarcelona.com/en/trade_show/"
    logger.info(f"Scraping La Fira events from: {url}")
    
    data_list: list[dict] = []
    today = pd.Timestamp.today().normalize()
    two_weeks_later = today + TWO_WEEKS
    keep_looking = True

    try:
        page.goto(url, wait_until="domcontentloaded")
        events = page.locator("article").all()
        for event in events:

            name = event.locator("div.fair__single__content--title").inner_text().strip()
            place = event.locator("div.fair__single__content--location").inner_text().strip()
            date_str = event.locator("div.fair__single__content--dates").inner_text().strip()
            if place == "Gran Via":
                continue
            
            match = re.search(r'(\d+)-(\d+)\s+(\w{3})\s+(\d{4})', date_str)

            start_day, end_day = match.group(1), match.group(2)
            month = match.group(3)     
            year = match.group(4)  
            
            start_date = pd.to_datetime(f'{start_day} {month} {year}', format='%d %b %Y', errors="coerce")
            end_date =  pd.to_datetime(f'{end_day} {month} {year}', format='%d %b %Y', errors="coerce")

            all_days = pd.date_range(start=start_date, end=end_date, freq='D')

            for date in all_days:
                
                if today <= date <= two_weeks_later:
                    data_list.append({
                        "day": date,
                        "impact": 0,
                        "barri": VENUE_BARRI[place],
                        "description": name
                    })
                elif date > two_weeks_later: keep_looking = False

            if not keep_looking: break
            
    except:
        logger.error(f"Error during La Fira scraping process")
        
    page.close()
    return pd.DataFrame(data_list)


def scrape_primavera_sound(browser: Browser) -> pd.DataFrame:
    """Scrapes Primavera Sound dates"""
    
    page = browser.new_page()
    url = "https://www.primaverasound.com/es/"
    logger.info(f"Scraping Primavera Sound dates from: {url}")
    
    data_list: list[dict] = []
    today = pd.Timestamp.today().normalize()

    try:
        page.goto(url, wait_until="domcontentloaded")
        page.click("text=Festivales")
        #start_date = pd.to_datetime(f'{start_day} {month} {year}', format='%d %b %Y', errors="coerce")
        #end_date =  pd.to_datetime(f'{end_day} {month} {year}', format='%d %b %Y', errors="coerce")
        date_locator = page.locator('h3.uppercase font-americaMono text-20 mb-4')
        texto_extraido = date_locator.inner_text()
        data_list["Primavera Sound"] = texto_extraido
                    
    except:
        logger.error(f"Error during La Fira scraping process")
        
    page.close()
    return pd.DataFrame(data_list)


def main() -> None:
    
    with sync_playwright() as playwright:
        browser = create_browser(playwright)

        df_primavera = scrape_primavera_sound(browser)
        print(df_primavera)

        # df_football = scrape_fc_barcelona_schedule(browser)
        # print(df_football)

        #df_anellolimpic = scrape_anellolimpic_events(browser)
        #print(df_anellolimpic)
            
        # df_lafira = scrape_lafira_events(browser)
        # print(df_lafira)
        
if __name__ == '__main__':
    main()