from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime

# --- SCHEMAS DE ITENS ---
class ItemBase(BaseModel):
    nome: str = Field(..., min_length=2, max_length=120, description="Nome do equipamento ou ativo da casa")
    categoria_id: int = Field(..., description="ID da categoria do item")
    numero_serie: str = Field(..., min_length=2, max_length=50, description="Número de série ou código de tombo")
    descricao: Optional[str] = Field(None, description="Descrição detalhada do item")
    localizacao: str = Field("Armário Central", max_length=100, description="Onde fica guardado na casa")
    icone: str = Field("📦", description="Emoji ou ícone representativo")

class ItemCreate(ItemBase):
    pass

class ItemUpdate(BaseModel):
    nome: Optional[str] = None
    categoria_id: Optional[int] = None
    descricao: Optional[str] = None
    localizacao: Optional[str] = None
    icone: Optional[str] = None
    status: Optional[str] = None

class ItemResponse(ItemBase):
    id: int
    status: str
    categoria_nome: Optional[str] = None
    categoria_icone: Optional[str] = None
    posse_atual: Optional[str] = None
    posse_membro_id: Optional[int] = None
    data_retirada_atual: Optional[str] = None
    data_prevista_atual: Optional[str] = None
    movimentacao_ativa_id: Optional[int] = None
    criado_em: Optional[str] = None

# --- SCHEMAS DE MEMBROS ---
class MemberResponse(BaseModel):
    id: int
    nome: str
    apelido: str
    papel: str
    descricao: str
    avatar_icone: str
    nivel_perigo: str
    reputacao_score: int
    itens_em_posse: int = 0
    total_emprestimos: int = 0
    total_castigos: int = 0
    criado_em: Optional[str] = None

# --- SCHEMAS DE MOVIMENTAÇÃO (EMPRÉSTIMO E DEVOLUÇÃO) ---
class RetiradaCreate(BaseModel):
    item_id: int = Field(..., description="ID do item a ser emprestado")
    membro_id: int = Field(..., description="ID do integrante da família que está pegando")
    motivo: str = Field(..., min_length=3, max_length=300, description="Motivo / finalidade do empréstimo")
    dias_previstos: int = Field(1, ge=1, le=90, description="Quantidade de dias até a devolução prevista")
    observacoes: Optional[str] = Field(None, description="Avisos, ameaças ou observações adicionais")

class DevolucaoCreate(BaseModel):
    movimentacao_id: int = Field(..., description="ID da movimentação ativa")
    condicao_devolucao: str = Field("PERFEITO", description="Estado de conservação pós-uso")
    castigo_aplicado: Optional[str] = Field(None, description="Castigo determinado pela Dona Maria caso haja avaria")
    observacoes: Optional[str] = Field(None, description="Relatório do que aconteceu com o item")
    novo_status_item: str = Field("DISPONIVEL", description="Novo status do item: DISPONIVEL, MANUTENCAO ou CONFISCADO_MARIA")

class MovimentacaoResponse(BaseModel):
    id: int
    item_id: int
    item_nome: str
    item_icone: str
    item_numero_serie: str
    membro_id: int
    membro_nome: str
    membro_apelido: str
    membro_avatar: str
    membro_nivel_perigo: str
    data_retirada: str
    data_prevista: str
    data_devolucao: Optional[str] = None
    motivo: str
    status: str
    condicao_devolucao: Optional[str] = None
    castigo_aplicado: Optional[str] = None
    observacoes: Optional[str] = None
