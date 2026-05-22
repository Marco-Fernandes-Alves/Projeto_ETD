import os
import sys
import logging

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from transformador import DataCleaner
from sentimento import SentimentAnalyzer
from integrador import DataIntegrator
from validador import DataValidator

def run_semana_2_pipeline():
    os.makedirs("logs", exist_ok=True)

    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler("logs/transformacao.log", mode="w", encoding="utf-8"),
            logging.StreamHandler(sys.stdout)
        ]
    )

    logging.info("INICIANDO O PIPELINE DE TRANSFORMAÇÃO DE DADOS")
    logging.info("==============================================================")

    logging.info("PASSO 1: Limpeza e Padronização de Indicadores & Ações")
    cleaner = DataCleaner(raw_path="data", processed_path="data/processados")
    cleaner.clean_fred_data()
    cleaner.clean_market_data()

    logging.info("PASSO 2: Processamento de Sentimento das Notícias")
    analyzer = SentimentAnalyzer(raw_path="data", processed_path="data/processados")
    analyzer.analyze_sentiment()

    logging.info("PASSO 3: Fusão e Interpolação na Camada Gold")
    integrator = DataIntegrator(processed_path="data/processados")
    integrator.integrar_dados_moda()

    logging.info("PASSO 4: Executando Suite de Qualidade (Validador)")
    validator = DataValidator(path="data/processados", report_file="relatorio_qualidade.md")
    validation_success = validator.validate_all()

    logging.info("==============================================================")
    if validation_success:
        logging.info("PIPELINE DA SEMANA 2 CONCLUÍDO COM SUCESSO!")
    else:
        logging.error("PIPELINE EXECUTADO COM SUCESSO, MAS COM FALHAS DE QUALIDADE DE DADOS!")
    logging.info("==============================================================")

if __name__ == "__main__":
    run_semana_2_pipeline()
