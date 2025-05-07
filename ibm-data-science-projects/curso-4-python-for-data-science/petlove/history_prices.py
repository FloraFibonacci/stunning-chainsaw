import os
import sqlite3
import matplotlib.pyplot as plt
from datetime import datetime
import re
from itertools import cycle  # Para alternar estilos de linha e cores

# Caminho para o banco de dados (relativo ao diretório do script)
DB_FILE = os.path.join(os.path.dirname(__file__), 'petlove_prices.db')

# Lista de palavras indesejadas na legenda
UNWANTED_WORDS = ['Ração', 'para', 'de', 'e', 'kg', 'Seca', 'N&D', 'Farmina', 'Gatos', 'Castrados', 'Médias', 'Grandes' , 'Cães', 'Adultos', 'Raças']

# Lista de estilos de linha
LINE_STYLES = ['-', '--', '-.', ':']

def clean_name(name):
    """
    Remove palavras indesejadas do nome do produto, apenas se estiverem isoladas.
    """
    for word in UNWANTED_WORDS:
        # Substitui apenas palavras completas (isoladas)
        name = re.sub(rf'\b{word}\b', '', name, flags=re.IGNORECASE).strip()
    # Remove espaços extras após a limpeza
    return re.sub(r'\s+', ' ', name).strip()

def plot_price_history_combined():
    """
    Lê os dados do banco de dados SQLite e exibe um único gráfico com o histórico de preços de todos os produtos.
    """
    print("Gerando gráfico combinado...")
    with sqlite3.connect(DB_FILE) as conn:
        cur = conn.cursor()

        # Obter todos os produtos distintos
        cur.execute('SELECT DISTINCT name, type FROM prices ORDER BY type, name')
        products = cur.fetchall()

        plt.figure(figsize=(15, 8))  # Configura o tamanho do gráfico

        # Gerar um colormap com base no número de produtos
        colormap = plt.colormaps['tab20']  # Use o colormap diretamente
        colors = cycle(colormap.colors)  # Cicla pelas cores se exceder o número disponível
        line_styles = cycle(LINE_STYLES)  # Cicla pelos estilos de linha

        for idx, (product_name, animal_type) in enumerate(products):
            # Obter todos os registros históricos para este produto
            cur.execute('''
                SELECT date, price_per_kg 
                FROM prices 
                WHERE name = ? AND type = ?
                ORDER BY date
            ''', (product_name, animal_type))
            rows = cur.fetchall()

            # Preparar dados para o gráfico
            dates = [datetime.strptime(row[0], '%Y-%m-%d') for row in rows]
            prices = [row[1] for row in rows]

            # Limpar e truncar o nome do produto para a legenda
            cleaned_name = clean_name(product_name)
            legend_label = f'{cleaned_name} {animal_type}'

            # Adicionar linha ao gráfico com uma cor e estilo de linha
            plt.plot(dates, prices, marker='o', linestyle=next(line_styles), label=legend_label, color=next(colors))

        # Formatando o gráfico
        plt.title('Histórico de Preço por Kg - Todos os Produtos')
        plt.xlabel('Data')
        plt.ylabel('Preço por Kg (R$)')
        plt.grid(True)

        # Ajustar o eixo X para exibir apenas as datas presentes nos dados
        plt.gca().xaxis.set_major_locator(plt.MaxNLocator(integer=True))
        plt.xticks(rotation=45)

        # Adicionar legenda abaixo do gráfico
        plt.legend(loc='upper center', bbox_to_anchor=(0.5, -0.15), fontsize='small', ncol=3)  # Ajusta a posição e o tamanho da legenda
        plt.tight_layout()

        # Mostrar o gráfico
        plt.show()

def plot_price_history_by_type(animal_type):
    """
    Lê os dados do banco de dados SQLite e exibe um gráfico com o histórico de preços para um tipo específico de animal.
    """
    print(f"Gerando gráfico para {animal_type}...")
    with sqlite3.connect(DB_FILE) as conn:
        cur = conn.cursor()

        # Obter todos os produtos do tipo especificado
        cur.execute('SELECT DISTINCT name FROM prices WHERE type = ? ORDER BY name', (animal_type,))
        products = cur.fetchall()

        plt.figure(figsize=(15, 8))  # Configura o tamanho do gráfico

        # Gerar um colormap com base no número de produtos
        colormap = plt.colormaps['tab20']  # Use o colormap diretamente
        colors = cycle(colormap.colors)  # Cicla pelas cores se exceder o número disponível
        line_styles = cycle(LINE_STYLES)  # Cicla pelos estilos de linha

        for idx, (product_name,) in enumerate(products):
            # Obter todos os registros históricos para este produto
            cur.execute('''
                SELECT date, price_per_kg 
                FROM prices 
                WHERE name = ? AND type = ?
                ORDER BY date
            ''', (product_name, animal_type))
            rows = cur.fetchall()

            
            # Preparar dados para o gráfico
            dates = [datetime.strptime(row[0], '%Y-%m-%d') for row in rows]
            prices = [row[1] for row in rows]

            # Limpar o nome do produto para a legenda
            cleaned_name = clean_name(product_name)
            legend_label = f'{cleaned_name}'  # Usa o nome completo sem truncar

            # Adicionar linha ao gráfico com uma cor e estilo de linha
            plt.plot(dates, prices, marker='o', linestyle=next(line_styles), label=legend_label, color=next(colors))

        # Formatando o gráfico
        plt.title(f'Histórico de Preço por Kg - {animal_type}')
        plt.xlabel('Data')
        plt.ylabel('Preço por Kg (R$)')
        plt.grid(True)

        # Ajustar o eixo X para exibir apenas as datas presentes nos dados
        plt.gca().xaxis.set_major_locator(plt.MaxNLocator(integer=True))
        plt.xticks(rotation=45)

        # Adicionar legenda abaixo do gráfico
        plt.legend(loc='upper center', bbox_to_anchor=(0.5, -0.15), fontsize='small', ncol=3)  # Ajusta a posição e o tamanho da legenda
        plt.tight_layout()

        # Mostrar o gráfico
        plt.show()

if __name__ == '__main__':
    # Gerar gráficos separados para gatos e cachorros
    plot_price_history_by_type('Gatos')
    plot_price_history_by_type('Cachorros')