import os
import pandas as pd
import logging

class DataCleaner:
    def __init__(self, raw_path="data/raw", processed_path="data/processados"):
        self.raw_path = raw_path
        self.processed_path = processed_path
        os.makedirs(self.processed_path, exist_ok=True)

    def clean_fred_data(self):
        logging.info("A processar indicadores de retalho (FRED)...")
        
        fred_files = [f for f in os.listdir(self.raw_path) if f.startswith("fred_") and f.endswith(".csv")]
        
        if not fred_files:
            logging.warning("Nenhum ficheiro FRED encontrado em: %s", self.raw_path)
            return None

        mapping = {
            "rsccas": "vendas_vestuario",
            "cpiappsl": "inflacao_vestuario",
            "gdp": "pib"
        }

        dfs = []
        for f in fred_files:
            indicator_id = f.split("_")[1]
            col_name = mapping.get(indicator_id, indicator_id)

            df = pd.read_csv(os.path.join(self.raw_path, f))
            if 'date' not in df.columns or 'value' not in df.columns:
                logging.error(f"Ficheiro {f} sem as colunas 'date' ou 'value'")
                continue
                
            df = df[['date', 'value']]
            df['value'] = pd.to_numeric(df['value'], errors='coerce')
            df['date'] = pd.to_datetime(df['date'])
            df = df.rename(columns={'value': col_name})
            dfs.append(df.set_index('date'))

        if not dfs:
            logging.error("Nenhum dado FRED foi limpo com sucesso.")
            return None

        final_df = pd.concat(dfs, axis=1).sort_index()
        final_df = final_df.ffill().dropna()

        output_file = os.path.join(self.processed_path, "indicadores_retalho_limpos.csv")
        final_df.to_csv(output_file)
        logging.info(f"Dados macroeconómicos FRED limpos e guardados em: {output_file}")
        return final_df

    def clean_market_data(self):
        logging.info("A processar dados de marcas de moda (Tiingo)...")
        market_files = [f for f in os.listdir(self.raw_path) if f.startswith("tiingo_") and f.endswith(".csv")]

        if not market_files:
            logging.warning("Nenhum ficheiro Tiingo encontrado em: %s", self.raw_path)
            return

        for f in market_files:
            ticker = f.split("_")[1]
            df = pd.read_csv(os.path.join(self.raw_path, f))
            
            if 'date' not in df.columns or 'close' not in df.columns:
                logging.error(f"Ficheiro {f} sem colunas 'date' ou 'close'")
                continue
                
            df['date'] = pd.to_datetime(df['date']).dt.date
            df = df.drop_duplicates(subset=['date'])
            
            df['close'] = pd.to_numeric(df['close'], errors='coerce')
            df['open'] = pd.to_numeric(df.get('open'), errors='coerce')
            df['high'] = pd.to_numeric(df.get('high'), errors='coerce')
            df['low'] = pd.to_numeric(df.get('low'), errors='coerce')
            df['volume'] = pd.to_numeric(df.get('volume'), errors='coerce')

            output_file = os.path.join(self.processed_path, f"mercado_{ticker}_limpo.csv")
            df.to_csv(output_file, index=False)
            logging.info(f"Dados de mercado da marca {ticker.upper()} limpos e guardados em: {output_file}")

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
    cleaner = DataCleaner()
    cleaner.clean_fred_data()
    cleaner.clean_market_data()
