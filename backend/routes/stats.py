from fastapi import APIRouter
from database import get_db_connection
from seed import seed_data

router = APIRouter(prefix="/api/stats", tags=["Estatísticas e Dashboard"])

@router.get("")
def get_dashboard_stats():
    """Retorna as métricas e indicadores do painel administrativo da família."""
    conn = get_db_connection()
    cursor = conn.cursor()

    # Contagem de itens por status
    cursor.execute("""
        SELECT 
            COUNT(*) as total_itens,
            SUM(CASE WHEN status = 'DISPONIVEL' THEN 1 ELSE 0 END) as disponiveis,
            SUM(CASE WHEN status = 'EMPRESTADO' THEN 1 ELSE 0 END) as emprestados,
            SUM(CASE WHEN status = 'MANUTENCAO' THEN 1 ELSE 0 END) as manutencao,
            SUM(CASE WHEN status = 'CONFISCADO_MARIA' THEN 1 ELSE 0 END) as confiscados
        FROM itens;
    """)
    itens_stats = dict(cursor.fetchone() or {})

    # Membro que mais pegou coisas emprestadas (O mais folgado)
    cursor.execute("""
        SELECT m.nome, m.apelido, m.avatar_icone, m.nivel_perigo, COUNT(mov.id) as total_retiradas
        FROM membros m
        JOIN movimentacoes mov ON m.id = mov.membro_id
        GROUP BY m.id
        ORDER BY total_retiradas DESC
        LIMIT 1;
    """)
    top_infrator = cursor.fetchone()

    # Membro com mais castigos
    cursor.execute("""
        SELECT m.nome, m.apelido, m.avatar_icone, COUNT(mov.id) as total_castigos
        FROM membros m
        JOIN movimentacoes mov ON m.id = mov.membro_id
        WHERE mov.castigo_aplicado IS NOT NULL AND mov.castigo_aplicado != ''
        GROUP BY m.id
        ORDER BY total_castigos DESC
        LIMIT 1;
    """)
    top_castigado = cursor.fetchone()

    # Item mais requisitado da casa
    cursor.execute("""
        SELECT i.nome, i.icone, i.numero_serie, COUNT(mov.id) as total_usos
        FROM itens i
        JOIN movimentacoes mov ON i.id = mov.item_id
        GROUP BY i.id
        ORDER BY total_usos DESC
        LIMIT 1;
    """)
    top_item = cursor.fetchone()

    # Total de movimentações registradas
    cursor.execute("SELECT COUNT(*) FROM movimentacoes;")
    total_movimentacoes = cursor.fetchone()[0]

    conn.close()

    return {
        "kpis": {
            "total_itens": itens_stats.get("total_itens") or 0,
            "disponiveis": itens_stats.get("disponiveis") or 0,
            "emprestados": itens_stats.get("emprestados") or 0,
            "manutencao": itens_stats.get("manutencao") or 0,
            "confiscados": itens_stats.get("confiscados") or 0,
            "total_movimentacoes": total_movimentacoes
        },
        "destaques": {
            "campeao_retiradas": dict(top_infrator) if top_infrator else None,
            "campeao_castigos": dict(top_castigado) if top_castigado else None,
            "item_mais_disputado": dict(top_item) if top_item else None
        }
    }

@router.post("/reset-banco")
def reset_database():
    """Restaura o banco de dados para os dados padrão da família para testes."""
    seed_data(force=True)
    return {"mensagem": "Banco de dados restaurado com os dados da Família com sucesso!"}
