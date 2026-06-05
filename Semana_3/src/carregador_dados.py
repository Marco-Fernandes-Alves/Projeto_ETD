import os
import sqlite3
import pandas as pd
import logging

class ModaDataLoader:
    def __init__(self, db_path="outputs/moda_analytics.db", gold_csv_path="../Semana_2/outputs/ouro_analise_moda.csv"):
        self.db_path = db_path
        self.gold_csv_path = gold_csv_path
        
        os.makedirs(os.path.dirname(self.db_path), exist_ok=True)

    def conectar_db(self):
        """Estabelece ligação ao SQLite com suporte para chaves estrangeiras."""
        conn = sqlite3.connect(self.db_path)
        conn.execute("PRAGMA foreign_keys = ON;")
        return conn

    def criar_esquema(self, conn):
        """Cria o esquema relacional em Estrela (Star Schema) e a View analítica."""
        cursor = conn.cursor()
        
        logging.info("A criar tabelas do Star Schema no SQLite...")

        cursor.execute("DROP TABLE IF EXISTS facto_mercado;")
        cursor.execute("DROP TABLE IF EXISTS dim_sentimento;")
        cursor.execute("DROP TABLE IF EXISTS dim_macroeconomia;")
        cursor.execute("DROP TABLE IF EXISTS dim_tempo;")
        cursor.execute("DROP VIEW IF EXISTS view_analitica_consolidada;")

        cursor.execute("""
        CREATE TABLE IF NOT EXISTS dim_tempo (
            date TEXT PRIMARY KEY,
            ano INTEGER NOT NULL,
            mes INTEGER NOT NULL,
            dia INTEGER NOT NULL,
            dia_semana INTEGER NOT NULL,
            nome_mes TEXT NOT NULL
        );
        """)

        cursor.execute("""
        CREATE TABLE IF NOT EXISTS dim_macroeconomia (
            date TEXT PRIMARY KEY,
            vendas_vestuario REAL NOT NULL,
            inflacao_vestuario REAL NOT NULL,
            FOREIGN KEY (date) REFERENCES dim_tempo (date)
        );
        """)

        cursor.execute("""
        CREATE TABLE IF NOT EXISTS dim_sentimento (
            date TEXT PRIMARY KEY,
            sentiment_score REAL NOT NULL,
            nike_sentiment REAL NOT NULL,
            lvmh_sentiment REAL NOT NULL,
            inditex_sentiment REAL NOT NULL,
            general_sentiment REAL NOT NULL,
            FOREIGN KEY (date) REFERENCES dim_tempo (date)
        );
        """)

        cursor.execute("""
        CREATE TABLE IF NOT EXISTS facto_mercado (
            date TEXT PRIMARY KEY,
            nike_close REAL,
            nike_volume REAL,
            lvmh_close REAL,
            lvmh_volume REAL,
            inditex_close REAL,
            inditex_volume REAL,
            FOREIGN KEY (date) REFERENCES dim_tempo (date),
            FOREIGN KEY (date) REFERENCES dim_macroeconomia (date),
            FOREIGN KEY (date) REFERENCES dim_sentimento (date)
        );
        """)

        cursor.execute("""
        DROP VIEW IF EXISTS view_analitica_consolidada;
        """)
        cursor.execute("""
        CREATE VIEW view_analitica_consolidada AS
        SELECT 
            t.date,
            t.ano,
            t.mes,
            t.nome_mes,
            t.dia_semana,
            m.vendas_vestuario,
            m.inflacao_vestuario,
            s.sentiment_score,
            s.nike_sentiment,
            s.lvmh_sentiment,
            s.inditex_sentiment,
            s.general_sentiment,
            f.nike_close,
            f.nike_volume,
            f.lvmh_close,
            f.lvmh_volume,
            f.inditex_close,
            f.inditex_volume
        FROM facto_mercado f
        JOIN dim_tempo t ON f.date = t.date
        JOIN dim_macroeconomia m ON f.date = m.date
        JOIN dim_sentimento s ON f.date = s.date;
        """)

        cursor.execute("CREATE INDEX IF NOT EXISTS idx_facto_date ON facto_mercado(date);")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_tempo_ano_mes ON dim_tempo(ano, mes);")

        conn.commit()
        logging.info("Tabelas, índices e view analítica criados do zero e prontos para carga!")

    def carregar_dados(self):
        """Carrega os dados transformados do CSV Gold para o Star Schema."""
        if not os.path.exists(self.gold_csv_path):
            logging.error(f"Ficheiro Gold não encontrado em: {self.gold_csv_path}")
            return False

        logging.info(f"A carregar dados a partir de: {self.gold_csv_path}")
        df = pd.read_csv(self.gold_csv_path)
        
        df['date_dt'] = pd.to_datetime(df['date'])
        
        conn = self.conectar_db()
        self.criar_esquema(conn)
        
        try:
            logging.info("A povoar dim_tempo...")
            dias_semana_pt = {0: "Segunda-feira", 1: "Terça-feira", 2: "Quarta-feira", 3: "Quinta-feira", 4: "Sexta-feira", 5: "Sábado", 6: "Domingo"}
            meses_pt = {1: "Janeiro", 2: "Fevereiro", 3: "Março", 4: "Abril", 5: "Maio", 6: "Junho", 7: "Julho", 8: "Agosto", 9: "Setembro", 10: "Outubro", 11: "Novembro", 12: "Dezembro"}
            
            tempo_df = pd.DataFrame({
                'date': df['date'],
                'ano': df['date_dt'].dt.year,
                'mes': df['date_dt'].dt.month,
                'dia': df['date_dt'].dt.day,
                'dia_semana': df['date_dt'].dt.weekday,
                'nome_mes': df['date_dt'].dt.month.map(meses_pt)
            }).drop_duplicates()
            
            tempo_df.to_sql('dim_tempo', conn, if_exists='append', index=False)

            logging.info("A povoar dim_macroeconomia...")
            macro_df = df[['date', 'vendas_vestuario', 'inflacao_vestuario']].drop_duplicates()
            macro_df.to_sql('dim_macroeconomia', conn, if_exists='append', index=False)

            logging.info("A povoar dim_sentimento...")
            sent_df = df[['date', 'sentiment_score', 'nike_sentiment', 'lvmh_sentiment', 'inditex_sentiment', 'general_sentiment']].drop_duplicates()
            sent_df.to_sql('dim_sentimento', conn, if_exists='append', index=False)

            logging.info("A povoar facto_mercado...")
            facto_df = df[['date', 'nike_close', 'nike_volume', 'lvmh_close', 'lvmh_volume', 'inditex_close', 'inditex_volume']].drop_duplicates()
            facto_df.to_sql('facto_mercado', conn, if_exists='append', index=False)

            conn.commit()
            logging.info("Carregamento de dados concluído com sucesso!")
            return True
            
        except Exception as e:
            conn.rollback()
            logging.error(f"Erro durante o carregamento de dados no SQLite: {e}")
            return False
        finally:
            conn.close()

    def realizar_testes_qualidade(self):
        """Executa testes analíticos pós-carga para gerar o relatório de validação."""
        conn = self.conectar_db()
        cursor = conn.cursor()
        
        logging.info("\n==============================================================")
        logging.info("EXECUÇÃO DOS TESTES DE QUALIDADE PÓS-CARGA (VALlDAÇÃO)")
        logging.info("==============================================================")
        
        report = []
        report.append("# 📊 Relatório de Validação Pós-Carga - Semana 3")
        report.append("Este relatório documenta os testes de integridade analítica e consistência pós-carregamento no SQLite.")
        report.append("\n## 1. Contagem de Registos por Tabela")
        
        tabelas = ['dim_tempo', 'dim_macroeconomia', 'dim_sentimento', 'facto_mercado']
        report.append("| Tabela | Contagem de Registos |")
        report.append("| :--- | :---: |")
        
        for t in tabelas:
            cursor.execute(f"SELECT COUNT(*) FROM {t}")
            cnt = cursor.fetchone()[0]
            logging.info(f"Tabela {t}: {cnt} registos carregados.")
            report.append(f"| `{t}` | **{cnt}** |")

        cursor.execute("SELECT COUNT(*) FROM facto_mercado")
        cnt_facto = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM view_analitica_consolidada")
        cnt_view = cursor.fetchone()[0]
        
        logging.info(f"Integridade Referencial (View vs Facto): {cnt_view}/{cnt_facto} registos.")
        report.append("\n## 2. Integridade Referencial & Chaves Estrangeiras")
        if cnt_view == cnt_facto:
            report.append("- ✅ **Sucesso**: O número de registos na View consolidada (`{}`) coincide exatamente com o da Tabela de Factos (`{}`). Nenhuma linha foi perdida por falha de JOIN.".format(cnt_view, cnt_facto))
        else:
            report.append("- ❌ **Erro**: Discrepância na contagem! View: {}, Facto: {}.".format(cnt_view, cnt_facto))

        report.append("\n## 3. Análise de Valores Nulos/Ausentes")
        cursor.execute("SELECT * FROM view_analitica_consolidada WHERE vendas_vestuario IS NULL OR nike_close IS NULL")
        null_rows = len(cursor.fetchall())
        if null_rows == 0:
            report.append("- ✅ **Sucesso**: Não foram encontrados valores nulos em colunas críticas de mercado e indicadores macro na camada analítica.")
        else:
            report.append(f"- ⚠️ **Aviso**: Detetados {null_rows} registos com valores nulos nas colunas críticas.")

        conn.close()
        
        report_path = "relatorio_valida_carga.md"
        with open(report_path, "w", encoding="utf-8") as f:
            f.write("\n".join(report))
            
        logging.info(f"\nRelatório de validação pós-carga gerado em: {report_path}")
        logging.info("==============================================================")

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
    loader = ModaDataLoader()
    if loader.carregar_dados():
        loader.realizar_testes_qualidade()
