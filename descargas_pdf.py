import os
import time
import shutil
import requests
import pandas as pd
from concurrent.futures import ThreadPoolExecutor
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# --- CONFIGURACIONES ---
CHROME_DRIVER_PATH = r"C:\Users\albar\Downloads\chromedriver-win64\chromedriver.exe"
XLSX_PATH = r"C:\Users\albar\Desktop\subvenciones_formato.xlsx"
DOWNLOAD_FOLDER = os.path.join(os.path.expanduser("~"), "Downloads")
SUBSIDY_FOLDER = os.path.join(os.path.expanduser("~"), "Desktop", "Subvenciones_PDFs")

# --- CONFIGURAR EL NAVEGADOR ---
def configure_browser(driver_path):
    options = webdriver.ChromeOptions()
    options.add_argument("--headless")
    options.add_argument("--disable-gpu")
    options.add_argument("--no-sandbox")
    options.add_argument("--log-level=3")
    options.add_argument("--disable-popup-blocking")  # Evitar bloqueos en descargas
    options.add_experimental_option("prefs", {
        "download.default_directory": DOWNLOAD_FOLDER,
        "download.prompt_for_download": False,
        "download.directory_upgrade": True,
        "safebrowsing.enabled": True
    })
    service = webdriver.chrome.service.Service(driver_path)
    return webdriver.Chrome(service=service, options=options)

# --- DESCARGAR PDF DIRECTAMENTE SI ES POSIBLE ---
def download_pdf_directly(pdf_url, subsidy_folder):
    """ Descarga el PDF directamente sin usar Selenium si el enlace es accesible """
    try:
        response = requests.get(pdf_url, stream=True)
        if response.status_code == 200:
            file_name = pdf_url.split("/")[-1]
            save_path = os.path.join(subsidy_folder, file_name)
            os.makedirs(subsidy_folder, exist_ok=True)  # Crear carpeta aunque no haya PDFs
            with open(save_path, "wb") as file:
                for chunk in response.iter_content(chunk_size=1024):
                    file.write(chunk)
            print(f" PDF descargado directamente: {save_path}")
            return True
    except Exception as e:
        print(f" No se pudo descargar directamente {pdf_url}: {e}")
    return False

# --- ESPERAR A QUE SE COMPLETEN LAS DESCARGAS ---
def wait_for_downloads(previous_files, subsidy_folder, timeout=60):
    """ Espera a que se descarguen los PDFs y los mueve a la carpeta correcta """
    print(f" Esperando descargas en: {subsidy_folder}")
    start_time = time.time()
    while time.time() - start_time < timeout:
        new_files = set(os.listdir(DOWNLOAD_FOLDER)) - previous_files
        pdfs = [file for file in new_files if file.endswith(".pdf")]

        if pdfs:
            time.sleep(3)  # Esperar un poco más para asegurar descargas completas
            os.makedirs(subsidy_folder, exist_ok=True)  # Crear la carpeta
            for pdf in pdfs:
                src = os.path.join(DOWNLOAD_FOLDER, pdf)
                dst = os.path.join(subsidy_folder, pdf)
                shutil.move(src, dst)
                print(f" Movido: {pdf} a {subsidy_folder}")
            return True  # Se descargaron archivos correctamente

        time.sleep(1)

    # Si no se descargó ningún PDF, se asegura de que la carpeta se cree vacía
    os.makedirs(subsidy_folder, exist_ok=True)
    print(f" No se encontraron PDFs en {subsidy_folder}, pero la carpeta ha sido creada.")
    return False  # No se descargaron archivos

# --- EXTRAER Y DESCARGAR PDFs DE UNA PÁGINA ---
def process_url(url):
    codigo_bdns = url.split("/")[-1]
    subsidy_folder = os.path.join(SUBSIDY_FOLDER, f"Subvencion_{codigo_bdns}")

    browser = configure_browser(CHROME_DRIVER_PATH)
    previous_files = set(os.listdir(DOWNLOAD_FOLDER))

    try:
        browser.get(url)
        time.sleep(3)

        # Intentar obtener el enlace directo al PDF
        try:
            pdf_links = browser.find_elements(By.XPATH, "//a[contains(@href, '.pdf')]")
            if pdf_links:
                pdf_url = pdf_links[0].get_attribute("href")
                if download_pdf_directly(pdf_url, subsidy_folder):
                    browser.quit()
                    return  # Salir si la descarga directa fue exitosa
        except Exception:
            pass  # Si no encuentra el enlace, sigue con Selenium

        # Si no hay enlace directo, intenta descargarlo con Selenium
        try:
            WebDriverWait(browser, 10).until(
                EC.presence_of_all_elements_located((By.XPATH, "//td[contains(@class, 'mat-column-nombreFic')]//mat-icon[text()='get_app']/ancestor::a"))
            )
            buttons = browser.find_elements(By.XPATH, "//td[contains(@class, 'mat-column-nombreFic')]//mat-icon[text()='get_app']/ancestor::a")

            for button in buttons:
                browser.execute_script("arguments[0].scrollIntoView();", button)
                time.sleep(1)
                try:
                    WebDriverWait(browser, 5).until(EC.element_to_be_clickable(button))
                    button.click()
                    time.sleep(2)
                except:
                    print(" No se pudo hacer clic con Selenium, intentando con JavaScript...")
                    browser.execute_script("arguments[0].click();", button)
                    time.sleep(2)
        except Exception as e:
            print(f" Error extrayendo PDFs en {url}: {e}")

        # Esperar descargas y mover archivos correctamente
        wait_for_downloads(previous_files, subsidy_folder)

    except Exception as e:
        print(f" Error en {url}: {e}")
    finally:
        browser.quit()

# --- PROCESO DE DESCARGA EN PARALELO ---
def process_subsidy_pdfs_in_parallel(urls, max_workers=6):
    """ Descarga los PDFs en paralelo asegurando que cada subvención tenga su carpeta """
    if os.path.exists(SUBSIDY_FOLDER):
        shutil.rmtree(SUBSIDY_FOLDER)
        print(f" Carpeta {SUBSIDY_FOLDER} vaciada.")
    os.makedirs(SUBSIDY_FOLDER, exist_ok=True)

    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        executor.map(process_url, urls)

    print(f"Descarga completada en {SUBSIDY_FOLDER}")

# --- EJECUTAR EL PROCESO ---
df = pd.read_excel(XLSX_PATH, engine='openpyxl')
urls = df["URL"].dropna().tolist()

process_subsidy_pdfs_in_parallel(urls, max_workers=6)
