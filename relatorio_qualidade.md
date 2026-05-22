# Relatório de Qualidade de Dados

> [!NOTE]
> **Estado Geral do Pipeline de Qualidade**: ✅ **APROVADO**

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
==================================================
🔍 INICIANDO SUITE DE VALIDAÇÃO DE QUALIDADE DE DADOS
==================================================

--- 1. Validação dos Indicadores FRED (Staging) ---
 Unicidade: Datas de indicadores FRED são 100% únicas.
 Schema & Tipos: 412 registos FRED validados com sucesso via Pydantic.

--- 2. Validação das Ações Tiingo (Staging) ---
 Unicidade NKE: Datas das ações são únicas.
 Schema & Tipos NKE: 343 registos validados com sucesso.
 Unicidade LVMUY: Datas das ações são únicas.
 Schema & Tipos LVMUY: 343 registos validados com sucesso.
 Unicidade IDEXY: Datas das ações são únicas.
 Schema & Tipos IDEXY: 343 registos validados com sucesso.

--- 3. Validação de Sentimento Diário (Staging) ---
 Unicidade: Datas dos scores de sentimento são únicas.
 Schema & Tipos: 22 registos de sentimento validados com sucesso.

--- 4. Validação do Dataset Integrado (Camada Gold) ---
 Unicidade: Datas de negócios da Camada Gold são estritamente únicas.
 Schema & Sanidade Gold: 343 registos consolidados validados e aprovados.

==================================================
✅ RESULTADO DO PIPELINE: APROVADO! Todos os dados cumprem os critérios de qualidade.
==================================================
```

---

## 🛠️ Anomalias Identificadas & Decisões de Limpeza

| Fonte | Problema Encontrado | Gravidade | Ação de Reparação / Decisão Técnica |
| :--- | :--- | :--- | :--- |
| **FRED (Indicadores)** | Granularidade mensal (apenas dia 1 de cada mês). *Inner joins* diretos colapsavam o dataset final para 6 registos. | Média | **Interpolação Temporal**: Foi efetuada uma reamostragem diária do calendário combinando os dias das ações e aplicando *Forward Fill* (`ffill`) para propagar o último dado económico conhecido. |
| **Tiingo (Ações)** | Fins de semana e feriados sem negociação originavam nulos em `close` caso mantivéssemos o calendário completo. | Baixa | **Filtro de Calendário de Negócios**: Remoção de linhas de fins-de-week utilizando `dropna(how='all')` nos valores de fecho das 3 marcas. |
| **NewsAPI (Notícias)** | Dias sem nenhuma notícia recolhida sobre moda/luxo/sustentabilidade causavam valores nulos no merge final. | Baixa | **Tratamento de Nulos**: Preenchimento automático dos sentimentos nulos com score neutro (`0.0`). |
| **Geral (Duplicados)** | Registos de datas duplicadas podem surgir por anomalias nas chamadas das APIs na extração. | Alta | **Remoção de Duplicados**: Lógica integrada de `drop_duplicates(subset=['date'])` nos scripts de limpeza. |

