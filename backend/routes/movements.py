from fastapi import APIRouter, HTTPException
from typing import List, Optional
from datetime import datetime, timedelta
from database import get_db_connection
from models import RetiradaCreate, DevolucaoCreate

router = APIRouter(prefix="/api/movimentacoes", tags=["Movimentações (Empréstimos e Devoluções)"])

@router.get("", response_model=List[dict])
def list_movements(status: Optional[str] = None):
    """Lista o histórico completo de movimentações da família."""
    conn = get_db_connection()
    cursor = conn.cursor()

    query = """
        SELECT 
            mov.id,
            mov.item_id,
            i.nome as item_nome,
            i.icone as item_icone,
            i.numero_serie as item_numero_serie,
            mov.membro_id,
            m.nome as membro_nome,
            m.apelido as membro_apelido,
            m.avatar_icone as membro_avatar,
            m.nivel_perigo as membro_nivel_perigo,
            mov.data_retirada,
            mov.data_prevista,
            mov.data_devolucao,
            mov.motivo,
            mov.status,
            mov.condicao_devolucao,
            mov.castigo_aplicado,
            mov.observacoes
        FROM movimentacoes mov
        JOIN itens i ON mov.item_id = i.id
        JOIN membros m ON mov.membro_id = m.id
        WHERE 1=1
    """
    params = []
    if status and status != "TODOS":
        if status == "ATIVO":
            query += " AND mov.status IN ('ABERTO', 'ATRASADO')"
        else:
            query += " AND mov.status = ?"
            params.append(status)

    query += " ORDER BY mov.id DESC;"
    cursor.execute(query, params)
    rows = cursor.fetchall()
    conn.close()

    return [dict(row) for row in rows]

@router.post("/retirada", status_code=201)
def registrar_retirada(payload: RetiradaCreate):
    """Registra o empréstimo / saída de um equipamento para um integrante da família."""
    conn = get_db_connection()
    cursor = conn.cursor()

    # 1. Verificar se o item existe e está disponível
    cursor.execute("SELECT id, nome, status FROM itens WHERE id = ?;", (payload.item_id,))
    item = cursor.fetchone()
    if not item:
        conn.close()
        raise HTTPException(status_code=404, detail="Equipamento não encontrado!")

    if item["status"] != "DISPONIVEL":
        conn.close()
        status_msg = {
            "EMPRESTADO": "já está emprestado para outra pessoa da casa!",
            "MANUTENCAO": "está em manutenção e não pode ser retirado!",
            "CONFISCADO_MARIA": "está confiscado pela Dona Maria no quarto dela!"
        }.get(item["status"], "não está disponível para empréstimo!")
        raise HTTPException(status_code=400, detail=f"O item '{item['nome']}' {status_msg}")

    # 2. Verificar se o membro existe
    cursor.execute("SELECT id, nome, apelido, reputacao_score FROM membros WHERE id = ?;", (payload.membro_id,))
    membro = cursor.fetchone()
    if not membro:
        conn.close()
        raise HTTPException(status_code=404, detail="Integrante da família não encontrado!")

    # 3. Calcular data prevista
    agora = datetime.now()
    data_prevista = agora + timedelta(days=payload.dias_previstos)

    # 4. Criar registro de movimentação
    cursor.execute("""
        INSERT INTO movimentacoes (
            item_id, membro_id, data_retirada, data_prevista, motivo, status, observacoes
        ) VALUES (?, ?, ?, ?, ?, 'ABERTO', ?);
    """, (
        payload.item_id,
        payload.membro_id,
        agora.strftime("%Y-%m-%d %H:%M:%S"),
        data_prevista.strftime("%Y-%m-%d %H:%M:%S"),
        payload.motivo.strip(),
        payload.observacoes.strip() if payload.observacoes else None
    ))
    mov_id = cursor.lastrowid

    # 5. Atualizar status do item para EMPRESTADO
    cursor.execute("UPDATE itens SET status = 'EMPRESTADO' WHERE id = ?;", (payload.item_id,))

    conn.commit()
    conn.close()

    return {
        "id": mov_id,
        "mensagem": f"Empréstimo registrado! '{item['nome']}' entregue para {membro['nome']} ({membro['apelido']}). Devolução prevista para {data_prevista.strftime('%d/%m/%Y')}."
    }

@router.post("/devolucao")
def registrar_devolucao(payload: DevolucaoCreate):
    """Registra a devolução de um equipamento com vistoria de danos e aplicação de castigo se necessário."""
    conn = get_db_connection()
    cursor = conn.cursor()

    # 1. Obter a movimentação
    cursor.execute("""
        SELECT mov.*, i.nome as item_nome, m.nome as membro_nome, m.reputacao_score 
        FROM movimentacoes mov
        JOIN itens i ON mov.item_id = i.id
        JOIN membros m ON mov.membro_id = m.id
        WHERE mov.id = ?;
    """, (payload.movimentacao_id,))
    mov = cursor.fetchone()

    if not mov:
        conn.close()
        raise HTTPException(status_code=404, detail="Movimentação de empréstimo não encontrada!")

    if mov["status"] == "CONCLUIDO":
        conn.close()
        raise HTTPException(status_code=400, detail="Esta movimentação já foi finalizada anteriormente!")

    agora = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    # 2. Atualizar a movimentação
    cursor.execute("""
        UPDATE movimentacoes 
        SET 
            data_devolucao = ?,
            status = 'CONCLUIDO',
            condicao_devolucao = ?,
            castigo_aplicado = ?,
            observacoes = COALESCE(?, observacoes)
        WHERE id = ?;
    """, (
        agora,
        payload.condicao_devolucao,
        payload.castigo_aplicado.strip() if payload.castigo_aplicado else None,
        payload.observacoes.strip() if payload.observacoes else None,
        payload.movimentacao_id
    ))

    # 3. Determinar o status do item
    novo_status = payload.novo_status_item
    if payload.condicao_devolucao in ('QUEBRADO_CARLINHOS', 'ROIDO_PELA_TITI'):
        if novo_status == 'DISPONIVEL':
            novo_status = 'MANUTENCAO'
    
    if payload.castigo_aplicado and "confisc" in payload.castigo_aplicado.lower():
        novo_status = 'CONFISCADO_MARIA'

    cursor.execute("UPDATE itens SET status = ? WHERE id = ?;", (novo_status, mov["item_id"]))

    # 4. Ajustar score de reputação do membro se houve avaria ou castigo
    if payload.condicao_devolucao != 'PERFEITO' or payload.castigo_aplicado:
        cursor.execute("""
            UPDATE membros 
            SET reputacao_score = MAX(0, reputacao_score - 15)
            WHERE id = ?;
        """, (mov["membro_id"],))
    else:
        cursor.execute("""
            UPDATE membros 
            SET reputacao_score = MIN(100, reputacao_score + 2)
            WHERE id = ?;
        """, (mov["membro_id"],))

    conn.commit()
    conn.close()

    return {
        "mensagem": f"Devolução de '{mov['item_nome']}' concluída com sucesso! Registrada vistoria por Dona Maria e Carlos.",
        "condicao": payload.condicao_devolucao,
        "castigo": payload.castigo_aplicado,
        "novo_status_item": novo_status
    }
