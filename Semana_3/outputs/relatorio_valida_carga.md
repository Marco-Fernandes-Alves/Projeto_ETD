# 📊 Relatório de Validação Pós-Carga - Semana 3
Este relatório documenta os testes de integridade analítica e consistência pós-carregamento no SQLite.

## 1. Contagem de Registos por Tabela
| Tabela | Contagem de Registos |
| :--- | :---: |
| `dim_tempo` | **353** |
| `dim_macroeconomia` | **353** |
| `dim_sentimento` | **353** |
| `facto_mercado` | **353** |

## 2. Integridade Referencial & Chaves Estrangeiras
- ✅ **Sucesso**: O número de registos na View consolidada (353) coincide com a Tabela de Factos (353).

## 3. Análise de Valores Nulos
- ⚠️ **Aviso**: Detetados 10 nulos nas colunas de fecho/indicadores.