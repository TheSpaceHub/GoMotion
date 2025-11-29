from playwright.sync_api import sync_playwright, Browser, Page
import pandas as pd
import logging
import google.generativeai as genai
from google.generativeai.types import HarmCategory, HarmBlockThreshold
import pandas as pd
import os
import json
from dotenv import load_dotenv

load_dotenv() 
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY") 
genai.configure(api_key=GEMINI_API_KEY)

logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')
logger = logging.getLogger(__name__)


TODAY = pd.Timestamp.today().normalize()
TWO_WEEKS = pd.Timedelta(weeks=2)
LIMIT = TODAY + TWO_WEEKS
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

def scrap_primavera(browser: Browser)-> str:
    page = browser.new_page()
    url = "https://www.primaverasound.com/es"
    logger.info(f"Scraping Primavera Sound dates from: {url}")
    
    text = ""
    try:
        page.goto(url, wait_until="domcontentloaded")
        rechazar_btn = page.locator('button:has-text("Rechazar todas las cookies")')
    
        rechazar_btn.wait_for(state="visible", timeout=7000)
        rechazar_btn.click()
        text = page.locator("body").inner_text()                    
    except:
        logger.error(f"Error during primavera sound scraping process")
        
    page.close()
    return text

def scrap_fira(browser: Browser)-> str:
    page = browser.new_page()
    url = "https://www.firabarcelona.com/en/trade_show/"
    logger.info(f"Scraping Primavera Sound dates from: {url}")
    
    text = ""
    try:
        page.goto(url, wait_until="domcontentloaded")
        text = page.locator("body").inner_text()                    
    except:
        logger.error(f"Error during la fira scraping process")
        
    page.close()
    return text

def scrap_fcb(browser: Browser)-> str:
    page = browser.new_page()
    url = "https://www.fcbarcelona.com/en/club/club-schedule"
    logger.info(f"Scraping fcb matches dates from: {url}")
    
    text = ""
    try:
        page.goto(url, wait_until="domcontentloaded")
        rechazar_btn = page.locator('button:has-text("Rechazar")')
        rechazar_btn.wait_for(state="visible", timeout=7000)
        rechazar_btn.click()
        text = page.locator("body").inner_text()                    
    except:
        logger.error(f"Error during fcb schedule scraping process")
        
    page.close()
    return text

def scrap_olimpic(browser: Browser)-> str:
    page = browser.new_page()
    url = "https://estadiolimpic.barcelona/en/events"
    logger.info(f"Scraping estadi olimpic events from: {url}")
    
    text = ""
    try:
        page.goto(url, wait_until="domcontentloaded")
        text = page.locator("body").inner_text()                    
    except:
        logger.error(f"Error during estadi olimpic scraping process")
        
    page.close()
    return text

def ask_gemini(text: str, user_prompt: str) -> pd.DataFrame:
    
    system_text = (
        "Eres un extractor de datos de eventos profesional. "
        "Tu única tarea es analizar el texto y extraer eventos en Barcelona. "
        "Salida OBLIGATORIA: Un ARRAY JSON de objetos []. Sin markdown, sin explicaciones. "
        "Cada objeto debe tener: 'nombre', 'ubicacion', 'fechas'."
    )
    
    full_prompt = f"""
    {system_text}
    
    PREGUNTA DEL USUARIO: "{user_prompt}"
    
    TEXTO A ANALIZAR:
    {text}
    """

    generation_config = {
        "temperature": 0.0,
        "response_mime_type": "application/json", # Fuerza JSON
    }


    try:
        model = genai.GenerativeModel('gemini-flash-latest')
        
        response = model.generate_content(
            full_prompt, # Pasamos todo junto para máxima compatibilidad
            generation_config=generation_config
        )
        
        json_string = response.text
        
        # Limpieza y Conversión
        # A veces devuelve ```json ... ```, lo quitamos por si acaso
        clean_json = json_string.strip()
        if clean_json.startswith("```"):
            clean_json = clean_json.strip("`").replace("json", "").strip()
            
        data = json.loads(clean_json)
        
        # Aplanar si devuelve diccionario en lugar de lista
        if isinstance(data, dict):
            flat_list = []
            for key, val in data.items():
                if isinstance(val, list): flat_list.extend(val)
            data = flat_list
            
        return pd.DataFrame(data)

    except Exception as e:
        return pd.DataFrame({'Error': [str(e)], 'Raw_Output': ["Verifica tu API Key y versión de librería"]})


def main() -> None:
    
    with sync_playwright() as playwright:

        browser = create_browser(playwright)
        webs_prompts = {
            scrap_primavera(browser): 
            "Te doy el texto que he extraido de una página web. Es de primavera sound. Quiero las fechas exactas (HORA NO) de la proxima vez que se celebre este evento en "
            "BARCELONA. SOLO DEL PRIMAVERA SOUND. OTRO EVENTOS NO IMPORTAN",

            scrap_fira(browser):
            "Te doy el texto que he extraido de una página web. Es de eventos de la fira de Barcelona. Dame fechas exactas (HORA NO) de todos los que encuentres desde {TODAY} hasta {LIMIT}."
            "DE ANTES O MAS TARDE NO QUIERO NADA.",

            scrap_fcb(browser):
            "Te doy el texto que he extraido de una página web. Es del calendario de partidos del FCB Barcelona. Dame fechas exactas (HORA NO) de todos los que encuentres desde {TODAY} hasta {LIMIT}."
            "SOLO DE LOS QUE SE CELEBRAN EN EL SPOTIFY CAMP NOU"
            "DE ANTES O MAS TARDE NO QUIERO NADA. DE OTRO SITIO TAMPOCO",

            scrap_olimpic(browser):
            "Te doy el texto que he extraido de una página web. Es del calendario de eventos del estadi olimpic de Barcelona. Dame fechas exactas (HORA NO) de todos los que encuentres desde {TODAY} hasta {LIMIT}."
            "DE ANTES DE ESAS FECHAS  O MAS TARDE NO QUIERO NADA"
            "SOLO DE LOS QUE SON DE MUSICA"
            "DE OTRO TIPO NO QUIERO NADA"

        }

        for scrap, prompt in webs_prompts.items():
            print(ask_gemini(scrap, prompt).to_string())

if __name__ == '__main__':
    main()