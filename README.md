# 🚗 NovaDrive: End-to-End Data Intelligence Pipeline (https://app.snowflake.com/streamlit/pdjgqtj/ov69368/#/apps/nwhqqzic3urfxrpbblvt)

Este projeto documenta a construção de um pipeline de dados completo para a **NovaDrive**, uma concessionária de veículos de luxo. A solução abrange desde a orquestração em ambiente de nuvem (Azure) até a entrega de um dashboard executivo de alta performance no Snowflake, utilizando práticas de **Arquitetura de Medalhão** e **DevSecOps**.

## 🏗️ Arquitetura do Sistema

O pipeline foi desenhado seguindo a filosofia de efemeridade e conteinerização, garantindo portabilidade e escalabilidade.

* **Infraestrutura:** Máquina Virtual Ubuntu na **Microsoft Azure**.
* **Orquestração:** **Apache Airflow** rodando via **Docker-Compose**.
* **Data Warehouse:** **Snowflake** (Camadas Bronze/Stage e Gold/Refined).
* **Visualização:** **Streamlit** (Snowpark) para análise de KPIs em tempo real.

![Arquitetura do Projeto](./img/nora.jpg)

---

## 🛠️ Stack Tecnológica

| Categoria | Tecnologia | Uso Principal |
| :--- | :--- | :--- |
| **Cloud** | Azure | Hospedagem da infraestrutura de processamento. |
| **Container** | Docker | Isolamento e portabilidade do ambiente Airflow. |
| **Workflow** | Airflow | Agendamento e monitoramento das DAGs de ETL. |
| **DW** | Snowflake | Armazenamento e modelagem (Arquitetura Medalhão). |
| **Language** | Python | Transformação de dados (Pandas) e interface (Streamlit). |

---

## 🛡️ Engineering Journey: Desafios e Soluções

### 1. O "Bug dos Quatrilhões" (Integridade de Dados)
Na carga inicial, o faturamento apresentou valores irreais (escala de petabytes). O diagnóstico revelou que o pipeline estava agregando `IDs` de transação como se fossem valores monetários.
* **Solução:** Implementação de um mapeamento rígido de colunas e saneamento da camada *Stage* via `TRUNCATE` para garantir a re-ingestão limpa dos dados.

### 2. Recuperação de Desastre com Time Travel
Durante a refatoração, a tabela principal de vendas foi sobrescrita acidentalmente. 
* **Solução:** Utilizei o recurso de **Time Travel** do Snowflake para realizar o *rollback* e resgate dos dados brutos:
    ```sql
    CREATE OR REPLACE TABLE NOVADRIVE_DB.REFINED.VENDAS_BKP AS 
    SELECT * FROM NOVADRIVE_DB.REFINED.VENDAS_FINAL AT(OFFSET => -3600);
    ```

### 3. Modelagem OBT (One Big Table) para Performance
Para evitar *JOINs* pesados e latência no dashboard, os dados foram desnormalizados na camada **Refined/Gold**.
* **Impacto:** Criação de uma tabela única unindo dimensões de Veículos, Lojas e Clientes, reduzindo drasticamente o tempo de resposta do Streamlit.

### 4. Saneamento de Tipagem e Fuso Horário
Ajuste fino para compatibilidade de dados entre Snowflake e Pandas:
* Conversão forçada de `TIMESTAMP_TZ` para `TIMESTAMP_LTZ` via SQL para garantir a precisão temporal.
* Tratamento de tipos numéricos para cálculos acurados de **Ticket Médio**.

---

## 📊 Resultados: Dashboard Executivo

O dashboard final entrega uma visão granular com faturamento verificado de **R$ 490 Milhões**.

* **Evolução Diária:** Gráfico com suavização *spline* e área sombreada para identificação de picos de venda.
* **Top Performance:** Ranking dos modelos de luxo (AgileXplorer, SpeedFury, etc.) mais vendidos.

![Dashboard Final NovaDrive](./img/graficos.png)

---

## 🚀 Como Executar este Projeto

1.  **Clone o repositório:**
    ```bash
    git clone [https://github.com/vdfs89/airflow-bootcamp.git](https://github.com/vdfs89/airflow-bootcamp.git)
    ```
2.  **Configuração de Ambiente:** Crie um arquivo `.env` na raiz com suas credenciais do Snowflake e configure sua chave SSH `.pem` para acesso à Azure.
3.  **Deploy via Docker:**
    ```bash
    docker-compose up -d
    ```
4.  **Acesso:** O Airflow estará disponível em `localhost:8080`.

---

> **Nota sobre DevSecOps:** Este projeto utiliza práticas de segurança rigorosas, incluindo o uso de `.gitignore` para impedir o vazamento de segredos e permissões NTFS (`icacls`) para proteção de chaves privadas em ambiente Windows/WSL.
