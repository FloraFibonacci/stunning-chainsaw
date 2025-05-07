import sqlite3
import matplotlib.pyplot as plt

# Caminho para o banco de dados
DB_FILE = '/home/luca/Codes/stunning-chainsaw/ibm-data-science-projects/curso-4-python-for-data-science/petlove/petlove_prices.db'

def truncate_name(name, max_length=30):
    """
    Trunca nomes longos para evitar cortes no gráfico.
    """
    return name if len(name) <= max_length else name[:max_length] + '...'

def plot_data():
    """
    Lê os dados do banco de dados SQLite e exibe gráficos separados para gatos e cachorros.
    """
    with sqlite3.connect(DB_FILE) as conn:
        cur = conn.cursor()

        for animal_type in ['Gatos', 'Cachorros']:
            cur.execute('''
                SELECT name, price_per_kg 
                FROM prices 
                WHERE type = ? 
                ORDER BY price_per_kg DESC
            ''', (animal_type,))
            rows = cur.fetchall()

            if not rows:
                print(f"Nenhum dado encontrado para {animal_type}.")
                continue

            # Trunca os nomes dos produtos para evitar cortes no gráfico
            product_names = [truncate_name(row[0], max_length=200) for row in rows]
            price_per_kg = [row[1] for row in rows]

            # Ajusta o tamanho da figura dinamicamente com base no número de produtos
            plt.figure(figsize=(12, len(product_names) * 0.5))
            plt.barh(product_names, price_per_kg, color='skyblue')
            plt.xlabel('Preço por Kg (R$)')
            plt.ylabel('Produtos')
            plt.title(f'Comparação de Preços por Kg - {animal_type}')
            plt.yticks(fontsize=8)  # Reduz o tamanho da fonte dos rótulos no eixo Y
            plt.tight_layout()  # Ajusta automaticamente o layout para evitar cortes
            plt.show()

if __name__ == '__main__':
    plot_data()

