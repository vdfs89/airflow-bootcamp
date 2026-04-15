CREATE TABLE IF NOT EXISTS veiculos (
    id_veiculos BIGINT PRIMARY KEY,
    nome VARCHAR(255),
    tipo VARCHAR(100),
    valor NUMERIC(12,2),
    data_inclusao TIMESTAMP,
    data_atualizacao TIMESTAMP
);

CREATE TABLE IF NOT EXISTS estados (
    id_estados BIGINT PRIMARY KEY,
    estado VARCHAR(255),
    sigla VARCHAR(2),
    data_inclusao TIMESTAMP,
    data_atualizacao TIMESTAMP
);

CREATE TABLE IF NOT EXISTS cidades (
    id_cidades BIGINT PRIMARY KEY,
    cidade VARCHAR(255),
    id_estados BIGINT,
    data_inclusao TIMESTAMP,
    data_atualizacao TIMESTAMP
);

CREATE TABLE IF NOT EXISTS concessionarias (
    id_concessionarias BIGINT PRIMARY KEY,
    concessionaria VARCHAR(255),
    id_cidades BIGINT,
    data_inclusao TIMESTAMP,
    data_atualizacao TIMESTAMP
);

CREATE TABLE IF NOT EXISTS vendedores (
    id_vendedores BIGINT PRIMARY KEY,
    nome VARCHAR(255),
    id_concessionarias BIGINT,
    data_inclusao TIMESTAMP,
    data_atualizacao TIMESTAMP
);

CREATE TABLE IF NOT EXISTS clientes (
    id_clientes BIGINT PRIMARY KEY,
    cliente VARCHAR(255),
    endereco VARCHAR(255),
    id_concessionarias BIGINT,
    data_inclusao TIMESTAMP,
    data_atualizacao TIMESTAMP
);

CREATE TABLE IF NOT EXISTS vendas (
    id_vendas BIGINT PRIMARY KEY,
    id_veiculos BIGINT,
    id_concessionarias BIGINT,
    id_vendedores BIGINT,
    id_clientes BIGINT,
    valor_pago NUMERIC(12,2),
    data_venda TIMESTAMP,
    data_inclusao TIMESTAMP,
    data_atualizacao TIMESTAMP
);
