import os
import logging
import pandas as pd
from datetime import datetime
import requests
from dotenv import load_dotenv
from pydantic import BaseModel
from typing import List

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("outputs/extracao.log"),
        logging.StreamHandler()
    ]
)

load_dotenv()

class FredObservation(BaseModel):
    realtime_start: str
    realtime_end: str
    date: str
    value: str

class FredExtractor:
    BASE_URL = "https://api.stlouisfed.org/fred/series/observations"

    def __init__(self):
        self.api_key = os.getenv('FRED_API_KEY')
        if not self.api_key:
            raise ValueError("FRED_API_KEY não encontrada no .env")

    def fetch_series(self, series_id: str, label: str):
        logging.info(f"A iniciar extração de Retalho: {series_id} ({label})")
        params = {
            "series_id": series_id,
            "api_key": self.api_key,
            "file_type": "json"
        }

        try:
            response = requests.get(self.BASE_URL, params=params)
            response.raise_for_status()
            data = response.json()

            observations = [FredObservation(**obs).model_dump() for obs in data['observations']]

            df = pd.DataFrame(observations)
            filename = f'data/fred_{series_id.lower()}_{datetime.now().strftime("%d-%m-%Y")}.csv'
            df.to_csv(filename, index=False, encoding='utf-8')

            logging.info(f'Sucesso: {len(df)} registos guardados em {filename}')
            return filename

        except Exception as e:
            logging.error(f'Erro ao extrair {series_id}: {e}')
            return None

if __name__ == '__main__':
    extractor = FredExtractor()

    series_to_fetch = {
        'RSCCAS': 'Vendas a Retalho: Vestuário e Acessórios',
        'CPIAPPSL': 'Índice de Preços ao Consumidor: Vestuário (Ajustado)'
    }

    print('Extração Macro (Retalho)')
    for sid, name in series_to_fetch.items():
        extractor.fetch_series(sid, name)
