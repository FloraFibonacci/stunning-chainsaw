# 🐾 Petlove Price Tracker

[![Python](https://img.shields.io/badge/Python-3.12-blue.svg)](https://www.python.org/)
[![License: GPL v3](https://img.shields.io/badge/License-GPLv3-blue.svg)](https://www.gnu.org/licenses/gpl-3.0)
[![Status](https://img.shields.io/badge/Status-Concluído-brightgreen.svg)]()

---

Este projeto automatiza a coleta e visualização de preços de rações da marca **N&D** para **gatos** e **cachorros** no site [Petlove](https://www.petlove.com.br). Ele utiliza **Selenium** para web scraping, **SQLite** para persistência dos dados e **Matplotlib** para visualização dos preços por quilo.

## 📂 Estrutura

- `main.py`: Rastreia os preços, filtra os produtos relevantes e grava os dados no banco de dados.
- `plot_data.py`: Lê os dados do banco e gera gráficos de preços por kg.
- `petlove_prices.db`: Banco de dados SQLite onde os dados coletados são armazenados.

## 🧰 Requisitos

- Python 3.8+
- Google Chrome instalado
- ChromeDriver compatível
- Bibliotecas:
  - `selenium`
  - `matplotlib`
  - `sqlite3` (padrão do Python)

Instale os pacotes necessários com:

```bash
pip install selenium matplotlib
```

## ⚙️ Configuração

1. **Baixe o [ChromeDriver](https://sites.google.com/chromium.org/driver/)** e coloque no caminho `/usr/bin/chromedriver`, ou ajuste o caminho no script.

2. Altere o caminho do banco de dados `DB_FILE` se necessário:
```python
DB_FILE = '/home/luca/Petlove/petlove_prices.db'
```

## 🚀 Como Usar

### 1. Coleta de Preços

Rode o script `main.py`:

```bash
python main.py
```

Você pode usar o modo **headless** (sem abrir a interface gráfica do navegador):

```bash
python main.py --headless
```

Esse script:

- Rastreia produtos com "N&D" no nome
- Filtra rações para **gatos adultos castrados** e **cães de porte grande**
- Extrai nome, peso e preço
- Calcula o preço por quilo
- Salva os dados em `petlove_prices.db`
- Evita duplicações para o mesmo dia

### 2. Geração de Gráficos

Rode o script `plot_data.py` para visualizar os dados:

```bash
python plot_data.py
```

Ele exibirá gráficos horizontais de preços por kg separados por tipo (gatos e cachorros).

## 📊 Exemplo de Saída

- Comparação de preços entre diferentes embalagens da marca N&D
- Gráficos organizados por ordem decrescente de preço por kg

## 🗣️ Comentários

Código rodando, mas preciso fazer algumas correções, pois estruturei ele localmente, quando ainda não entendia a lógica do Github.
Quando fiz esse curso ainda não havia aprendido SQL, então não tive uma visão do banco de dados criado. O script me retorna apenas os dados adquiridos no momento em que ele roda. Quero ampliar o escopo para fazer um histórico de cada produto. 

## 📝 Observações

- O script usa seletores CSS específicos que podem quebrar se o layout do site Petlove mudar.
- Produtos são identificados por palavras-chave como `"gato"`, `"adulto"`, `"castrado"` e `"porte grande"`.
- O script foi pensado para fins educacionais ou pessoais.
