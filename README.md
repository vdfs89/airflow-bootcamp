# 🚗 NovaDrive Intelligence: Pipeline de Dados de Ponta a Ponta

Este projeto demonstra a construção de um ecossistema de dados completo, desde a orquestração de containers até a visualização em tempo real.

## 🛠️ Tecnologias Utilizadas
- **Nuvem:** Microsoft Azure (VM Ubuntu)
- **Orquestração:** Apache Airflow & Docker
- **Data Warehouse:** Snowflake
- **Visualização:** Streamlit
- **Linguagens:** Python & SQL

## 🏗️ Arquitetura do Projeto
1. **Ingestão:** Airflow orquestra a coleta de dados brutos.
2. **Processamento:** Transformações em Python e SQL para limpeza de tipos.
3. **Armazenamento:** Arquitetura de Medalhão (Stage -> Refined) no Snowflake.
4. **Dashboard:** Visualização de KPIs como Faturamento e Ticket Médio.

## 🚀 Desafios Superados (O "Bug dos Quatrilhões")
Durante o desenvolvimento, identifiquei uma falha crítica de integridade onde IDs eram somados como valores monetários devido ao mapeamento de colunas. A solução envolveu o reset de volumes Docker, saneamento de tabelas via SQL (TRUNCATE) e implementação de uma lógica de "achatamento" de Multi-Index no Pandas para garantir a acurácia dos dados.