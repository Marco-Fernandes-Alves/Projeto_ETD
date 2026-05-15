import os
import logging
import pandas as pd
from datetime import datetime
import requests
from dotenv import load_dotenv
from pydantic import BaseModel
from typing import List, Optional


logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("logs/extracao.log"),
        logging.StreamHandler()
    ]
)

load_dotenv()

class NewsArticle(BaseModel):
    source_name: str
    author: Optional[str] = None
    title: str
    description: Optional[str] = None
    url: str
    publishedAt: str

class NewsExtractor:
    BASE_URL = 'https://newsapi.org/v2/everything'

    def __init__(self):
        self.api_key = os.getenv('NEWS_API_KEY')
        if not self.api_key:
            raise ValueError('NEWS_API_KEY não encontrada no .env')

    def fetch_news(self, query: str, label: str):
        logging.info(f'A recolher notícias de Moda: {query}')
        params = {
            'q': query,
            'apiKey': self.api_key,
            'language': 'en',
            'sortBy': 'publishedAt',
            'pageSize': 50
        }

        try:
            response = requests.get(self.BASE_URL, params=params)
            response.raise_for_status()
            data = response.json()

            articles_data = []
            for art in data['articles']:
                art_copy = art.copy()
                art_copy['source_name'] = art.get('source', {}).get('name', 'Unknown')
                validated_art = NewsArticle(**art_copy)
                articles_data.append(validated_art.model_dump())

            df = pd.DataFrame(articles_data)
            filename = f'src/1_extracao/data/noticias_{label.lower().replace(' ', '_')}_{datetime.now().strftime('%d-%m-%Y')}.csv'
            df.to_csv(filename, index=False, encoding='utf-8')

            logging.info(f'Sucesso: {len(df)} notícias de moda guardadas.')
            return filename

        except Exception as e:
            logging.error(f' Erro na NewsAPI: {e}')
            return None

if __name__ == '__main__':
    extractor = NewsExtractor()


    queries = {
        'fashion retail trends': 'Tendencias_Moda',
        'luxury apparel market': 'Mercado_Luxo',
        'fast fashion sustainability': 'Sustentabilidade_Moda'
    }

    print('Extração de Notícias (Indústria da Moda)')
    for query, label in queries.items():
        extractor.fetch_news(query, label)
