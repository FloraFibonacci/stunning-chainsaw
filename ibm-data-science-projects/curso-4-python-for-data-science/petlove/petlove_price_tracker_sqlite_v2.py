import os
import re
import sqlite3
import argparse
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from datetime import datetime
import matplotlib.pyplot as plt
from plot_data import plot_data  # Importa a função plot_data do arquivo plot_data.py

### Configurações e constantes
DB_FILE = os.path.expanduser('/home/luca/Petlove/petlove_prices.db')
CAT_MIN_WEIGHT = 5.1
DOG_MIN_WEIGHT = 10

BASE_URL = 'https://www.petlove.com.br'
SEARCH_URL = f"{BASE_URL}/busca?q=n%26d&order=price_desc"

### Regex para capturar peso em nomes de produtos
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

def fetch_page(driver, url):
    """
    Faz a requisição de uma página usando Selenium e retorna os produtos encontrados.
    """
    driver.get(url)
    try:
        # Aguarda até que os produtos sejam carregados
        WebDriverWait(driver, 20).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, 'div.product-card'))
        )
    except Exception as e:
        print(f"Erro ao carregar a página {url}: {e}")
        return []

    items = []

    ### Seletores para diferentes layouts de produtos
    product_cards = driver.find_elements(By.CSS_SELECTOR, 'div.product-card')
    print(f"Encontrados {len(product_cards)} produtos na página {url}")

    for card in product_cards:
        try:
            # Seletor genérico para o título do produto
            name_el = card.find_element(By.CSS_SELECTOR, 'h2.product-card__name')

            # Seletor genérico para o preço
            price_el = card.find_element(By.CSS_SELECTOR, 'span[datatest-id="subscriber-price"]')

            name = name_el.text.strip()
            price_text = price_el.text.strip().replace('R$', '').replace('.', '').replace(',', '.')

            # Converte o preço para float
            price = float(price_text)

            # Extrai o peso do nome do produto
            weight = parse_weight(name)
            if weight:
                print(f"Produto encontrado: {name}, Preço: {price}, Peso: {weight}")
                items.append({'name': name, 'price': price, 'weight': weight})
        except Exception as e:
            print(f"Erro ao processar um produto: {e}")
            continue

    return items

def init_db():
    """
    Inicializa o banco de dados SQLite, criando a tabela se necessário.
    """
    with sqlite3.connect(DB_FILE) as conn:
        cur = conn.cursor()
        cur.execute('''
            CREATE TABLE IF NOT EXISTS prices (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TEXT,
                date TEXT,
                type TEXT,
                name TEXT,
                weight REAL,
                price REAL,
                price_per_kg REAL
            )
        ''')
        conn.commit()

def write_items_to_db(conn, items, product_type):
    """
    Escreve os itens no banco de dados SQLite.
    """
    now = datetime.now()
    timestamp = now.strftime('%Y-%m-%d %H:%M:%S')  # Data e hora no formato YYYY-MM-DD HH:MM:SS
    today = now.strftime('%Y-%m-%d')  # Apenas a data

    cur = conn.cursor()
    for item in items:
        ppkg = round(item['price'] / item['weight'], 2)
        cur.execute('''
            SELECT COUNT(*) FROM prices WHERE name = ? AND date = ? AND type = ?
        ''', (item['name'], today, product_type))
        exists = cur.fetchone()[0]

        if not exists:
            cur.execute('''
                INSERT INTO prices (timestamp, date, type, name, weight, price, price_per_kg)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (timestamp, today, product_type, item['name'], item['weight'], item['price'], ppkg))
            print(f"Inserido: {item['name']}")
        else:
            print(f"Produto já existe no banco: {item['name']}")
    conn.commit()

def truncate_name(name, max_length=30):
    return name if len(name) <= max_length else name[:max_length] + '...'

def parse_args():
    parser = argparse.ArgumentParser(description="Rastreamento de preços Petlove")
    parser.add_argument('--headless', action='store_true', help="Executar o navegador em modo headless")
    return parser.parse_args()

def main():
    """
    Função principal que coleta os dados e os armazena no banco de dados.
    """
    # Configurações do Selenium WebDriver
    chrome_options = Options()
    # chrome_options.add_argument('--headless')  # Executa o navegador em modo headless (sem interface gráfica)
    chrome_options.add_argument('--disable-gpu')
    chrome_options.add_argument('--no-sandbox')

    service = Service('/usr/bin/chromedriver')  # Caminho para o ChromeDriver
    driver = webdriver.Chrome(service=service, options=chrome_options)

    all_products = []
    page = 1
    while True:
        url = f"{SEARCH_URL}&page={page}"
        results = fetch_page(driver, url)
        if not results:
            break
        all_products.extend(results)
        page += 1

    driver.quit()  # Encerra o WebDriver

    # Filtra produtos da marca N&D
    nd_products = [p for p in all_products if 'n&d' in p['name'].lower()]

    # Filtra produtos para gatos e cachorros dentro da marca N&D
    cats = [p for p in nd_products if 'gato' in p['name'].lower() and 'adulto' in p['name'].lower() and 'castrado' in p['name'].lower() and p['weight'] >= CAT_MIN_WEIGHT]
    dogs = [p for p in nd_products if 'cães' in p['name'].lower() and ('grande' in p['name'].lower() or 'porte grande' in p['name'].lower()) and p['weight'] >= DOG_MIN_WEIGHT]

    print(f"Produtos de gato identificados: {len(cats)}")
    for cat in cats:
        print(f"Nome: {cat['name']}, Peso: {cat['weight']}, Preço: {cat['price']}")

    print(f"Produtos de cachorro identificados: {len(dogs)}")
    for dog in dogs:
        print(f"Nome: {dog['name']}, Peso: {dog['weight']}, Preço: {dog['price']}")

    # Inicializa o banco de dados e escreve os dados
    init_db()
    with sqlite3.connect(DB_FILE) as conn:
        write_items_to_db(conn, cats, 'Gatos')
        write_items_to_db(conn, dogs, 'Cachorros')

    print(f"Escritas {len(cats)} gatos e {len(dogs)} cachorros da marca N&D no banco de dados em {datetime.now().date()}")

    # Chama a função plot_data para gerar os gráficos
    plot_data()

if __name__ == '__main__':
    main()
