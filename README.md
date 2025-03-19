# Memòria Tècnica - Crawler de Detecció d'Errors 4XX

## Descripció del Projecte
Aquest projecte consisteix en un crawler desenvolupat en Python que explora un domini web i detecta totes les URLs que retornin codis d'error 4XX. El programa utilitza Selenium per navegar per les pàgines web i BeautifulSoup per extreure els enllaços interns. A més, s'usa la llibreria `requests` per comprovar l'estat HTTP de cada URL visitada.

## Tecnologies Utilitzades
- **Python** (llenguatge principal)
- **Selenium** (automatització de la navegació web)
- **BeautifulSoup** (extracció d'enllaços d'HTML)
- **requests** (comprovació de l'estat de les URLs)
- **CSV** (generació d'informe d'errors)

## Procés de Disseny i Decisions Preses
### 1. Inicialització del Navegador
S'utilitza Selenium per carregar les pàgines web. S'usa `webdriver_manager` per instal·lar automàticament el driver de Chrome:
```python
def inicia_navegador():
    options = webdriver.ChromeOptions()
    navegador = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
    return navegador
```

### 2. Extracció d'Enllaços
S'analitza el codi HTML amb BeautifulSoup per trobar enllaços interns:
```python
def obtenir_enllacos_interns(navegador, url_base):
    navegador.get(url_base)
    time.sleep(2)
    codi_html = navegador.page_source
    soup = BeautifulSoup(codi_html, 'html.parser')
    enllacos = set()
    for etiqueta_a in soup.find_all('a', href=True):
        enllac = etiqueta_a['href']
        if enllac.startswith('/'):
            enllac = urljoin(url_base, enllac)
        if urlparse(enllac).netloc == urlparse(url_base).netloc:
            enllacos.add(enllac)
    return enllacos
```

### 3. Comprovació de l'Estat de les URLs
Cada URL visitada és verificada per detectar si retorna un codi 4XX:
```python
def comprovar_estat_url(url):
    try:
        resposta = requests.get(url)
        return resposta.status_code
    except requests.exceptions.RequestException:
        return None
```

### 4. Límit de Pàgines Visitades
Per evitar que el crawler es quedi encallat o explori indefinidament, s'ha establert un límit de 10 pàgines:
```python
max_pagines = 10
if comptador >= max_pagines:
    print(f"🚦 S'ha assolit el límit de {max_pagines} pàgines. Aturant...")
    break
```

### 5. Generació de l'Informe
Els errors trobats es guarden en un fitxer CSV:
```python
def generar_informe(errors_4xx, nom_fitxer='informe_errors_4xx.csv'):
    claus = errors_4xx[0].keys() if errors_4xx else []
    with open(nom_fitxer, mode='w', newline='', encoding='utf-8') as fitxer:
        escriptor = csv.DictWriter(fitxer, fieldnames=claus)
        escriptor.writeheader()
        escriptor.writerows(errors_4xx)
```

## Com Utilitzar el Crawler
### 1. Instal·lació de Dependències
Executa la següent comanda per instal·lar els paquets necessaris:
```bash
pip install selenium beautifulsoup4 requests webdriver_manager
```

### 2. Execució del Programa
Executa el crawler amb:
```bash
python crawler.py
```
El programa explorarà el domini especificat i generarà un informe `informe_errors_4xx.csv` amb els errors trobats.

## Conclusions
Aquest crawler permet identificar errors 4XX dins d'un domini web de manera eficient, fent servir Selenium per la navegació i `requests` per la verificació d'estats HTTP. L'estratègia de limitació de pàgines evita cicles infinits i millora el rendiment. El projecte pot ampliar-se en el futur per incloure funcionalitats com la detecció d'altres codis d'error HTTP o l'extracció de més metadades de cada pàgina.

