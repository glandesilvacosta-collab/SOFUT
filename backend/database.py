import sqlite3
import os
from pathlib import Path

DB_PATH = Path(__file__).resolve().parent / "familia_ativos.db"

def get_db_connection():
    """Retorna uma conexão SQLite com suporte a dicionários e integridade referencial ativa."""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON;")
    return conn

def init_db():
    """Inicializa as tabelas relacionais do sistema de ativos da família se não existirem."""
    conn = get_db_connection()
    cursor = conn.cursor()

    # 1. Tabela de Categorias
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS categorias (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nome TEXT NOT NULL UNIQUE,
            icone TEXT NOT NULL,
            descricao TEXT
        );
    """)

    # 2. Tabela de Integrantes da Família (Membros)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS membros (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nome TEXT NOT NULL UNIQUE,
            apelido TEXT NOT NULL,
            papel TEXT NOT NULL,
            descricao TEXT NOT NULL,
            avatar_icone TEXT NOT NULL,
            nivel_perigo TEXT NOT NULL DEFAULT 'Médio',
            reputacao_score INTEGER NOT NULL DEFAULT 100,
            criado_em TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
    """)

    # 3. Tabela de Equipamentos / Ativos da Casa
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS itens (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nome TEXT NOT NULL,
            categoria_id INTEGER NOT NULL,
            numero_serie TEXT NOT NULL UNIQUE,
            descricao TEXT,
            localizacao TEXT NOT NULL DEFAULT 'Armário Central',
            icone TEXT NOT NULL DEFAULT '📦',
            status TEXT NOT NULL DEFAULT 'DISPONIVEL' CHECK(status IN ('DISPONIVEL', 'EMPRESTADO', 'MANUTENCAO', 'CONFISCADO_MARIA')),
            criado_em TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (categoria_id) REFERENCES categorias(id) ON DELETE RESTRICT
        );
    """)

    # 4. Tabela de Movimentações (Empréstimos / Devoluções / Vistorias)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS movimentacoes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            item_id INTEGER NOT NULL,
            membro_id INTEGER NOT NULL,
            data_retirada TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            data_prevista TIMESTAMP NOT NULL,
            data_devolucao TIMESTAMP NULL,
            motivo TEXT NOT NULL,
            status TEXT NOT NULL DEFAULT 'ABERTO' CHECK(status IN ('ABERTO', 'CONCLUIDO', 'ATRASADO')),
            condicao_devolucao TEXT NULL CHECK(condicao_devolucao IN (NULL, 'PERFEITO', 'ARRANHADO', 'ROIDO_PELA_TITI', 'QUEBRADO_CARLINHOS', 'MOLHADO_CLEUSA', 'DESAPARECIDO')),
            castigo_aplicado TEXT NULL,
            observacoes TEXT NULL,
            FOREIGN KEY (item_id) REFERENCES itens(id) ON DELETE CASCADE,
            FOREIGN KEY (membro_id) REFERENCES membros(id) ON DELETE CASCADE
        );
    """)

    conn.commit()
    conn.close()

if __name__ == "__main__":
    init_db()
    print("Banco de dados inicializado com sucesso!")
