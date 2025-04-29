import json
import os
import re
import requests
from bs4 import BeautifulSoup
from datetime import datetime
import gspread
from oauth2client.service_account import ServiceAccountCredentials

# Configurações e constantes
CREDENTIALS_FILE = os.path.expanduser('~/.credentials/petlove-sheets.json')
SPREADSHEET_NAME = 'Petlove_ND_Price_History'
CAT_SHEET = 'Gatos'
DOG_SHEET = 'Cachorros'

BASE_URL = 'https://www.petlove.com.br'
SEARCH_URL = f"{BASE_URL}/busca?brand=1058&order=price_desc"

CAT_MIN_WEIGHT = 5.1
DOG_MIN_WEIGHT = 10.1

# Regex para capturar peso em nomes de produtos
weight_pattern = re.compile(r"(\d+[\d\.,]*)\s*kg", re.IGNORECASE)

def parse_weight(name):
    """
    Extrai o peso de um produto a partir do nome.
    """
    match = weight_pattern.search(name)
    if match:
        text = match.group(1).replace('.', '').replace(',', '.')
        try:
            return float(text)
        except ValueError:
            return None
    return None

def fetch_page(url):
    """
    Faz a requisição de uma página e retorna os produtos encontrados.
    """
    try:
        resp = requests.get(url)
        resp.raise_for_status()
    except requests.RequestException as e:
        print(f"Erro ao buscar a URL {url}: {e}")
        return []

    soup = BeautifulSoup(resp.text, 'html.parser')
    items = []

    # Seletores para diferentes layouts de produtos
    product_selectors = [
        'div.product-card', 'div.product', 'div.product__info',
        'div.product__summary', 'div.product__content'
    ]
    selector_query = ', '.join(product_selectors)

    for card in soup.select(selector_query):
        name_el = (
            card.select_one('h2.product-name') or
            card.select_one('h3.product-name') or
            card.select_one('h1.mt-5.font-title-xs.font-medium.color-neutral-darkest') or
            card.select_one('.name') or
            card.select_one('.product__title')
        )
        price_el = (
            card.select_one('span.price') or
            card.select_one('.product-price') or
            card.select_one('.price__best') or
            card.select_one('span.leading-1')
        )
        if not name_el or not price_el:
            continue

        name = name_el.get_text(strip=True)
        price_text = price_el.get_text(strip=True)
        try:
            price = float(price_text.replace('R$', '').replace('.', '').replace(',', '.'))
        except ValueError:
            continue

        weight = parse_weight(name)
        if weight:
            items.append({'name': name, 'price': price, 'weight': weight})
    return items

def discover_brand_ids():
    """
    Descobre os IDs das marcas disponíveis na página de busca.
    """
    try:
        resp = requests.get(BASE_URL + '/busca')
        resp.raise_for_status()
    except requests.RequestException as e:
        print(f"Erro ao buscar marcas: {e}")
        return {}

    soup = BeautifulSoup(resp.text, 'html.parser')
    brands = {}
    for inp in soup.select('input[name="brand"]'):
        val = inp.get('value')
        lbl = soup.find('label', {'for': inp.get('id')})
        name = lbl.get_text(strip=True) if lbl else val
        brands[name] = val
    return brands

def auth_sheets(credentials_path):
    """
    Autentica no Google Sheets usando credenciais do arquivo JSON.
    """
    try:
        with open(credentials_path, 'r') as f:
            creds_dict = json.load(f)
        scope = [
            'https://www.googleapis.com/auth/spreadsheets',
            'https://www.googleapis.com/auth/drive'
        ]
        creds = ServiceAccountCredentials.from_json_keyfile_dict(creds_dict, scope)
        client = gspread.authorize(creds)
        return client.open(SPREADSHEET_NAME)
    except Exception as e:
        print(f"Erro ao autenticar no Google Sheets: {e}")
        raise

def write_items_to_sheet(sheet, items, worksheet_name):
    """
    Escreve os itens no Google Sheets, criando a aba se necessário.
    """
    headers = ['Data', 'Tipo', 'Nome', 'Peso (kg)', 'Preço Total (R$)', 'Preço por Kg (R$/kg)']
    try:
        ws = sheet.worksheet(worksheet_name)
    except gspread.exceptions.WorksheetNotFound:
        ws = sheet.add_worksheet(title=worksheet_name, rows='1000', cols='10')
        ws.append_row(headers)

    today = datetime.now().strftime('%Y-%m-%d')
    for item in items:
        ppkg = round(item['price'] / item['weight'], 2)
        row = [today, worksheet_name, item['name'], item['weight'], item['price'], ppkg]
        ws.append_row(row)

def main():
    """
    Função principal que coleta os dados e os escreve no Google Sheets.
    """
    all_products = []
    page = 1
    while True:
        url = f"{SEARCH_URL}&page={page}"
        results = fetch_page(url)
        if not results:
            break
        all_products.extend(results)
        page += 1

    # Filtra produtos para gatos e cachorros
    cats = [p for p in all_products if 'gato' in p['name'].lower() and 'adulto' in p['name'].lower() and 'castrado' in p['name'].lower() and p['weight'] >= CAT_MIN_WEIGHT]
    dogs = [p for p in all_products if 'cachorro' in p['name'].lower() and ('porte grande' in p['name'].lower() or 'raça grande' in p['name'].lower()) and p['weight'] >= DOG_MIN_WEIGHT]

    try:
        sheet = auth_sheets(CREDENTIALS_FILE)
        write_items_to_sheet(sheet, cats, CAT_SHEET)
        write_items_to_sheet(sheet, dogs, DOG_SHEET)
        print(f"Escritas {len(cats)} gatos e {len(dogs)} cachorros no Sheets em {datetime.now().date()}")
    except Exception as e:
        print(f"Erro durante a execução: {e}")

if __name__ == '__main__':
    main()
