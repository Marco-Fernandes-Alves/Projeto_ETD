import os
import pandas as pd
import logging

class SentimentAnalyzer:
    def __init__(self, raw_path="data", processed_path="data/processados"):
        self.raw_path = raw_path
        self.processed_path = processed_path
        os.makedirs(self.processed_path, exist_ok=True)

    def analyze_sentiment(self):
        logging.info("A analisar o sentimento das notícias...")

        news_files = [f for f in os.listdir(self.raw_path) if f.startswith("noticias_") and f.endswith(".csv")]

        if not news_files:
            logging.warning("Nenhum ficheiro de notícias encontrado em: %s", self.raw_path)
            return None

        # Léxicos de sentimento para marcas/setor de moda
        positive_keywords = ['growth', 'rise', 'recovery', 'gain', 'strong', 'positive', 'bull', 'sustainable', 'eco-friendly', 'innovative']
        negative_keywords = ['inflation', 'fall', 'crisis', 'drop', 'weak', 'negative', 'bear', 'risk', 'fear', 'scandal', 'waste', 'pollution']

        all_news = []
        for f in news_files:
            df = pd.read_csv(os.path.join(self.raw_path, f))
            if 'publishedAt' not in df.columns or 'title' not in df.columns:
                logging.error(f"Ficheiro {f} sem colunas necessárias 'publishedAt' ou 'title'")
                continue
            all_news.append(df)

        if not all_news:
            logging.error("Nenhuma notícia processada.")
            return None

        combined_news = pd.concat(all_news)
        combined_news['publishedAt'] = pd.to_datetime(combined_news['publishedAt']).dt.date

        def get_score(text):
            text = str(text).lower()
            score = 0
            for k in positive_keywords:
                if k in text: score += 1
            for k in negative_keywords:
                if k in text: score -= 1
            return score

        combined_news['sentiment_score'] = combined_news['title'].apply(get_score)

        # Agrupa pelo dia de publicação e tira a média do sentimento
        daily_sentiment = combined_news.groupby('publishedAt')['sentiment_score'].mean().reset_index()
        daily_sentiment = daily_sentiment.rename(columns={'publishedAt': 'date'})

        output_file = os.path.join(self.processed_path, "sentimento_diario_limpo.csv")
        daily_sentiment.to_csv(output_file, index=False)
        logging.info(f"Sentimento diário processado e guardado em: {output_file}")
        return daily_sentiment

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
    analyzer = SentimentAnalyzer()
    analyzer.analyze_sentiment()
