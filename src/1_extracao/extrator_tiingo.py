import os
import logging
from datetime import datetime, timedelta
import requests
import pandas as pd
from dotenv import load_dotenv
from pydantic import BaseModel
from typing import List


logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/extracao.log'),
        logging.StreamHandler()
    ]
)

load_dotenv()

class TiingoPrice(BaseModel):
    date: str
    close: float
    high: float
    low: float
    open: float
    volume: float

class TiingoExtractor:
    BASE_URL = 'https://api.tiingo.com/tiingo/daily/{ticker}/prices'

    def __init__(self):
        self.api_key = os.getenv('TIINGO_API_KEY')
        if not self.api_key:
            raise ValueError('TIINGO_API_KEY não encontrada no .env')

    def fetch_fashion_stocks(self, ticker: str, days: int = 500):
        logging.info(f'A extrair dados de mercado para marca: {ticker}')

        start_date = (datetime.now() - timedelta(days=days)).strftime('%Y-%m-%d')
        headers = {'Content-Type': 'application/json', 'Authorization': f'Token {self.api_key}'}
        url = self.BASE_URL.format(ticker=ticker)
        params = {'startDate': start_date, 'resampleFreq': 'daily'}

        try:
            response = requests.get(url, headers=headers, params=params)
            response.raise_for_status()
            data = response.json()

            prices = [TiingoPrice(**p).model_dump() for p in data]
            df = pd.DataFrame(prices)
            filename = f'src/1_extracao/data/tiingo_{ticker.lower()}_{datetime.now().strftime('%d-%m-%Y')}.csv'
            df.to_csv(filename, index=False, encoding='utf-8')

            logging.info(f' Sucesso: {len(df)} registos de {ticker} guardados.')
            return filename

        except Exception as e:
            logging.error(f' Erro ao extrair stock de {ticker}: {e}')
            return None

if __name__ == '__main__':
    extractor = TiingoExtractor()


    tickers = ['NKE', 'IDEXY', 'LVMUY']

    print('Extração de Ações (Retalho de Moda)')
    for ticker in tickers:
        extractor.fetch_fashion_stocks(ticker)
