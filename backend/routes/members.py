from fastapi import APIRouter, HTTPException
from typing import List
from database import get_db_connection

router = APIRouter(prefix="/api/membros", tags=["Integrantes da Família"])

@router.get("", response_model=List[dict])
def list_members():
    """Lista os integrantes da família com contadores de itens em posse, histórico de empréstimos e castigos."""
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT 
            m.id,
            m.nome,
            m.apelido,
            m.papel,
            m.descricao,
            m.avatar_icone,
            m.nivel_perigo,
            m.reputacao_score,
            m.criado_em,
            COUNT(CASE WHEN mov.status IN ('ABERTO', 'ATRASADO') THEN 1 END) as itens_em_posse,
            COUNT(CASE WHEN mov.id IS NOT NULL THEN 1 END) as total_emprestimos,
            COUNT(CASE WHEN mov.castigo_aplicado IS NOT NULL AND mov.castigo_aplicado != '' THEN 1 END) as total_castigos
        FROM membros m
        LEFT JOIN movimentacoes mov ON m.id = mov.membro_id
        GROUP BY m.id
        ORDER BY m.id ASC;
    """)
    rows = cursor.fetchall()
    conn.close()

    return [dict(row) for row in rows]

@router.get("/{membro_id}")
def get_member(membro_id: int):
    """Retorna o perfil completo de um integrante com itens em sua posse e histórico de movimentações."""
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM membros WHERE id = ?;", (membro_id,))
    member = cursor.fetchone()
    if not member:
        conn.close()
        raise HTTPException(status_code=404, detail="Integrante da família não encontrado!")

    # Itens atualmente em posse
    cursor.execute("""
        SELECT 
            mov.id as movimentacao_id,
            mov.data_retirada,
            mov.data_prevista,
            mov.motivo,
            mov.status as mov_status,
            i.id as item_id,
            i.nome as item_nome,
            i.numero_serie,
            i.icone as item_icone
        FROM movimentacoes mov
        JOIN itens i ON mov.item_id = i.id
        WHERE mov.membro_id = ? AND mov.status IN ('ABERTO', 'ATRASADO')
        ORDER BY mov.data_retirada DESC;
    """, (membro_id,))
    itens_em_posse = cursor.fetchall()

    # Histórico de movimentações passadas
    cursor.execute("""
        SELECT 
            mov.*,
            i.nome as item_nome,
            i.numero_serie,
            i.icone as item_icone
        FROM movimentacoes mov
        JOIN itens i ON mov.item_id = i.id
        WHERE mov.membro_id = ?
        ORDER BY mov.id DESC;
    """, (membro_id,))
    historico = cursor.fetchall()
    conn.close()

    result = dict(member)
    result["itens_em_posse"] = [dict(i) for i in itens_em_posse]
    result["historico"] = [dict(h) for h in historico]
    return result
