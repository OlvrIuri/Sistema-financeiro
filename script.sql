-- ============================================================
-- script.sql — Estrutura do banco de dados 'sistema_financeiro'
-- ============================================================
-- Como usar: criar o banco (CREATE DATABASE sistema_financeiro;)
-- e executar este script inteiro no phpMyAdmin / MySQL.
--
-- Apresentação: este arquivo faz parte da PARTE 3 (Banco de Dados / MER).
-- ============================================================

USE sistema_financeiro;

-- Tabela de domínio: perfis de acesso (1 = Gerente, 2 = Cliente)
CREATE TABLE perfis (
    id INT AUTO_INCREMENT PRIMARY KEY,
    nome VARCHAR(50) NOT NULL UNIQUE
);

-- USUARIO: dados de cadastro e credenciais de login
-- Regra de negócio: e-mail ÚNICO identifica o usuário no sistema
CREATE TABLE usuarios (
    id INT AUTO_INCREMENT PRIMARY KEY,
    nome VARCHAR(100) NOT NULL,
    email VARCHAR(100) NOT NULL UNIQUE,   -- garante unicidade do login
    senha VARCHAR(255) NOT NULL,
    perfil_id INT,
    FOREIGN KEY (perfil_id) REFERENCES perfis(id)
);

-- Tabela de domínio: tipos de conta (1 = Corrente, 2 = Poupança)
CREATE TABLE tipos_conta (
    id INT AUTO_INCREMENT PRIMARY KEY,
    nome VARCHAR(50) NOT NULL UNIQUE
);

-- CONTA: relação 1:1 com usuário; saldo inicia em 0.00
-- ON DELETE CASCADE: apagar o usuário apaga a conta automaticamente
CREATE TABLE contas (
    id INT AUTO_INCREMENT PRIMARY KEY,
    usuario_id INT,
    tipo_conta_id INT,
    saldo DECIMAL(10, 2) DEFAULT 0.00,
    FOREIGN KEY (usuario_id) REFERENCES usuarios(id) ON DELETE CASCADE,
    FOREIGN KEY (tipo_conta_id) REFERENCES tipos_conta(id)
);

-- Tabela de domínio: tipos de transação (1 = Depósito, 2 = Saque)
CREATE TABLE tipos_transacao (
    id INT AUTO_INCREMENT PRIMARY KEY,
    nome VARCHAR(50) NOT NULL UNIQUE
);

-- TRANSACAO: histórico/extrato — relação 1:N com conta
-- data_hora é preenchida automaticamente pelo MySQL (CURRENT_TIMESTAMP)
CREATE TABLE transacoes (
    id INT AUTO_INCREMENT PRIMARY KEY,
    conta_id INT,
    tipo_transacao_id INT,
    valor DECIMAL(10, 2) NOT NULL,
    data_hora TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (conta_id) REFERENCES contas(id) ON DELETE CASCADE,
    FOREIGN KEY (tipo_transacao_id) REFERENCES tipos_transacao(id)
);

-- CARTOES e EMPRESTIMOS: entidades previstas no modelo para
-- evolução futura do sistema (não usadas pelo menu atual)
CREATE TABLE cartoes (
    id INT AUTO_INCREMENT PRIMARY KEY,
    conta_id INT,
    numero_cartao VARCHAR(16) NOT NULL UNIQUE,
    limite DECIMAL(10, 2) DEFAULT 1000.00,
    FOREIGN KEY (conta_id) REFERENCES contas(id) ON DELETE CASCADE
);

CREATE TABLE emprestimos (
    id INT AUTO_INCREMENT PRIMARY KEY,
    conta_id INT,
    valor_total DECIMAL(10, 2) NOT NULL,
    parcelas INT NOT NULL,
    FOREIGN KEY (conta_id) REFERENCES contas(id) ON DELETE CASCADE
);

-- Dados iniciais vitais para o sistema (tabelas de domínio)
INSERT INTO perfis (nome) VALUES ('Gerente'), ('Cliente');
INSERT INTO tipos_conta (nome) VALUES ('Corrente'), ('Poupança');
INSERT INTO tipos_transacao (nome) VALUES ('Depósito'), ('Saque');

-- Gerente padrão para testar o login administrativo
-- Login: gerente@banco.com  |  Senha: 1234
INSERT INTO usuarios (nome, email, senha, perfil_id) VALUES ('Admin Gerente', 'gerente@banco.com', '1234', 1);
