# 👗 TF_ETD: Fashion Retail & Industry Intelligence
*Trabalho Final Prático de ETL, Engenharia de Dados & Visualização Analítica*  
*Universidade da Beira Interior (UBI)*

---

## 🎯 Apresentação do Projeto
O **TF_ETD** é uma plataforma de engenharia de dados de ponta a ponta focada no setor da **Moda e Retalho de Luxo**. O sistema captura e cruza dados macroeconómicos de consumo americano (FRED), dados financeiros diários das maiores multinacionais do setor (Nike, LVMH, Inditex/Zara via Tiingo API) e a perceção mediática da sociedade civil sobre tendências e sustentabilidade (NewsAPI / Alpha Vantage).

O pipeline higieniza estes dados em Staging, unifica-os de forma inteligente na camada Gold, estrutura-os num **Star Schema** relacional no SQLite e serve-os num painel de visualização interativo Streamlit com design Bento Grid premium.

---

## 🏗️ Arquitetura de Dados de Ponta a Ponta

O fluxo de dados foi concebido em 4 etapas perfeitamente articuladas, estruturadas sob uma taxonomia de pastas simplificada e simétrica para garantir que não há duplicação desnecessária de ficheiros:

```text
               🔌 FONTES DE DADOS (API Ingestion)
     ┌───────────────────┬───────────────────┐
     │                   │                   │
  FRED API          Tiingo API        NewsAPI / Alpha
 (Consumo/IPC)    (Ações: NKE, LVMH,      Vantage
                       Zara)             (Notícias)
     │                   │                   │
     └─────────┬─────────┴─────────┬─────────┘
               │                   │
               ▼                   ▼
     📂 SEMANA 1: EXTRAÇÃO & INGESTÃO (Bronze Layer)
     ├─ Scripts de Extração (Pydantic validated)
     ├─ data/ (Ficheiros CSV brutos: fred_*, tiingo_*, noticias_*)
     └─ outputs/extracao.log
               │
               ▼
     📂 SEMANA 2: TRANSFORMAÇÃO & QUALIDADE (Silver -> Gold Layer)
     ├─ Limpeza & Padronização
     ├─ Análise de Sentimento Léxico (VADER)
     ├─ Fusão & Interpolação Temporal (FRED Mensal -> Diário)
     ├─ Validação de Schema (Suite de Data Quality com Pydantic)
     └─ outputs/ (ouro_analise_moda.csv, relatorio_qualidade.md)
               │
               ▼
     📂 SEMANA 3: MODELAGEM & CARREGAMENTO (Relational Layer)
     ├─ Desenho do Star Schema (1 Facto, 3 Dimensões)
     ├─ Carregador de Dados (SQLite: moda_analytics.db)
     └─ View Analítica Consolidada (com Índices Otimizados)
               │
               ▼ (Cópia preventiva no arranque)
     📂 SEMANA 4: VISUALIZAÇÃO ANALÍTICA (Presentation Layer)
     ├─ Streamlit App (Estética Bento Grid Premium)
     └─ Gráficos Interativos Plotly (Base 100, Correlação OLS)
```

---

## 📂 Estrutura do Repositório (Organização por Semanas)

O repositório está estruturado de forma simétrica e modular por semanas para facilitar a verificação independente de cada módulo:

```text
TF_ETD/
├── .env.example                # Variáveis de ambiente com chaves de API locais
├── README.md                   # Documentação consolidada (Dicionário e Relatório Final)
├── requirements.txt            # Dependências globais do repositório
│
├── Semana_1/                   # EXTRAÇÃO & INGESTÃO (Bronze Layer)
│   ├── data/                   # Ficheiros CSV puros importados das APIs
│   ├── outputs/extracao.log    # Registo de logs de chamadas
│   └── src/                    # Scripts de ingestão (FRED, Tiingo, NewsAPI) e validação
│
├── Semana_2/                   # TRANSFORMAÇÃO (Silver & Gold Layer)
│   ├── outputs/                # Ficheiros limpos, logs e dataset Gold (ouro_analise_moda.csv)
│   │   ├── relatorio_qualidade.md # Auditoria de dados via Pydantic
│   │   └── transformacao.log   # Registo da execução da transformação e sentimento
│   └── src/                    # Limpeza, sentimento, interpolação e integrador Gold
│
├── Semana_3/                   # CARREGAMENTO RELACIONAL (SQLite Layer)
│   ├── outputs/                # Base relacional final e relatórios pós-carga
│   │   ├── moda_analytics.db   # SQLite preenchido sob Star Schema
│   │   └── relatorio_valida_carga.md # Auditoria SQL e testes de FK/Nulos
│   └── src/                    # Converte o CSV Gold em tabelas SQLite e View consolidada
│
└── Semana_4/                   # VISUALIZAÇÃO (Presentation Layer)
    ├── src/app.py              # Aplicação do dashboard interativo Streamlit
    └── outputs/                # Base de dados local (cópia autónoma para o professor)
```

---

## 🚀 Como Executar o Pipeline

O projeto oferece flexibilidade total: pode correr o pipeline completo a partir da raiz com um único comando ou aceder a cada semana e executá-la autonomamente.

### Requisito Prévio: Instalação das Dependências Globais
```bash
pip install -r requirements.txt
```

### Método 1: Execução Global Unificada (Recomendado)
Para executar toda a lógica de transformação, limpeza, cálculo de sentimento, validação Pydantic, modelagem e carregamento no SQLite, corra a partir da raiz do repositório:
```bash
python run_pipeline.py
```
*Este comando limpará a base de dados SQLite, reprocessará as fontes e deixará a base de dados em `Semana_3/outputs/moda_analytics.db` no estado perfeito de produção.*

### Método 2: Execução por Semanas Individuais
Consulte o ficheiro `README.md` localizado no diretório de cada semana para obter instruções atómicas detalhadas sobre como executar cada etapa isoladamente.

---

## 🎨 Como Lançar o Dashboard Analítico (Semana 4)
Para desfrutar do painel de controlo interativo com gráficos Plotly e métricas analíticas Bento, execute a partir da raiz:
```bash
streamlit run Semana_4/src/app.py
```
Ou navegue até à pasta `Semana_4` e execute `streamlit run src/app.py`.  
O Streamlit abrirá uma janela no seu browser padrão em `http://localhost:8501`.

---

## 🛠️ Stack Tecnológica & Padrões de Engenharia
*   **Linguagem**: Python 3.14 (Localização nativa: pt-PT)
*   **Armazenamento**: SQLite 3 (Com suporte para integridade referencial PRAGMA e colunas nulas otimizadas para acomodar calendários de bolsas sobrepostos)
*   **Segurança**: Variáveis de ambiente isoladas em `.env` via `python-dotenv`
*   **Data Quality**: Validação estrita de tipos com `pydantic`
*   **Manipulação de Séries**: `pandas` e interpolação inteligente com `ffill()` / `bfill()`
*   **Visualização**: `streamlit` e `plotly` (Gráficos baseados em templates escuros personalizados e slider de foco automático dinâmico no primeiro sentimento válido)

---

## 🤖 Uso de IA & Transparência
Este projeto foi codesenvolvido utilizando técnicas avançadas de IA e Prompt Engineering em regime de pair-programming. Toda a metodologia, logs de prompts e critérios de validação humana encontram-se documentados no ficheiro [REGISTO_IA.md](file:///home/alves7174/Documents/UBI/IACD/2_Ano/2_Semestre/ETD/TF_ETD/REGISTO_IA.md).

---

## 📖 Dicionário de Dados (Star Schema)

Esta secção detalha o esquema da base de dados relacional `moda_analytics.db` (SQLite) e as regras de transformação aplicadas.

### 1. Tabela de Dimensão: `dim_tempo`
*   **Descrição**: Dimensão temporal para agregação e segmentação temporal.
*   **Chave Primária**: `date` (TEXT)

| Nome do Campo | Tipo SQL | Descrição | Fonte / Origem | Regra de Transformação | Observações |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **`date`** | TEXT | Data de referência do calendário (formato `YYYY-MM-DD`). | Dataset Gold consolidado | Chave temporal unificada das três fontes (FRED, Tiingo, NewsAPI). | **Chave Primária (PK)**. |
| **`ano`** | INTEGER | Ano civil do registo. | Derivado de `date` | Extraído em Python com `pandas.dt.year`. | Utilizado para filtros anuais. |
| **`mes`** | INTEGER | Mês do ano (numérico: `1` a `12`). | Derivado de `date` | Extraído em Python com `pandas.dt.month`. | Permite ordenação cronológica. |
| **`dia`** | INTEGER | Dia do mês (`1` a `31`). | Derivado de `date` | Extraído em Python com `pandas.dt.day`. | Granularidade diária básica. |
| **`dia_semana`** | INTEGER | Dia da semana numérico (`0` = Segunda-feira, ..., `6` = Domingo). | Derivado de `date` | Extraído em Python com `pandas.dt.weekday`. | Útil para analisar efeitos de dia de semana na bolsa. |
| **`nome_mes`** | TEXT | Nome do mês por extenso em Português Europeu. | Mapeamento de `mes` | Mapeado através de dicionário em Python (`1: "Janeiro"`, etc.). | Utilizado em eixos de gráficos. |

### 2. Tabela de Dimensão: `dim_macroeconomia`
*   **Descrição**: Armazena os indicadores económicos mensais do consumo americano obtidos via API do FRED.
*   **Chave Primária**: `date` (TEXT)
*   **Chave Estrangeira**: `date` referencia `dim_tempo(date)`

| Nome do Campo | Tipo SQL | Descrição | Fonte / Origem | Regra de Transformação | Observações |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **`date`** | TEXT | Data de referência (formato `YYYY-MM-DD`). | API do FRED | Chave primária da tabela. | **Chave Primária (PK)**, **Chave Estrangeira (FK)**. |
| **`vendas_vestuario`** | REAL | Índice de Vendas a Retalho de Vestuário e Acessórios nos EUA (FRED: `RSFSXMV`). | API do FRED | As séries originais do FRED são mensais. Para a escala diária, foi aplicada interpolação temporal de preenchimento (*Forward Fill - ffill()* e *Backward Fill - bfill()*). | Representa o volume macroeconómico de consumo do setor. |
| **`inflacao_vestuario`** | REAL | Índice de Preços ao Consumidor (IPC/CPI) para Vestuário nos EUA (FRED: `CPIAPPNS`). | API do FRED | Interpolação temporal na escala diária através de *Forward Fill* a partir da série mensal original. | Indica a pressão inflacionária no consumo de moda. |

### 3. Tabela de Dimensão: `dim_sentimento`
*   **Descrição**: Guarda a pontuação de sentimento diário das notícias do setor extraída de media sociais e agências noticiosas.
*   **Chave Primária**: `date` (TEXT)
*   **Chave Estrangeira**: `date` referencia `dim_tempo(date)`

| Nome do Campo | Tipo SQL | Descrição | Fonte / Origem | Regra de Transformação | Observações |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **`date`** | TEXT | Data de referência (formato `YYYY-MM-DD`). | NewsAPI / Alpha Vantage | Chave primária da tabela. | **Chave Primária (PK)**, **Chave Estrangeira (FK)**. |
| **`sentiment_score`** | REAL | Pontuação diária de sentimento média global. | NewsAPI / Alpha Vantage | Análise léxica baseada na biblioteca VADER (`compound score` de `-1.0` a `+1.0`) e efetuada a média aritmética simples diária. | Representa a atitude geral dos media sobre a moda. |
| **`nike_sentiment`** | REAL | Sentimento médio diário associado especificamente à Nike. | NewsAPI / Alpha Vantage | Filtragem de artigos que contêm menções a "Nike" e cálculo do sentimento VADER médio compound correspondente. | Pontuação entre `-1.0` (Negativo) e `+1.0` (Positivo). |
| **`lvmh_sentiment`** | REAL | Sentimento médio diário associado especificamente à LVMH. | NewsAPI / Alpha Vantage | Filtragem de artigos com a palavra-chave "LVMH" / "Louis Vuitton" e cálculo do sentimento VADER compound. | Pontuação entre `-1.0` e `+1.0`. |
| **`inditex_sentiment`** | REAL | Sentimento médio diário associado à Inditex (Zara). | NewsAPI / Alpha Vantage | Filtragem de artigos com as palavras-chave "Inditex" / "Zara" e cálculo do sentimento VADER compound. | Pontuação entre `-1.0` e `+1.0`. |
| **`general_sentiment`** | REAL | Sentimento médio diário de notícias genéricas sobre sustentabilidade e retalho global. | NewsAPI / Alpha Vantage | Filtragem de artigos com termos da indústria (ex. "sustainability", "retail", "fashion") excluindo marcas específicas. | Pontuação entre `-1.0` e `+1.0`. |

### 4. Tabela de Factos: `facto_mercado`
*   **Descrição**: Tabela central do Star Schema contendo as métricas de cotações financeiras diárias das marcas no portfólio.
*   **Chave Primária**: `date` (TEXT)
*   **Chaves Estrangeiras**:
    *   `date` referencia `dim_tempo(date)`
    *   `date` referencia `dim_macroeconomia(date)`
    *   `date` referencia `dim_sentimento(date)`

| Nome do Campo | Tipo SQL | Descrição | Fonte / Origem | Regra de Transformação | Observações |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **`date`** | TEXT | Data do pregão da bolsa (formato `YYYY-MM-DD`). | API do Tiingo | Liga a tabela às dimensões. | **Chave Primária (PK)**, **Chaves Estrangeiras (FK)**. |
| **`nike_close`** | REAL | Preço de fecho da ação da Nike Inc. (NKE). | API do Tiingo | Sanitização de valores negativos. Admite nulos para feriados em bolsas locais. | Expresso em USD. |
| **`nike_volume`** | REAL | Volume diário de ações transacionadas da Nike. | API do Tiingo | Admitidos valores nulos em feriados de bolsa. | Métrica de liquidez bolsista. |
| **`lvmh_close`** | REAL | Preço de fecho da ação do grupo LVMH (LVMUY). | API do Tiingo | Conversão de cotação e tratamento de calendário europeu (nulos permitidos). | Expresso em USD (ticker LVMUY ADR). |
| **`lvmh_volume`** | REAL | Volume diário de ações transacionadas da LVMH. | API do Tiingo | Admitidos valores nulos em feriados de bolsa. | Métrica de liquidez. |
| **`inditex_close`** | REAL | Preço de fecho da ação da Inditex S.A. (IDEXY). | API do Tiingo | Tratamento de feriados locais da bolsa de Madrid (nulos permitidos). | Expresso em USD (ticker IDEXY ADR). |
| **`inditex_volume`** | REAL | Volume diário de ações transacionadas da Inditex. | API do Tiingo | Admitidos valores nulos em feriados de bolsa. | Métrica de liquidez. |

---

## 📊 Relatório Técnico & Metodologia

Esta secção descreve a fundamentação, decisões de arquitetura e metodologias implementadas no projeto.

### 1. Contexto & Objetivos
A indústria de moda de luxo e retalho de vestuário é influenciada pelas condições macroeconómicas (vendas a retalho e inflação), pelo desempenho financeiro das ações das empresas líderes (Nike, LVMH, Inditex) e pela perceção pública/reputação das marcas nos media. O **TF_ETD** implementa um pipeline modular automatizado que extrai, higieniza, integra e visualiza estas três vertentes de dados.

### 2. Decisões de Engenharia de Dados & ETL
*   **Alinhamento de Frequências (Interpolação)**: Os dados do FRED são mensais, enquanto as ações e notícias são diárias. Aplicou-se interpolação temporal por preenchimento (*Forward Fill*), propagando os valores mensais de consumo/inflação para todos os dias do respetivo mês. Os dias marginais iniciais foram resolvidos com *Backward Fill*.
*   **Feriados Bolsistas Desalinhados**: As ações são transacionadas em bolsas com calendários e feriados locais distintos. A tabela de factos `facto_mercado` admite valores nulos (`NULL`) nas colunas de fecho e volume das ações para evitar rejeitar linhas inteiras em dias de pregão parcial, preservando a integridade temporal de outras dimensões (notícias e macroeconomia).
*   **View Analítica Consolidada**: Para evitar junções relacionais lentas em tempo real na app de visualização, criou-se a `view_analitica_consolidada` diretamente na base de dados. O Streamlit precisa apenas de fazer `SELECT * FROM view_analitica_consolidada` aplicando os filtros laterais. Adicionaram-se índices explícitos na tabela de factos (`idx_facto_date`) e de tempo (`idx_tempo_ano_mes`) para otimizar as junções.

### 3. Decisões Analíticas & Data Science
*   **Análise de Sentimento Léxica (VADER)**: Utilizou-se o classificador léxico VADER (`compound score` de `-1.0` a `+1.0`) para notícias curtas e textos digitais. Cada notícia foi submetida a limpeza básica. Notícias sem menção direta a marcas foram atribuídas a `general_sentiment`, enquanto as restantes alimentaram os sentimentos específicos.
*   **Análise Financeira Normalizada (Base 100)**: Para comparar de forma justa o desempenho de ações cujos preços absolutos diferem por ordens de grandeza (ex: LVMH vs Nike), o dashboard implementa uma normalização para Base 100 a partir da primeira data selecionada:
  $$\text{Preço Normalizado} = \left(\frac{\text{Preço}_t}{\text{Preço}_{t_0}}\right) \times 100$$
*   **Modelagem Estatística (OLS)**: Implementou-se um cálculo de regressão linear dinâmica por Mínimos Quadrados Ordinários (OLS) no gráfico de dispersão do Plotly. O dashboard calcula a linha de tendência, o coeficiente de determinação ($R^2$) e o declive dinamicamente, reagindo aos filtros laterais.

### 4. Limitações & Trade-offs
*   **Dados de Notícias Históricos**: Devido às restrições de quotas gratuitas nas APIs de notícias (limite de 30 dias na NewsAPI), utilizou-se um dataset histórico representativo estruturado na Semana 1.
*   **Latência de Carga Inicial**: No arranque do Streamlit, o failover copia a base de dados SQLite da Semana 3 se esta não existir na pasta `Semana_4/outputs/`. Embora adicione uma pequena latência no primeiro arranque, garante total autonomia ao professor.
*   **Escalabilidade**: Para volumes de dados massivos, o SQLite poderá sofrer com concorrência de escrita. No entanto, para um dashboard analítico (predominantemente de leitura rápida), provou ser extremamente leve e rápido.

