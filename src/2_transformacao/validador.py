import os
import pandas as pd
import logging
from typing import Optional
from datetime import date
from pydantic import BaseModel, Field, ValidationError

class FREDModel(BaseModel):
    date: date
    vendas_vestuario: float = Field(gt=0, description="Vendas de retalho de vestuário devem ser positivas")
    inflacao_vestuario: float = Field(gt=0, description="O índice de preços ao consumidor para vestuário deve ser positivo")

class TiingoModel(BaseModel):
    date: date
    close: float = Field(gt=0, description="O valor de fecho da ação deve ser positivo")
    volume: Optional[float] = Field(None, ge=0, description="O volume de negociação deve ser não-negativo")

class SentimentModel(BaseModel):
    date: date
    sentiment_score: float = Field(ge=-10, le=10, description="O score de sentimento deve estar entre -10 e 10")

class GoldModel(BaseModel):
    date: date
    vendas_vestuario: float = Field(gt=0)
    inflacao_vestuario: float = Field(gt=0)
    nike_close: Optional[float] = Field(None, gt=0)
    lvmh_close: Optional[float] = Field(None, gt=0)
    inditex_close: Optional[float] = Field(None, gt=0)
    sentiment_score: float = Field(ge=-10, le=10)

class DataValidator:
    def __init__(self, path="data/processados", report_file="relatorio_qualidade.md"):
        self.path = path
        self.report_file = report_file
        self.log_entries = []

    def log_validation(self, message: str, level=logging.INFO):
        logging.log(level, message)
        self.log_entries.append(message)

    def validate_all(self):
        self.log_validation("==================================================", logging.INFO)
        self.log_validation("INICIANDO SUITE DE VALIDAÇÃO DE QUALIDADE DE DADOS", logging.INFO)
        self.log_validation("==================================================", logging.INFO)
        
        success = True
        
        fred_path = os.path.join(self.path, "indicadores_retalho_limpos.csv")
        if os.path.exists(fred_path):
            self.log_validation("Validação dos Indicadores FRED (Staging)")
            df = pd.read_csv(fred_path)
            if df['date'].duplicated().any():
                self.log_validation("FALHA: Encontradas datas duplicadas no FRED!", logging.ERROR)
                success = False
            else:
                self.log_validation(" Unicidade: Datas de indicadores FRED são 100% únicas.")

            errors = 0
            for idx, row in df.iterrows():
                try:
                    FREDModel(
                        date=row['date'],
                        vendas_vestuario=row['vendas_vestuario'],
                        inflacao_vestuario=row['inflacao_vestuario']
                    )
                except ValidationError as e:
                    errors += 1
                    if errors <= 3:
                        self.log_validation(f" Erro na linha {idx}: {e.json()}", logging.ERROR)
            if errors > 0:
                self.log_validation(f"FALHA: Encontrados {errors} registos inválidos no FRED.", logging.ERROR)
                success = False
            else:
                self.log_validation(f" Schema & Tipos: {len(df)} registos FRED validados com sucesso via Pydantic.")
        else:
            self.log_validation("AVISO: Ficheiro FRED não encontrado para validação.", logging.WARNING)

        self.log_validation("Validação das Ações Tiingo (Staging)")
        tickers = ["nke", "lvmuy", "idexy"]
        for t in tickers:
            t_path = os.path.join(self.path, f"mercado_{t}_limpo.csv")
            if os.path.exists(t_path):
                df = pd.read_csv(t_path)
                if df['date'].duplicated().any():
                    self.log_validation(f"FALHA: Datas duplicadas encontradas para {t.upper()}!", logging.ERROR)
                    success = False
                else:
                    self.log_validation(f" Unicidade {t.upper()}: Datas das ações são únicas.")

                errors = 0
                for idx, row in df.iterrows():
                    try:
                        TiingoModel(
                            date=row['date'],
                            close=row['close'],
                            volume=row['volume'] if not pd.isna(row['volume']) else None
                        )
                    except ValidationError as e:
                        errors += 1
                        if errors <= 3:
                            self.log_validation(f" Erro {t.upper()} linha {idx}: {e.json()}", logging.ERROR)
                if errors > 0:
                    self.log_validation(f" FALHA: Encontrados {errors} registos inválidos para {t.upper()}.", logging.ERROR)
                    success = False
                else:
                    self.log_validation(f" Schema & Tipos {t.upper()}: {len(df)} registos validados com sucesso.")
            else:
                self.log_validation(f"AVISO: Ficheiro de mercado para {t.upper()} não encontrado.", logging.WARNING)

        sent_path = os.path.join(self.path, "sentimento_diario_limpo.csv")
        if os.path.exists(sent_path):
            self.log_validation("Validação de Sentimento Diário (Staging)")
            df = pd.read_csv(sent_path)
            if df['date'].duplicated().any():
                self.log_validation("FALHA: Encontradas datas duplicadas no Sentimento!", logging.ERROR)
                success = False
            else:
                self.log_validation(" Unicidade: Datas dos scores de sentimento são únicas.")

            errors = 0
            for idx, row in df.iterrows():
                try:
                    SentimentModel(
                        date=row['date'],
                        sentiment_score=row['sentiment_score']
                    )
                except ValidationError as e:
                    errors += 1
                    if errors <= 3:
                        self.log_validation(f"Erro sentimento linha {idx}: {e.json()}", logging.ERROR)
            if errors > 0:
                self.log_validation(f"FALHA: Encontrados {errors} registos de sentimento inválidos.", logging.ERROR)
                success = False
            else:
                self.log_validation(f"Schema & Tipos: {len(df)} registos de sentimento validados com sucesso.")

        gold_path = os.path.join(self.path, "ouro_analise_moda.csv")
        if os.path.exists(gold_path):
            self.log_validation("Validação do Dataset Integrado (Camada Gold)")
            df = pd.read_csv(gold_path)
            
            # Unicidade
            if df['date'].duplicated().any():
                self.log_validation("FALHA: Datas duplicadas na Camada Gold!", logging.ERROR)
                success = False
            else:
                self.log_validation("Unicidade: Datas de negócios da Camada Gold são estritamente únicas.")

            # Valores Nulos Críticos
            null_cols = df.columns[df.isnull().any()].tolist()
            if null_cols:
                self.log_validation(f"INFO: Detetados valores nulos nas colunas: {null_cols} (Serão validados via Pydantic como opcionais).", logging.INFO)

            # Pydantic
            errors = 0
            for idx, row in df.iterrows():
                try:
                    GoldModel(
                        date=row['date'],
                        vendas_vestuario=row['vendas_vestuario'],
                        inflacao_vestuario=row['inflacao_vestuario'],
                        nike_close=row['nike_close'] if not pd.isna(row['nike_close']) else None,
                        lvmh_close=row['lvmh_close'] if not pd.isna(row['lvmh_close']) else None,
                        inditex_close=row['inditex_close'] if not pd.isna(row['inditex_close']) else None,
                        sentiment_score=row['sentiment_score']
                    )
                except ValidationError as e:
                    errors += 1
                    if errors <= 3:
                        self.log_validation(f"Erro Gold linha {idx}: {e.json()}", logging.ERROR)
            if errors > 0:
                self.log_validation(f"FALHA: Encontrados {errors} registos inválidos na Camada Gold.", logging.ERROR)
                success = False
            else:
                self.log_validation(f"Schema & Sanidade Gold: {len(df)} registos consolidados validados e aprovados.")
        else:
            self.log_validation("ERRO: Tabela Gold final não encontrada em: " + gold_path, logging.ERROR)
            success = False

        self.log_validation("==================================================", logging.INFO)
        if success:
            self.log_validation("RESULTADO DO PIPELINE: APROVADO! Todos os dados cumprem os critérios de qualidade.", logging.INFO)
        else:
            self.log_validation("RESULTADO DO PIPELINE: REPROVADO! Foram encontradas anomalias nos dados.", logging.ERROR)
        self.log_validation("==================================================", logging.INFO)

        self._write_report_markdown(success)
        return success

    def _write_report_markdown(self, success: bool):
        os.makedirs(os.path.dirname(os.path.abspath(self.report_file)), exist_ok=True)
        
        status_banner = "> [!NOTE]\n> **Estado Geral do Pipeline de Qualidade**: " + ("**APROVADO**" if success else "**REPROVADO**")
        
        with open(self.report_file, "w") as f:
            f.write(f"""# Relatório de Qualidade de Dados

{status_banner}

## Resumo das Validações Executadas

Esta auditoria inspeciona automaticamente a sanidade, integridade e coerência estrutural dos dados intermédios (Staging) e finais (Gold) da Semana 2 do projeto **TF_ETD**.

### Regras de Qualidade Implementadas:
1. **Unicidade de Chave Primária**: Garantia de que a coluna de data não apresenta registos duplicados em nenhuma fonte.
2. **Conformidade de Esquema (Schema)**: Validação estrita de tipos de dados (Datas válidas, floats numéricos) utilizando os modelos de dados **Pydantic**.
3. **Restrições de Domínio & Sanidade**: 
   - Preço de fecho de ações (`close`) e volume devem ser estritamente maiores que zero.
   - Vendas de retalho de vestuário e inflação de vestuário (FRED) devem ser positivas.
   - O score de sentimento diário das notícias deve estar contido no intervalo fechado de `[-10.0, 10.0]`.

---

## 🪵 Registo Completo da Auditoria (Logs do Validador)

```text
""" + "\n".join(self.log_entries) + """
```

---

## 🛠️ Anomalias Identificadas & Decisões de Limpeza

| Fonte | Problema Encontrado | Gravidade | Ação de Reparação / Decisão Técnica |
| :--- | :--- | :--- | :--- |
| **FRED (Indicadores)** | Granularidade mensal (apenas dia 1 de cada mês). *Inner joins* diretos colapsavam o dataset final para 6 registos. | Média | **Interpolação Temporal**: Foi efetuada uma reamostragem diária do calendário combinando os dias das ações e aplicando *Forward Fill* (`ffill`) para propagar o último dado económico conhecido. |
| **Tiingo (Ações)** | Fins de semana e feriados sem negociação originavam nulos em `close` caso mantivéssemos o calendário completo. | Baixa | **Filtro de Calendário de Negócios**: Remoção de linhas de fins-de-week utilizando `dropna(how='all')` nos valores de fecho das 3 marcas. |
| **NewsAPI (Notícias)** | Dias sem nenhuma notícia recolhida sobre moda/luxo/sustentabilidade causavam valores nulos no merge final. | Baixa | **Tratamento de Nulos**: Preenchimento automático dos sentimentos nulos com score neutro (`0.0`). |
| **Geral (Duplicados)** | Registos de datas duplicadas podem surgir por anomalias nas chamadas das APIs na extração. | Alta | **Remoção de Duplicados**: Lógica integrada de `drop_duplicates(subset=['date'])` nos scripts de limpeza. |

""")
            
if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
    validator = DataValidator()
    validator.validate_all()
