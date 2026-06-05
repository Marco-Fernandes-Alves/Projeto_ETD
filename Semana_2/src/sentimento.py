import os
import pandas as pd
import logging

class SentimentAnalyzer:
    def __init__(self, raw_path="data/raw", processed_path="data/processados"):
        self.raw_path = raw_path
        self.processed_path = processed_path
        os.makedirs(self.processed_path, exist_ok=True)

    def analyze_sentiment(self):
        logging.info("A analisar o sentimento das notícias...")

        news_files = [f for f in os.listdir(self.raw_path) if f.startswith("noticias_") and f.endswith(".csv")]

        if not news_files:
            logging.warning("Nenhum ficheiro de notícias encontrado em: %s", self.raw_path)
            return None

        positive_keywords = ['growth', 'rise', 'recovery', 'gain', 'strong', 'positive', 'bull', 'sustainable', 'eco-friendly', 'innovative']
        negative_keywords = ['inflation', 'fall', 'crisis', 'drop', 'weak', 'negative', 'bear', 'risk', 'fear', 'scandal', 'waste', 'pollution']
        
        def get_score(text):
            text = str(text).lower()
            score = 0.0
            for k in positive_keywords:
                if k in text: score += 1.0
            for k in negative_keywords:
                if k in text: score -= 1.0
            return score

        nike_words = ['nike', 'nke', 'jordan', 'converse']
        lvmh_words = ['lvmh', 'lvmuy', 'vuitton', 'dior', 'luxury', 'fendi', 'givenchy', 'celine', 'hennessy']
        inditex_words = ['inditex', 'zara', 'idexy', 'pull&bear', 'bershka', 'massimo', 'stradivarius']

        def get_brand(text):
            text = str(text).lower()
            if any(w in text for w in nike_words):
                return 'nike'
            elif any(w in text for w in lvmh_words):
                return 'lvmh'
            elif any(w in text for w in inditex_words):
                return 'inditex'
            return 'general'

        all_news = []
        for f in news_files:
            try:
                df = pd.read_csv(os.path.join(self.raw_path, f))
                if 'publishedAt' not in df.columns:
                    logging.error(f"Ficheiro {f} sem coluna necessária 'publishedAt'")
                    continue
                
                if 'overall_sentiment' not in df.columns:
                    logging.info(f"Ficheiro clássico {f} detetado. A enriquecer com NLP léxico clássico...")
                    if 'title' not in df.columns:
                        logging.error(f"Ficheiro clássico {f} sem coluna 'title'. Ignorado.")
                        continue
                    
                    df['overall_sentiment'] = df['title'].apply(get_score)
                    df['brand'] = df['title'].apply(get_brand)
                    
                    df['nike_sentiment'] = 0.0
                    df['nike_relevance'] = 0.0
                    df['lvmh_sentiment'] = 0.0
                    df['lvmh_relevance'] = 0.0
                    df['inditex_sentiment'] = 0.0
                    df['inditex_relevance'] = 0.0
                    
                    for idx, row in df.iterrows():
                        brand = row['brand']
                        score = row['overall_sentiment']
                        if brand == 'nike':
                            df.at[idx, 'nike_sentiment'] = score
                            df.at[idx, 'nike_relevance'] = 1.0
                        elif brand == 'lvmh':
                            df.at[idx, 'lvmh_sentiment'] = score
                            df.at[idx, 'lvmh_relevance'] = 1.0
                        elif brand == 'inditex':
                            df.at[idx, 'inditex_sentiment'] = score
                            df.at[idx, 'inditex_relevance'] = 1.0

                all_news.append(df)
            except Exception as e:
                logging.error(f"Erro ao ler/processar ficheiro {f}: {e}")

        if not all_news:
            logging.error("Nenhuma notícia válida para processar.")
            return None

        combined_news = pd.concat(all_news, ignore_index=True)
        combined_news['date'] = pd.to_datetime(combined_news['publishedAt'], format='mixed', utc=True).dt.date

        logging.info("A aplicar cálculo de médias ponderadas de sentimento segmentado por marca...")
        
        daily_records = []
        for d, group in combined_news.groupby('date'):
            global_sent = group['overall_sentiment'].mean()
            
            nike_rel_sum = group.get('nike_relevance', pd.Series([0.0]*len(group))).sum()
            if nike_rel_sum > 0:
                nike_sent = (group['nike_sentiment'] * group['nike_relevance']).sum() / nike_rel_sum
            else:
                nike_sent = 0.0
                
            lvmh_rel_sum = group.get('lvmh_relevance', pd.Series([0.0]*len(group))).sum()
            if lvmh_rel_sum > 0:
                lvmh_sent = (group['lvmh_sentiment'] * group['lvmh_relevance']).sum() / lvmh_rel_sum
            else:
                lvmh_sent = 0.0
                
            inditex_rel_sum = group.get('inditex_relevance', pd.Series([0.0]*len(group))).sum()
            if inditex_rel_sum > 0:
                inditex_sent = (group['inditex_sentiment'] * group['inditex_relevance']).sum() / inditex_rel_sum
            else:
                inditex_sent = 0.0
                
            nike_rel_col = group.get('nike_relevance', pd.Series([0.0]*len(group)))
            lvmh_rel_col = group.get('lvmh_relevance', pd.Series([0.0]*len(group)))
            inditex_rel_col = group.get('inditex_relevance', pd.Series([0.0]*len(group)))
            
            general_group = group[(nike_rel_col == 0) & (lvmh_rel_col == 0) & (inditex_rel_col == 0)]
            if len(general_group) > 0:
                general_sent = general_group['overall_sentiment'].mean()
            else:
                general_sent = 0.0
                
            daily_records.append({
                'date': d,
                'sentiment_score': global_sent,
                'nike_sentiment': nike_sent,
                'lvmh_sentiment': lvmh_sent,
                'inditex_sentiment': inditex_sent,
                'general_sentiment': general_sent
            })
            
        daily_sentiment = pd.DataFrame(daily_records)

        output_file = os.path.join(self.processed_path, "sentimento_diario_limpo.csv")
        daily_sentiment = daily_sentiment.sort_values('date').reset_index(drop=True)
        daily_sentiment.to_csv(output_file, index=False)
        logging.info(f"Sentimento diário segmentado por marcas processado e guardado em: {output_file}")
        return daily_sentiment

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
    analyzer = SentimentAnalyzer()
    analyzer.analyze_sentiment()
