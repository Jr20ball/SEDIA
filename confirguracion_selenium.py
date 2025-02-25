from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import pandas as pd
import os
from openpyxl import load_workbook
from openpyxl.styles import PatternFill, Font, Alignment
import logging
from concurrent.futures import ThreadPoolExecutor

# Configurar logging
logging.basicConfig(filename="scraping_log.txt", level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

# Configurar Selenium con ChromeDriver
def configure_browser(driver_path):
    chrome_options = Options()
    chrome_options.add_argument('--headless')  # Modo sin interfaz gráfica
    chrome_options.add_argument('--disable-gpu')
    chrome_options.add_argument('--no-sandbox')
    chrome_options.add_argument('--log-level=3')  # Reduce logs de Chrome
    chrome_options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36")
    
    service = Service(driver_path)
    return webdriver.Chrome(service=service, options=chrome_options)

# Cargar las URLs desde el archivo CSV
file_path = "C:\\Users\\albar\\Desktop\\enlaces_infosubvenciones.csv"
df_urls = pd.read_csv(file_path, sep=';')
urls = df_urls["Enlace"].dropna().tolist()
cleaned_urls = [url.replace("https://www.infosubvenciones.eshttps://www.infosubvenciones.es", "https://www.infosubvenciones.es") for url in urls]

# Ruta del driver
driver_path = "C:\\Users\\albar\\Downloads\\chromedriver-win64\\chromedriver.exe"