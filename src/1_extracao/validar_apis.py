import os
import requests
from dotenv import load_dotenv


load_dotenv()

def test_fred():
    api_key = os.getenv('FRED_API_KEY')
    url = f'https://api.stlouisfed.org/fred/series?series_id=GNPCA&api_key={api_key}&file_type=json'
    try:
        response = requests.get(url)
        if response.status_code == 200:
            print('FRED API: Conexão bem-sucedida.')
            
        else:
            print(f'FRED API: Erro {response.status_code}')

    except Exception as e:
        print(f'FRED API: Falha - {e}')

def test_news_api():
    api_key = os.getenv('NEWS_API_KEY')
    url = f'https://newsapi.org/v2/top-headlines?category=business&apiKey={api_key}'
    try:
        response = requests.get(url)
        if response.status_code == 200:
            print('NewsAPI: Conexão bem-sucedida.')

        else:
            print(f'NewsAPI: Erro {response.status_code}')

    except Exception as e:
        print(f'NewsAPI: Falha - {e}')

def test_exchangerate():
    api_key = os.getenv('EXCHANGERATE_API_KEY')
    url = f'https://v6.exchangerate-api.com/v6/{api_key}/latest/USD'
    try:
        response = requests.get(url)
        if response.status_code == 200:
            print(' ExchangeRate API: Conexão bem-sucedida.')

        else:
            print(f' ExchangeRate API: Erro {response.status_code}')

    except Exception as e:
        print(f' ExchangeRate API: Falha - {e}')

if __name__ == '__main__':
    print('Validando Chaves de API')
    test_fred()
    test_news_api()
    test_exchangerate()
