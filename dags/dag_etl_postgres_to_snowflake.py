from airflow import DAG
from airflow.providers.postgres.hooks.postgres import PostgresHook
from airflow.providers.snowflake.hooks.snowflake import SnowflakeHook
from airflow.operators.python import PythonOperator
from datetime import datetime
import pandas as pd

def transferir_dados_vendas():
    # 1. EXTRAÇÃO: Conecta no Postgres da NovaDrive (Fonte)
    # Certifique-se de que a Connection 'postgres_novadrive' existe no Airflow
    pg_hook = PostgresHook(postgres_conn_id='postgres_novadrive')
    
    # Buscamos os dados reais do banco de vendas
    df = pg_hook.get_pandas_df("SELECT * FROM vendas")
    print(f"Extração concluída: {len(df)} registros encontrados.")

    # 2. TRANSFORMAÇÃO: Ajuste de nomes para o Snowflake
    # O Snowflake prefere nomes de colunas em maiúsculo
    df.columns = [c.upper() for c in df.columns]

    # 3. CARGA: Conecta no Snowflake (Destino)
    # Certifique-se de que a Connection 'snowflake_conn' existe no Airflow
    sf_hook = SnowflakeHook(snowflake_conn_id='snowflake_conn')
    
    # Criamos a tabela final se ela não existir
    sf_hook.run("CREATE TABLE IF NOT EXISTS NOVADRIVE_DB.REFINED.VENDAS_FINAL (ID INT, MODELO STRING, VALOR FLOAT, DATA DATE)")
    
    # Inserimos os dados usando o SQLAlchemy Engine
    engine = sf_hook.get_sqlalchemy_engine()
    df.to_sql('vendas_final', con=engine, schema='REFINED', if_exists='replace', index=False)
    
    print("Sucesso! Dados reais da NovaDrive carregados no Snowflake.")

# Definição da DAG corrigida para Airflow 3.0+
with DAG(
    '04_pipeline_vendas_completo',
    start_date=datetime(2026, 3, 17),
    schedule='@daily',  # Corrigido aqui: apenas 'schedule'
    catchup=False
) as dag:

    tarefa_etl = PythonOperator(
        task_id='transferir_postgres_para_snowflake',
        python_callable=transferir_dados_vendas
    )
