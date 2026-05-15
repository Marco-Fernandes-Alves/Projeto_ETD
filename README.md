# 👗 TF_ETD: Fashion Retail & Industry Intelligence
*Projeto Prático de ETL, Engenharia de Dados & Visualização Analítica*

## 🎯 Objetivo
Análise integrada do setor da **Moda**, cruzando indicadores macroeconómicos de consumo (FRED), performance de mercado de gigantes globais como Nike e LVMH (Tiingo) e o sentimento mediático sobre tendências e sustentabilidade (NewsAPI).

## 🏗️ Estrutura do Projeto (Organização por Semanas)

### 📂 [1_extracao](src/1_extracao/)
- **Scripts:** Coleta de dados via APIs (FRED, Tiingo, NewsAPI).
- **Dados:** CSVs brutos de vendas, ações e notícias.

## 🚀 Como Executar
1. Instalar dependências: `pip install -r requirements.txt`
2. Mudar o nome do ficheiro `.env.example` para `.env` e adicionar as chaves API que serão submetidas ao Docente junto com o link para este repositório no Moodle.
3. Correr os scripts de extração:
   ```bash
   python src/1_extracao/scripts/extrator_fred.py
   python src/1_extracao/scripts/extrator_tiingo.py
   python src/1_extracao/scripts/extrator_noticias.py
   ```
4. Correr os scripts de validação:
   ```bash
   python src/1_extracao/scripts/validar_apis.py
   ```
5. Verificar os logs para confirmar que tudo correu bem:
   ```bash
   cat logs/extracao.log
   ```

## 🛠️ Tecnologias
- **Linguagem:** Python 3.14 (Localização: pt-PT)
- **Engenharia:** Pandas, Pydantic, SQLite