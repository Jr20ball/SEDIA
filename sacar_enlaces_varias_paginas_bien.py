from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import pandas as pd
import time

# Configurar la ruta del ChromeDriver
chrome_driver_path = "C:\\Users\\albar\\Downloads\\chromedriver-win64\\chromedriver.exe"

# Configurar opciones del navegador
options = webdriver.ChromeOptions()
options.add_argument("--headless")  # Ejecutar en segundo plano
options.add_argument("--disable-gpu")
options.add_argument("--no-sandbox")
options.add_argument("--disable-dev-shm-usage")

# Iniciar el navegador
driver = webdriver.Chrome(options=options)
driver.get("https://www.infosubvenciones.es/bdnstrans/GE/es/convocatorias")

# Esperar a que la página cargue completamente
wait = WebDriverWait(driver, 10)
time.sleep(3)

# Establecer el número máximo de páginas a recorrer
max_paginas = 1  # Cambia este valor según lo que necesites

# Seleccionar 100 elementos por página
try:
    selector = wait.until(EC.element_to_be_clickable((By.XPATH, "//mat-select[contains(@class, 'mat-select')]")))
    driver.execute_script("arguments[0].click();", selector)
    time.sleep(1)  # Esperar que el menú se despliegue
    opcion_100 = wait.until(EC.element_to_be_clickable((By.XPATH, "//span[contains(text(),'100')]")))
    driver.execute_script("arguments[0].click();", opcion_100)
    time.sleep(3)  # Esperar que la tabla se actualice
    print(" Se seleccionaron 100 elementos por página.")
except Exception as e:
    print(f" No se pudo cambiar a 100 elementos por página: {e}")

data = []
pagina = 1  # Contador de páginas

while pagina <= max_paginas:
    print(f" Extrayendo datos de la página {pagina}/{max_paginas}...")

    # Esperar a que la tabla de datos cargue
    wait.until(EC.presence_of_element_located((By.XPATH, "//tr[contains(@class, 'mat-row')]")))

    rows = driver.find_elements(By.XPATH, "//tr[contains(@class, 'mat-row')]")
    if not rows:
        print("⚠ No se encontraron filas en esta página.")
        break

    print(f" Se encontraron {len(rows)} filas en la página {pagina}.")

    # Extraer información de cada fila
    for row in rows:
        try:
            columns = row.find_elements(By.TAG_NAME, "td")
            if len(columns) > 5:
                numero = columns[0].text.strip()
                entidad1 = columns[1].text.strip()
                entidad2 = columns[2].text.strip()
                entidad3 = columns[3].text.strip()
                fecha_recepcion = columns[4].text.strip()
                descripcion = columns[5].text.strip()

                # Extraer enlace
                enlace_element = columns[0].find_elements(By.TAG_NAME, "a")
                enlace = "https://www.infosubvenciones.es" + enlace_element[0].get_attribute("href") if enlace_element else ""

                data.append([numero, entidad1, entidad2, entidad3, fecha_recepcion, descripcion, enlace])

        except Exception as e:
            print(f"⚠ Error extrayendo datos de una fila: {e}")

    # Intentar hacer clic en el botón de "Siguiente página"
    try:
        siguiente_boton = driver.find_element(By.XPATH, "//button[contains(@class, 'mat-paginator-navigation-next')]")

        # Verificar si el botón está deshabilitado (última página)
        if "mat-button-disabled" in siguiente_boton.get_attribute("class"):
            print("🚀 Última página alcanzada. Finalizando extracción.")
            break

        # Desplazar hasta el botón antes de hacer clic
        driver.execute_script("arguments[0].scrollIntoView();", siguiente_boton)
        driver.execute_script("arguments[0].click();", siguiente_boton)

        # Esperar a que la nueva página cargue
        time.sleep(2)  # Pequeña pausa para permitir la carga de la tabla
        wait.until(EC.staleness_of(rows[0]))  # Esperar que la página cambie
        wait.until(EC.presence_of_element_located((By.XPATH, "//tr[contains(@class, 'mat-row')]")))

        pagina += 1  # Incrementar el contador de páginas

    except Exception as e:
        print(f"⚠ Error al cambiar de página: {e}")
        break  # Si hay un error, salimos del bucle

# Cerrar el navegador
driver.quit()

# Guardar los datos en un archivo CSV si hay datos
if data:
    df = pd.DataFrame(data, columns=["Número", "Adiministración", "Departamento", "Órgano", "Fecha de Registro", "Título", "Enlace"])
    csv_path = "C:\\Users\\albar\\Desktop\\enlaces_infosubvenciones.csv"
    df.to_csv(csv_path, sep=";", index=False, encoding="utf-8-sig")
    print(f" Archivo guardado en: {csv_path}")
else:
    print(" No se extrajeron datos. No se guardará el archivo.")
