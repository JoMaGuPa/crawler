import time
import csv
import requests
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from bs4 import BeautifulSoup
from urllib.parse import urlparse, urljoin

# Funció per inicialitzar el navegador
def inicia_navegador():
    options = webdriver.ChromeOptions()
    navegador = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
    return navegador

# Funció per obtenir tots els enllaços interns d'una pàgina
def obtenir_enllacos_interns(navegador, url_base):
    navegador.get(url_base)
    time.sleep(2)  # Espera perquè la pàgina es carregui completament
    codi_html = navegador.page_source
    soup = BeautifulSoup(codi_html, 'html.parser')

    enllacos = set()
    for etiqueta_a in soup.find_all('a', href=True):
        enllac = etiqueta_a['href']
        # Ignorar enllaços externs i només seguir enllaços interns
        if enllac.startswith('/'):
            enllac = urljoin(url_base, enllac)  # Convertir l'enllaç relatiu en absolut
        parsed_url = urlparse(enllac)
        if parsed_url.netloc == urlparse(url_base).netloc:  # Assegurar-nos que és intern
            enllacos.add(enllac)
    
    return enllacos

# Funció per comprovar l'estat HTTP d'una URL
def comprovar_estat_url(url):
    try:
        resposta = requests.get(url)
        return resposta.status_code
    except requests.exceptions.RequestException:
        return None  # Si hi ha un error en la connexió

# Funció principal del rastrejador
def rastrejar_domini(url_base):
    navegador = inicia_navegador()
    visitades = set()
    errors_4xx = []
    per_visitar = [url_base]
    
    comptador = 0  # Comptador de pàgines visitades
    max_pagines = 10  # Límit de pàgines a visitar

    while per_visitar:
        if comptador >= max_pagines:
            print(f"🚦 S'ha assolit el límit de {max_pagines} pàgines. Aturant...")
            break

        url = per_visitar.pop()
        if url in visitades:
            continue
        visitades.add(url)
        comptador += 1

        print(f"📌 Visitant ({comptador}/{max_pagines}): {url}")
        navegador.get(url)
        time.sleep(2)  # Pausa per veure la pàgina abans de continuar

        enllacos_interns = obtenir_enllacos_interns(navegador, url)

        # Afegir només els enllaços nous que encara no hem visitat
        for enllac in enllacos_interns:
            if enllac not in visitades:
                per_visitar.append(enllac)

        estat_http = comprovar_estat_url(url)
        if estat_http and 400 <= estat_http < 500:
            print(f"❌ Error 4XX a {url} - Codi: {estat_http}")
            errors_4xx.append({
                'url': url,
                'codi_error': estat_http,
                'pagina_origen': url_base
            })

    navegador.quit()
    return errors_4xx

# Funció per generar un informe CSV dels errors trobats
def generar_informe(errors_4xx, nom_fitxer='informe_errors_4xx.csv'):
    claus = errors_4xx[0].keys() if errors_4xx else []
    with open(nom_fitxer, mode='w', newline='', encoding='utf-8') as fitxer:
        escriptor = csv.DictWriter(fitxer, fieldnames=claus)
        escriptor.writeheader()
        escriptor.writerows(errors_4xx)

if __name__ == "__main__":
    url_domini = "http://httpstat.us"
    print("🔎 Iniciant el rastrejador...")
    
    errors = rastrejar_domini(url_domini)

    if errors:
        print(f"⚠️ S'han trobat {len(errors)} errors 4XX.")
        generar_informe(errors)
        print("📄 Informe generat: informe_errors_4xx.csv")
    else:
        print("✅ No s'han trobat errors 4XX.")

    input("Prem Enter per tancar el navegador...")