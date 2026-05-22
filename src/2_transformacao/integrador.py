import os
import pandas as pd
import logging

class DataIntegrator:
    def __init__(self, processed_path="data/processados"):
        self.processed_path = processed_path

    def integrar_dados_moda(self):
        logging.info("A iniciar integração da Camada Gold (Moda & Mercados)...")

        # 1. Carregar dados limpos
        path = self.processed_path
        
        try:
            retalho = pd.read_csv(os.path.join(path, "indicadores_retalho_limpos.csv"))
            nke = pd.read_csv(os.path.join(path, "mercado_nke_limpo.csv"))
            lvmh = pd.read_csv(os.path.join(path, "mercado_lvmuy_limpo.csv"))
            idexy = pd.read_csv(os.path.join(path, "mercado_idexy_limpo.csv"))
            
            # O sentimento é opcional mas recomendado
            sentimento_path = os.path.join(path, "sentimento_diario_limpo.csv")
            sentimento = pd.read_csv(sentimento_path) if os.path.exists(sentimento_path) else None
        except Exception as e:
            logging.error(f"Erro ao carregar ficheiros intermédios de processamento: {e}")
            return None

        # 2. Converter colunas de data para datetime
        retalho['date'] = pd.to_datetime(retalho['date'])
        nke['date'] = pd.to_datetime(nke['date'])
        lvmh['date'] = pd.to_datetime(lvmh['date'])
        idexy['date'] = pd.to_datetime(idexy['date'])
        
        if sentimento is not None:
            sentimento['date'] = pd.to_datetime(sentimento['date'])

        # 3. Criar uma base diária unificada a partir das datas das ações
        # Usamos o período que cobre todos os dados das ações
        min_date = min(nke['date'].min(), lvmh['date'].min(), idexy['date'].min())
        max_date = max(nke['date'].max(), lvmh['date'].max(), idexy['date'].max())
        
        logging.info(f"Intervalo temporal do pipeline Gold: {min_date.date()} até {max_date.date()}")
        
        # Gerar calendário diário completo
        calendario = pd.DataFrame({'date': pd.date_range(start=min_date, end=max_date)})

        # 4. Interpolação inteligente dos dados macroeconómicos do FRED (mensais)
        # Fundimos os dados mensais com o calendário diário e propagamos com forward fill (ffill)
        retalho_diario = pd.merge(calendario, retalho, on='date', how='left')
        # Ordenamos e aplicamos ffill e bfill para preencher quaisquer NaNs residuais nas pontas
        retalho_diario = retalho_diario.sort_values('date').ffill().bfill()


        # 5. Cruzamento das marcas de moda (dados diários de mercado)
        # Selecionamos apenas as colunas de fecho e volume para simplificar a camada analítica final
        nke_sub = nke[['date', 'close', 'volume']].rename(columns={'close': 'nike_close', 'volume': 'nike_volume'})
        lvmh_sub = lvmh[['date', 'close', 'volume']].rename(columns={'close': 'lvmh_close', 'volume': 'lvmh_volume'})
        idexy_sub = idexy[['date', 'close', 'volume']].rename(columns={'close': 'inditex_close', 'volume': 'inditex_volume'})

        # Fazemos left joins sucessivos sobre o calendário diário
        gold_df = pd.merge(calendario, retalho_diario, on='date', how='left')
        gold_df = pd.merge(gold_df, nke_sub, on='date', how='left')
        gold_df = pd.merge(gold_df, lvmh_sub, on='date', how='left')
        gold_df = pd.merge(gold_df, idexy_sub, on='date', how='left')

        # 6. Cruzamento do Sentimento de Notícias Diário (se disponível)
        if sentimento is not None:
            gold_df = pd.merge(gold_df, sentimento, on='date', how='left')
            # Preencher dias sem notícias com sentimento neutro (0.0)
            gold_df['sentiment_score'] = gold_df['sentiment_score'].fillna(0.0)

        # 7. Limpeza final: remover fins de semana onde não há negociação de nenhuma marca (todas as ações são nulas)
        # Isto limpa os dados deixando apenas dias úteis / dias de negociação
        gold_df = gold_df.dropna(subset=['nike_close', 'lvmh_close', 'inditex_close'], how='all')

        # Garantir ordenação temporal
        gold_df = gold_df.sort_values('date').reset_index(drop=True)

        output_file = os.path.join(path, "ouro_analise_moda.csv")
        gold_df.to_csv(output_file, index=False)
        logging.info(f"Dataset FINAL Gold gerado com SUCESSO: {len(gold_df)} registos integrados.")
        logging.info(f"Ficheiro de saída: {output_file}")
        
        # Mostrar exemplo
        logging.info("\nAmostra dos dados finais integrados (Gold):")
        print(gold_df.tail())
        
        return gold_df

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
    integrator = DataIntegrator()
    integrator.integrar_dados_moda()
