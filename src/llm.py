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

DATE = "27-12-2025"
TODAY = pd.Timestamp.today().normalize()

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
        rechazar_btn = page.locator('#CybotCookiebotDialogBodyButtonDecline')
    
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
    logger.info(f"Scraping la fira event dates from: {url}")
    
    text = ""
    try:
        page.goto(url, wait_until="networkidle")
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
        rechazar_btn = page.locator('#didomi-notice-disagree-button')
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
    
    # HE MODIFICADO ESTO PARA QUE SEA UN f-string Y INCLUYA LOGICA DE RANGOS
    system_text = f"""
    Eres un extractor de datos de eventos profesional y estricto.
    Tu única tarea es analizar el texto y extraer eventos en Barcelona que estén activos el día objetivo: {DATE}.
    
    REGLAS DE FECHA CRÍTICAS:
    1. Si el evento es de un solo día, la fecha debe coincidir exactamente con {DATE}.
    2. Si el evento es un rango (ej: "Del 25 al 30 de Diciembre"), DEBES incluirlo si {DATE} está dentro de ese lapso.
    3. Si el evento ocurre en otra fecha distinta a {DATE}, IGNORELÓ completamente.
    4. Si no hay eventos activos para el {DATE}, devuelve una lista vacía [].

    Salida OBLIGATORIA: Un ARRAY JSON de objetos []. Sin markdown, sin explicaciones.
    Cada objeto debe tener: 'nombre', 'ubicacion', 'fechas'.
    
    REGLA DE UBICACIÓN:
    En la ubicación, dame el nombre exacto del BARRIO de Barcelona donde se encuentra (ej: Sants-Montjuïc, Les Corts, El Besòs), no el nombre del estadio.
    """
    
    full_prompt = f"""
    {system_text}
    
    INSTRUCCIÓN ESPECÍFICA: "{user_prompt}"
    
    TEXTO A ANALIZAR:
    {text}
    """

    generation_config = {
        "temperature": 0.0,
        "response_mime_type": "application/json", 
    }


    try:
        model = genai.GenerativeModel('gemini-flash-latest')
        
        response = model.generate_content(
            full_prompt, 
            generation_config=generation_config
        )
        
        json_string = response.text
        
        clean_json = json_string.strip()
        if clean_json.startswith("```"):
            clean_json = clean_json.strip("`").replace("json", "").strip()
            
        data = json.loads(clean_json)
        
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
            f"Analiza si hay algún concierto del Primavera Sound activo exactamente el día {DATE}. Si el festival es en junio y estamos en {DATE}, devuelve lista vacía.",

            scrap_fira(browser):
            f"Busca ferias o congresos en Fira Barcelona que estén ocurriendo el {DATE}. Revisa las fechas de inicio y fin.",

            scrap_fcb(browser):
            f"Busca si el FC Barcelona juega un partido exactamente el día {DATE}. Si es otro día, ignóralo.",

            scrap_olimpic(browser):
            f"Busca eventos MUSICALES (conciertos) en el Estadi Olímpic que tengan lugar el {DATE}. Ignora deportes u otros tipos."
        }

        for scrap, prompt in webs_prompts.items():
            if scrap: 
                print(f"--- Procesando Prompt: {prompt[:50]}... ---")
                df = ask_gemini(scrap, prompt)
                if not df.empty:
                    print(df.to_string())
                else:
                    print("No se encontraron eventos para esta fecha.")
                print("\n")

if __name__ == '__main__':
    main()