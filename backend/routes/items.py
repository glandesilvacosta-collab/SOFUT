from fastapi import APIRouter, HTTPException, Query
from typing import List, Optional
from database import get_db_connection
from models import ItemCreate, ItemUpdate, ItemResponse

router = APIRouter(prefix="/api/itens", tags=["Itens e Equipamentos"])

@router.get("", response_model=List[dict])
def list_items(
    busca: Optional[str] = Query(None, description="Buscar por nome ou número de série"),
    status: Optional[str] = Query(None, description="Filtrar por status: DISPONIVEL, EMPRESTADO, MANUTENCAO, CONFISCADO_MARIA"),
    categoria_id: Optional[int] = Query(None, description="Filtrar por ID de categoria"),
    localizacao: Optional[str] = Query(None, description="Filtrar por cômodo da casa")
):
    """Lista todos os equipamentos e ativos da casa com seus dados, categorias e posses atuais."""
    conn = get_db_connection()
    cursor = conn.cursor()

    query = """
        SELECT 
            i.id,
            i.nome,
            i.categoria_id,
            c.nome as categoria_nome,
            c.icone as categoria_icone,
            i.numero_serie,
            i.descricao,
            i.localizacao,
            i.icone,
            i.status,
            i.criado_em,
            m.id as posse_membro_id,
            m.nome as posse_atual,
            m.avatar_icone as posse_membro_avatar,
            mov.id as movimentacao_ativa_id,
            mov.data_retirada as data_retirada_atual,
            mov.data_prevista as data_prevista_atual,
            mov.motivo as motivo_atual
        FROM itens i
        LEFT JOIN categorias c ON i.categoria_id = c.id
        LEFT JOIN movimentacoes mov ON mov.item_id = i.id AND mov.status IN ('ABERTO', 'ATRASADO')
        LEFT JOIN membros m ON mov.membro_id = m.id
        WHERE 1=1
    """
    params = []

    if busca:
        query += " AND (i.nome LIKE ? OR i.numero_serie LIKE ? OR i.descricao LIKE ?)"
        term = f"%{busca}%"
        params.extend([term, term, term])

    if status and status != "TODOS":
        query += " AND i.status = ?"
        params.append(status)

    if categoria_id:
        query += " AND i.categoria_id = ?"
        params.append(categoria_id)

    if localizacao:
        query += " AND i.localizacao LIKE ?"
        params.append(f"%{localizacao}%")

    query += " ORDER BY i.id DESC;"
    cursor.execute(query, params)
    rows = cursor.fetchall()
    conn.close()

    return [dict(row) for row in rows]

@router.get("/categorias")
def list_categories():
    """Retorna a lista de categorias disponíveis no sistema."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT c.*, COUNT(i.id) as total_itens 
        FROM categorias c 
        LEFT JOIN itens i ON c.id = i.categoria_id 
        GROUP BY c.id 
        ORDER BY c.nome ASC;
    """)
    rows = cursor.fetchall()
    conn.close()
    return [dict(row) for row in rows]

@router.get("/{item_id}")
def get_item(item_id: int):
    """Retorna detalhes de um item específico e seu histórico de movimentações."""
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT 
            i.*, 
            c.nome as categoria_nome, 
            c.icone as categoria_icone 
        FROM itens i
        LEFT JOIN categorias c ON i.categoria_id = c.id
        WHERE i.id = ?;
    """, (item_id,))
    item = cursor.fetchone()

    if not item:
        conn.close()
        raise HTTPException(status_code=404, detail="Equipamento não encontrado na casa!")

    cursor.execute("""
        SELECT 
            mov.*,
            m.nome as membro_nome,
            m.apelido as membro_apelido,
            m.avatar_icone as membro_avatar
        FROM movimentacoes mov
        JOIN membros m ON mov.membro_id = m.id
        WHERE mov.item_id = ?
        ORDER BY mov.id DESC;
    """, (item_id,))
    historico = cursor.fetchall()
    conn.close()

    result = dict(item)
    result["historico"] = [dict(h) for h in historico]
    return result

@router.post("", status_code=201)
def create_item(item: ItemCreate):
    """Registra um novo equipamento / ativo na casa com número de série único."""
    conn = get_db_connection()
    cursor = conn.cursor()

    # Verificar unicidade do número de série
    cursor.execute("SELECT id FROM itens WHERE numero_serie = ?;", (item.numero_serie.strip(),))
    if cursor.fetchone():
        conn.close()
        raise HTTPException(status_code=400, detail=f"O número de série '{item.numero_serie}' já está registrado em outro item!")

    # Verificar categoria
    cursor.execute("SELECT id FROM categorias WHERE id = ?;", (item.categoria_id,))
    if not cursor.fetchone():
        conn.close()
        raise HTTPException(status_code=400, detail="Categoria informada não existe!")

    cursor.execute("""
        INSERT INTO itens (nome, categoria_id, numero_serie, descricao, localizacao, icone, status)
        VALUES (?, ?, ?, ?, ?, ?, 'DISPONIVEL');
    """, (
        item.nome.strip(),
        item.categoria_id,
        item.numero_serie.strip().upper(),
        item.descricao.strip() if item.descricao else None,
        item.localizacao.strip(),
        item.icone.strip() or "📦"
    ))
    new_id = cursor.lastrowid
    conn.commit()
    conn.close()

    return {"id": new_id, "mensagem": f"Equipamento '{item.nome}' registrado com sucesso no inventário familiar!"}

@router.put("/{item_id}")
def update_item(item_id: int, item: ItemUpdate):
    """Atualiza as informações de um equipamento."""
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT id FROM itens WHERE id = ?;", (item_id,))
    if not cursor.fetchone():
        conn.close()
        raise HTTPException(status_code=404, detail="Equipamento não encontrado!")

    fields = []
    values = []

    if item.nome is not None:
        fields.append("nome = ?")
        values.append(item.nome.strip())
    if item.categoria_id is not None:
        fields.append("categoria_id = ?")
        values.append(item.categoria_id)
    if item.descricao is not None:
        fields.append("descricao = ?")
        values.append(item.descricao.strip())
    if item.localizacao is not None:
        fields.append("localizacao = ?")
        values.append(item.localizacao.strip())
    if item.icone is not None:
        fields.append("icone = ?")
        values.append(item.icone.strip())
    if item.status is not None:
        fields.append("status = ?")
        values.append(item.status)

    if not fields:
        conn.close()
        raise HTTPException(status_code=400, detail="Nenhum dado informado para atualização.")

    values.append(item_id)
    sql = f"UPDATE itens SET {', '.join(fields)} WHERE id = ?;"
    cursor.execute(sql, values)
    conn.commit()
    conn.close()

    return {"mensagem": "Equipamento atualizado com sucesso!"}

@router.delete("/{item_id}")
def delete_item(item_id: int):
    """Exclui um equipamento, desde que não esteja emprestado no momento."""
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT status, nome FROM itens WHERE id = ?;", (item_id,))
    item = cursor.fetchone()
    if not item:
        conn.close()
        raise HTTPException(status_code=404, detail="Equipamento não encontrado!")

    if item["status"] == "EMPRESTADO":
        conn.close()
        raise HTTPException(status_code=400, detail=f"Não é possível excluir '{item['nome']}' pois ele está emprestado no momento! Registre a devolução primeiro.")

    cursor.execute("DELETE FROM itens WHERE id = ?;", (item_id,))
    conn.commit()
    conn.close()

    return {"mensagem": f"Equipamento '{item['nome']}' removido do inventário familiar!"}
