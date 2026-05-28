# 📊 Relatório de Validação Pós-Carga - Semana 3
Este relatório documenta os testes de integridade analítica e consistência pós-carregamento no SQLite.

## 1. Contagem de Registos por Tabela
| Tabela | Contagem de Registos |
| :--- | :---: |
| `dim_tempo` | **343** |
| `dim_macroeconomia` | **343** |
| `dim_sentimento` | **343** |
| `facto_mercado` | **343** |

## 2. Integridade Referencial & Chaves Estrangeiras
- ✅ **Sucesso**: O número de registos na View consolidada (`343`) coincide exatamente com o da Tabela de Factos (`343`). Nenhuma linha foi perdida por falha de JOIN.

## 3. Análise de Valores Nulos/Ausentes
- ✅ **Sucesso**: Não foram encontrados valores nulos em colunas críticas de mercado e indicadores macro na camada analítica.
