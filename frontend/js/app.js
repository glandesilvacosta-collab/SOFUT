/**
 * PATRIMÔNIO DA FAMÍLIA - APP.JS
 * Lógica da Interface, Consumo da API FastAPI, Gerenciamento de Estado e Modais
 */

const API_BASE = '/api';

// Estado global da aplicação
let state = {
    items: [],
    categories: [],
    members: [],
    movements: [],
    stats: null,
    currentTab: 'tab-inventario',
    activeFilters: {
        busca: '',
        status: 'TODOS',
        categoria_id: 'TODAS'
    }
};

// ==========================================================================
// INICIALIZAÇÃO
// ==========================================================================

document.addEventListener('DOMContentLoaded', () => {
    initApp();
});

async function initApp() {
    try {
        await Promise.all([
            fetchCategories(),
            fetchMembers(),
            fetchStats(),
            fetchItems(),
            fetchMovements()
        ]);
        renderAll();
    } catch (err) {
        console.error('Erro ao inicializar aplicativo:', err);
        showToast('Erro ao carregar dados do servidor.', 'error');
    }
}

async function renderAll() {
    renderKPIs();
    renderCategoriesSelect();
    renderItemsGrid();
    renderActiveLoans();
    renderMembersGrid();
    renderHistoryFeed();
    updateBadges();
}

// ==========================================================================
// REQUISIÇÕES À API (FETCHERS)
// ==========================================================================

async function fetchCategories() {
    const res = await fetch(`${API_BASE}/itens/categorias`);
    state.categories = await res.json();
}

async function fetchMembers() {
    const res = await fetch(`${API_BASE}/membros`);
    state.members = await res.json();
}

async function fetchStats() {
    const res = await fetch(`${API_BASE}/stats`);
    state.stats = await res.json();
}

async function fetchItems() {
    let url = `${API_BASE}/itens?`;
    if (state.activeFilters.busca) {
        url += `busca=${encodeURIComponent(state.activeFilters.busca)}&`;
    }
    if (state.activeFilters.status && state.activeFilters.status !== 'TODOS') {
        url += `status=${encodeURIComponent(state.activeFilters.status)}&`;
    }
    if (state.activeFilters.categoria_id && state.activeFilters.categoria_id !== 'TODAS') {
        url += `categoria_id=${encodeURIComponent(state.activeFilters.categoria_id)}&`;
    }
    const res = await fetch(url);
    state.items = await res.json();
}

async function fetchMovements() {
    const res = await fetch(`${API_BASE}/movimentacoes`);
    state.movements = await res.json();
}

// ==========================================================================
// RENDERIZADORES DE TELA
// ==========================================================================

function renderKPIs() {
    if (!state.stats) return;
    const { kpis, destaques } = state.stats;

    document.getElementById('kpi-total').textContent = kpis.total_itens || 0;
    document.getElementById('kpi-borrowed').textContent = kpis.emprestados || 0;
    document.getElementById('kpi-available').textContent = kpis.disponiveis || 0;
    document.getElementById('kpi-maintenance').textContent = (kpis.manutencao + kpis.confiscados) || 0;

    const infrator = destaques.campeao_retiradas;
    if (infrator) {
        document.getElementById('kpi-infrator-avatar').textContent = infrator.avatar_icone || '👦';
        document.getElementById('kpi-infrator-nome').textContent = `${infrator.nome} (${infrator.total_retiradas}x)`;
        document.getElementById('kpi-infrator-detalhe').textContent = `Nível de Perigo: ${infrator.nivel_perigo}`;
    } else {
        document.getElementById('kpi-infrator-nome').textContent = 'Nenhum';
    }
}

function updateBadges() {
    const totalInventario = state.items.length;
    const totalEmprestimos = state.movements.filter(m => m.status === 'ABERTO' || m.status === 'ATRASADO').length;

    document.getElementById('badge-count-inventario').textContent = totalInventario;
    document.getElementById('badge-count-emprestimos').textContent = totalEmprestimos;
}

function renderCategoriesSelect() {
    const filterSelect = document.getElementById('filter-categoria');
    const formItemSelect = document.getElementById('item-categoria');

    if (filterSelect) {
        let html = '<option value="TODAS">Todas as Categorias</option>';
        state.categories.forEach(cat => {
            html += `<option value="${cat.id}">${cat.icone} ${cat.nome}</option>`;
        });
        filterSelect.innerHTML = html;
        filterSelect.value = state.activeFilters.categoria_id;
    }

    if (formItemSelect) {
        let html = '';
        state.categories.forEach(cat => {
            html += `<option value="${cat.id}">${cat.icone} ${cat.nome}</option>`;
        });
        formItemSelect.innerHTML = html;
    }
}

function renderItemsGrid() {
    const grid = document.getElementById('items-grid');
    if (!grid) return;

    if (state.items.length === 0) {
        grid.innerHTML = `
            <div style="grid-column: 1 / -1; text-align: center; padding: 3rem; background: var(--bg-surface); border-radius: var(--radius-lg); border: 1px dashed var(--border-color);">
                <span style="font-size: 2.5rem; display: block; margin-bottom: 0.5rem;">🔍</span>
                <h3 style="font-size: 1.15rem; color: var(--text-primary);">Nenhum equipamento encontrado</h3>
                <p style="color: var(--text-muted); font-size: 0.88rem; margin-top: 0.25rem;">Tente ajustar os filtros de busca ou cadastre um novo item.</p>
            </div>
        `;
        return;
    }

    grid.innerHTML = state.items.map(item => {
        const isDisponivel = item.status === 'DISPONIVEL';
        const isEmprestado = item.status === 'EMPRESTADO';
        
        let statusBadge = '';
        if (item.status === 'DISPONIVEL') {
            statusBadge = '<span class="badge badge-disponivel">🟢 No Armário</span>';
        } else if (item.status === 'EMPRESTADO') {
            statusBadge = `<span class="badge badge-emprestado">🟡 Com ${item.posse_atual || 'Alguém'}</span>`;
        } else if (item.status === 'MANUTENCAO') {
            statusBadge = '<span class="badge badge-manutencao">🔧 Em Reparo</span>';
        } else if (item.status === 'CONFISCADO_MARIA') {
            statusBadge = '<span class="badge badge-confiscado">👡 Confiscado pela Maria</span>';
        }

        return `
            <article class="item-card">
                <div class="item-card-header">
                    <div class="item-badge-wrap">
                        <div class="item-icon">${item.icone || '📦'}</div>
                        <div class="item-title-block">
                            <h3>${escapeHtml(item.nome)}</h3>
                            <span class="item-serial">${item.numero_serie}</span>
                        </div>
                    </div>
                </div>

                <div>${statusBadge}</div>

                <p class="item-desc">${escapeHtml(item.descricao || 'Sem observações cadastradas.')}</p>

                <div class="item-meta-info">
                    <div class="item-meta-row">
                        <span>🏷️ Categoria:</span>
                        <strong>${item.categoria_icone || '📁'} ${item.categoria_nome || 'Geral'}</strong>
                    </div>
                    <div class="item-meta-row">
                        <span>📍 Local na Casa:</span>
                        <strong>${escapeHtml(item.localizacao)}</strong>
                    </div>
                    ${isEmprestado ? `
                        <div class="item-meta-row" style="color: #fbbf24; background: rgba(245, 158, 11, 0.1); padding: 0.35rem 0.5rem; border-radius: var(--radius-sm);">
                            <span>👤 Em posse de:</span>
                            <span class="posse-badge-tag">${item.posse_membro_avatar || '👤'} ${item.posse_atual}</span>
                        </div>
                    ` : ''}
                </div>

                <div class="item-actions">
                    ${isDisponivel ? `
                        <button class="btn btn-primary" onclick="openBorrowForItem(${item.id})">
                            <span>📤</span> Pegar
                        </button>
                    ` : ''}

                    ${isEmprestado ? `
                        <button class="btn btn-success" onclick="openReturnModal(${item.movimentacao_ativa_id})">
                            <span>📥</span> Devolver
                        </button>
                    ` : ''}

                    <button class="btn btn-secondary" onclick="viewItemHistory(${item.id})" title="Ver Histórico">
                        <span>📜</span>
                    </button>
                    <button class="btn btn-ghost" onclick="editItem(${item.id})" title="Editar Ativo">
                        <span>✏️</span>
                    </button>
                    ${!isEmprestado ? `
                        <button class="btn btn-ghost" onclick="deleteItem(${item.id}, '${escapeHtml(item.nome)}')" title="Excluir Ativo" style="color: var(--rose);">
                            <span>🗑️</span>
                        </button>
                    ` : ''}
                </div>
            </article>
        `;
    }).join('');
}

function renderActiveLoans() {
    const grid = document.getElementById('active-loans-grid');
    if (!grid) return;

    const activeLoans = state.movements.filter(m => m.status === 'ABERTO' || m.status === 'ATRASADO');

    if (activeLoans.length === 0) {
        grid.innerHTML = `
            <div style="grid-column: 1 / -1; text-align: center; padding: 3rem; background: var(--bg-surface); border-radius: var(--radius-lg); border: 1px dashed var(--border-color);">
                <span style="font-size: 2.5rem; display: block; margin-bottom: 0.5rem;">🎉</span>
                <h3 style="font-size: 1.15rem; color: var(--text-primary);">Nenhum equipamento emprestado no momento!</h3>
                <p style="color: var(--text-muted); font-size: 0.88rem; margin-top: 0.25rem;">Todos os ativos da família estão sãos e salvos guardados nos armários.</p>
            </div>
        `;
        return;
    }

    grid.innerHTML = activeLoans.map(loan => {
        const isOverdue = loan.status === 'ATRASADO';
        return `
            <article class="loan-card ${isOverdue ? 'overdue' : ''}">
                <div class="loan-header">
                    <div class="loan-member-info">
                        <div class="loan-member-avatar">${loan.membro_avatar || '👤'}</div>
                        <div class="loan-member-names">
                            <h4>${loan.membro_nome}</h4>
                            <span>${loan.membro_apelido}</span>
                        </div>
                    </div>
                    ${isOverdue ? '<span class="badge badge-confiscado">⏰ Atrasado!</span>' : '<span class="badge badge-emprestado">⏳ Em Uso</span>'}
                </div>

                <div class="loan-item-box">
                    <h5>${loan.item_icone || '📦'} ${escapeHtml(loan.item_nome)}</h5>
                    <span class="item-serial">${loan.item_numero_serie}</span>
                    <p class="loan-motivo">“${escapeHtml(loan.motivo)}”</p>
                </div>

                <div class="loan-dates">
                    <span>📅 Retirado: ${formatDate(loan.data_retirada)}</span>
                    <span style="font-weight: 600; color: ${isOverdue ? 'var(--rose)' : 'var(--amber)'};">
                        Devolver até: ${formatDate(loan.data_prevista)}
                    </span>
                </div>

                <button class="btn btn-success" style="width: 100%;" onclick="openReturnModal(${loan.id})">
                    <span>📥</span> Registrar Devolução & Vistoria
                </button>
            </article>
        `;
    }).join('');
}

function renderMembersGrid() {
    const grid = document.getElementById('members-grid');
    if (!grid) return;

    grid.innerHTML = state.members.map(member => {
        let dangerClass = 'danger-medio';
        const nivel = (member.nivel_perigo || '').toLowerCase();
        if (nivel === 'baixo') dangerClass = 'danger-baixo';
        else if (nivel === 'médio' || nivel === 'medio') dangerClass = 'danger-medio';
        else if (nivel === 'alto') dangerClass = 'danger-alto';
        else if (nivel === 'crítico' || nivel === 'critico') dangerClass = 'danger-critico';
        else if (nivel === 'caótico' || nivel === 'caotico') dangerClass = 'danger-caotico';

        return `
            <article class="member-card">
                <div class="member-header">
                    <div class="member-avatar">${member.avatar_icone || '👤'}</div>
                    <div class="member-info">
                        <h3>${member.nome}</h3>
                        <div class="member-apelido">${member.apelido}</div>
                        <div class="member-role">${member.papel}</div>
                    </div>
                </div>

                <div style="display: flex; justify-content: space-between; align-items: center;">
                    <span class="danger-tag ${dangerClass}">Perigo: ${member.nivel_perigo}</span>
                    <span style="font-size: 0.78rem; color: var(--text-muted);">Reputação: <strong>${member.reputacao_score}/100</strong></span>
                </div>

                <p class="member-desc">${escapeHtml(member.descricao)}</p>

                <div class="member-stats-row">
                    <div class="stat-box">
                        <div class="stat-box-val" style="color: var(--amber);">${member.itens_em_posse || 0}</div>
                        <div class="stat-box-lbl">Em Posse</div>
                    </div>
                    <div class="stat-box">
                        <div class="stat-box-val" style="color: var(--primary);">${member.total_emprestimos || 0}</div>
                        <div class="stat-box-lbl">Retiradas</div>
                    </div>
                    <div class="stat-box">
                        <div class="stat-box-val" style="color: var(--rose);">${member.total_castigos || 0}</div>
                        <div class="stat-box-lbl">Castigos</div>
                    </div>
                </div>

                <button class="btn btn-secondary" onclick="viewMemberProfile(${member.id})" style="width: 100%;">
                    <span>👤</span> Ver Ficha & Histórico
                </button>
            </article>
        `;
    }).join('');
}

function renderHistoryFeed() {
    const feed = document.getElementById('history-feed');
    if (!feed) return;

    if (state.movements.length === 0) {
        feed.innerHTML = `
            <div style="text-align: center; padding: 3rem; background: var(--bg-surface); border-radius: var(--radius-lg); border: 1px dashed var(--border-color);">
                <p style="color: var(--text-muted);">Nenhuma ocorrência registrada no livro negro da família ainda.</p>
            </div>
        `;
        return;
    }

    feed.innerHTML = state.movements.map(mov => {
        const isConcluido = mov.status === 'CONCLUIDO';
        let condicaoLabel = '';
        if (mov.condicao_devolucao) {
            const condMap = {
                'PERFEITO': '✨ Devolvido Perfeito',
                'ARRANHADO': '🩹 Devolvido Arranhado',
                'ROIDO_PELA_TITI': '🐶 Roído pela Titi',
                'QUEBRADO_CARLINHOS': '💥 Quebrado pelo Carlinhos',
                'MOLHADO_CLEUSA': '💦 Molhado pela Cleusa',
                'DESAPARECIDO': '❓ Desaparecido'
            };
            condicaoLabel = condMap[mov.condicao_devolucao] || mov.condicao_devolucao;
        }

        return `
            <div class="history-card">
                <div class="history-main-info">
                    <div class="history-icon-badge">${mov.item_icone || '📦'}</div>
                    <div class="history-details">
                        <h4>${mov.membro_avatar || '👤'} ${mov.membro_nome} pegou <strong>${escapeHtml(mov.item_nome)}</strong> (${mov.item_numero_serie})</h4>
                        <p class="history-motivo"><strong>Motivo:</strong> “${escapeHtml(mov.motivo)}”</p>
                        
                        ${isConcluido ? `
                            <div style="margin-top: 0.35rem; font-size: 0.82rem; color: var(--emerald);">
                                <strong>Vistoria:</strong> ${condicaoLabel}
                            </div>
                        ` : `
                            <div style="margin-top: 0.35rem; font-size: 0.82rem; color: var(--amber);">
                                <strong>Status:</strong> Empréstimo em andamento
                            </div>
                        `}

                        ${mov.castigo_aplicado ? `
                            <div class="history-castigo">
                                <span>👡 <strong>Castigo Aplicado:</strong> ${escapeHtml(mov.castigo_aplicado)}</span>
                            </div>
                        ` : ''}

                        ${mov.observacoes ? `
                            <p style="font-size: 0.78rem; color: var(--text-muted); margin-top: 0.25rem;">
                                <em>Nota: ${escapeHtml(mov.observacoes)}</em>
                            </p>
                        ` : ''}
                    </div>
                </div>

                <div class="history-dates">
                    <div>Saída: ${formatDate(mov.data_retirada)}</div>
                    ${mov.data_devolucao ? `<div>Devolvido: ${formatDate(mov.data_devolucao)}</div>` : `<div style="color: var(--amber);">Prazo: ${formatDate(mov.data_prevista)}</div>`}
                </div>
            </div>
        `;
    }).join('');
}

// ==========================================================================
// FILTROS E BUSCA
// ==========================================================================

let searchTimeout = null;
function handleSearch() {
    clearTimeout(searchTimeout);
    searchTimeout = setTimeout(() => {
        state.activeFilters.busca = document.getElementById('search-input').value;
        fetchItems().then(() => renderItemsGrid());
    }, 250);
}

function applyFilters() {
    state.activeFilters.status = document.getElementById('filter-status').value;
    state.activeFilters.categoria_id = document.getElementById('filter-categoria').value;
    fetchItems().then(() => renderItemsGrid());
}

function switchTab(tabId) {
    state.currentTab = tabId;
    document.querySelectorAll('.nav-tab').forEach(tab => {
        tab.classList.toggle('active', tab.dataset.tab === tabId);
    });
    document.querySelectorAll('.tab-pane').forEach(pane => {
        pane.classList.toggle('active', pane.id === tabId);
    });
}

// ==========================================================================
// MODAL: NOVO EMPRÉSTIMO
// ==========================================================================

function openBorrowModal(preselectedItemId = null) {
    const itemSelect = document.getElementById('borrow-item-select');
    const memberSelect = document.getElementById('borrow-member-select');

    // Preencher itens disponíveis
    const disponiveis = state.items.filter(i => i.status === 'DISPONIVEL');
    if (disponiveis.length === 0) {
        showToast('Não há nenhum equipamento disponível no armário para empréstimo!', 'warning');
        return;
    }

    itemSelect.innerHTML = '<option value="">-- Escolha um equipamento --</option>' + 
        disponiveis.map(i => `<option value="${i.id}">${i.icone} ${escapeHtml(i.nome)} (${i.numero_serie})</option>`).join('');

    if (preselectedItemId) {
        itemSelect.value = preselectedItemId;
    }

    // Preencher membros
    memberSelect.innerHTML = '<option value="">-- Escolha o integrante da família --</option>' + 
        state.members.map(m => `<option value="${m.id}">${m.avatar_icone} ${m.nome} - ${m.apelido}</option>`).join('');

    document.getElementById('borrow-motivo').value = '';
    document.getElementById('borrow-obs').value = '';
    document.getElementById('borrow-dias').value = '1';
    document.getElementById('borrow-member-preview').classList.add('hidden');

    openModal('modal-borrow');
}

function openBorrowForItem(itemId) {
    openBorrowModal(itemId);
}

function handleMemberSelectPreview(memberId) {
    const previewBox = document.getElementById('borrow-member-preview');
    if (!memberId) {
        previewBox.classList.add('hidden');
        return;
    }

    const member = state.members.find(m => m.id == memberId);
    if (!member) return;

    previewBox.classList.remove('hidden');
    previewBox.innerHTML = `
        <div style="display: flex; align-items: center; gap: 0.65rem;">
            <span style="font-size: 1.8rem;">${member.avatar_icone}</span>
            <div>
                <strong>${member.nome} (${member.apelido})</strong>
                <div style="font-size: 0.78rem; color: var(--text-muted);">${member.descricao}</div>
                <div style="margin-top: 0.25rem; font-size: 0.75rem; color: #fbbf24;">
                    ⚠️ Nível de Perigo: <strong>${member.nivel_perigo}</strong> | Itens já em posse: <strong>${member.itens_em_posse}</strong>
                </div>
            </div>
        </div>
    `;
}

function setBorrowMotivo(preset) {
    document.getElementById('borrow-motivo').value = preset;
}

async function handleBorrowSubmit(e) {
    e.preventDefault();
    const itemId = parseInt(document.getElementById('borrow-item-select').value);
    const memberId = parseInt(document.getElementById('borrow-member-select').value);
    const motivo = document.getElementById('borrow-motivo').value;
    const dias = parseInt(document.getElementById('borrow-dias').value);
    const obs = document.getElementById('borrow-obs').value;

    try {
        const res = await fetch(`${API_BASE}/movimentacoes/retirada`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                item_id: itemId,
                membro_id: memberId,
                motivo: motivo,
                dias_previstos: dias,
                observacoes: obs
            })
        });

        const data = await res.json();
        if (!res.ok) {
            throw new Error(data.detail || 'Erro ao registrar saída.');
        }

        closeModal('modal-borrow');
        showToast(data.mensagem, 'success');
        await refreshAll();
    } catch (err) {
        showToast(err.message, 'error');
    }
}

// ==========================================================================
// MODAL: DEVOLUÇÃO & VISTORIA
// ==========================================================================

function openReturnModal(movementId) {
    const mov = state.movements.find(m => m.id == movementId);
    if (!mov) {
        showToast('Movimentação não encontrada.', 'error');
        return;
    }

    document.getElementById('return-mov-id').value = mov.id;
    document.getElementById('return-summary').innerHTML = `
        <span style="font-size: 2rem;">${mov.item_icone || '📦'}</span>
        <div>
            <h4 style="font-size: 1.05rem;">${escapeHtml(mov.item_nome)} <span class="item-serial">${mov.item_numero_serie}</span></h4>
            <p style="font-size: 0.82rem; color: var(--text-muted);">
                Retirado por: <strong>${mov.membro_avatar} ${mov.membro_nome}</strong> em ${formatDate(mov.data_retirada)}
            </p>
        </div>
    `;

    document.getElementById('return-condicao').value = 'PERFEITO';
    document.getElementById('return-castigo').value = '';
    document.getElementById('return-obs').value = '';
    document.getElementById('return-status-item').value = 'DISPONIVEL';
    document.getElementById('box-castigo').classList.add('hidden');

    openModal('modal-return');
}

function handleConditionChange(cond) {
    const castigoBox = document.getElementById('box-castigo');
    const statusSelect = document.getElementById('return-status-item');

    if (cond !== 'PERFEITO') {
        castigoBox.classList.remove('hidden');
        if (cond === 'QUEBRADO_CARLINHOS' || cond === 'ROIDO_PELA_TITI') {
            statusSelect.value = 'MANUTENCAO';
        }
    } else {
        castigoBox.classList.add('hidden');
        statusSelect.value = 'DISPONIVEL';
    }
}

function setCastigo(preset) {
    document.getElementById('return-castigo').value = preset;
}

async function handleReturnSubmit(e) {
    e.preventDefault();
    const movId = parseInt(document.getElementById('return-mov-id').value);
    const condicao = document.getElementById('return-condicao').value;
    const castigo = document.getElementById('return-castigo').value;
    const novoStatus = document.getElementById('return-status-item').value;
    const obs = document.getElementById('return-obs').value;

    try {
        const res = await fetch(`${API_BASE}/movimentacoes/devolucao`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                movimentacao_id: movId,
                condicao_devolucao: condicao,
                castigo_aplicado: castigo,
                observacoes: obs,
                novo_status_item: novoStatus
            })
        });

        const data = await res.json();
        if (!res.ok) {
            throw new Error(data.detail || 'Erro ao registrar devolução.');
        }

        closeModal('modal-return');
        showToast(data.mensagem, 'success');
        await refreshAll();
    } catch (err) {
        showToast(err.message, 'error');
    }
}

// ==========================================================================
// MODAL: CADASTRAR / EDITAR ITEM
// ==========================================================================

function openItemModal() {
    document.getElementById('modal-item-title').textContent = 'Cadastrar Novo Equipamento';
    document.getElementById('modal-item-icon-title').textContent = '➕';
    document.getElementById('btn-save-item').textContent = 'Cadastrar Equipamento';
    document.getElementById('item-edit-id').value = '';
    
    document.getElementById('item-nome').value = '';
    document.getElementById('item-icone').value = '📦';
    document.getElementById('item-serial').value = '';
    document.getElementById('item-serial').disabled = false;
    document.getElementById('item-localizacao').value = 'Armário Central da Casa';
    document.getElementById('item-descricao').value = '';

    renderCategoriesSelect();
    openModal('modal-item');
}

function editItem(itemId) {
    const item = state.items.find(i => i.id == itemId);
    if (!item) return;

    document.getElementById('modal-item-title').textContent = 'Editar Equipamento';
    document.getElementById('modal-item-icon-title').textContent = '✏️';
    document.getElementById('btn-save-item').textContent = 'Salvar Alterações';
    document.getElementById('item-edit-id').value = item.id;

    document.getElementById('item-nome').value = item.nome;
    document.getElementById('item-icone').value = item.icone || '📦';
    document.getElementById('item-serial').value = item.numero_serie;
    document.getElementById('item-serial').disabled = true; // Não altera serial existente
    document.getElementById('item-categoria').value = item.categoria_id;
    document.getElementById('item-localizacao').value = item.localizacao;
    document.getElementById('item-descricao').value = item.descricao || '';

    openModal('modal-item');
}

function generateSerial() {
    const prefixos = ['FERR', 'ELET', 'LIM', 'BRINQ', 'MIL', 'MARIA', 'CASA'];
    const prefix = prefixos[Math.floor(Math.random() * prefixos.length)];
    const num = Math.floor(100 + Math.random() * 900);
    const suf = Math.random().toString(36).substring(2, 5).toUpperCase();
    document.getElementById('item-serial').value = `${prefix}-${num}-${suf}`;
}

async function handleItemSubmit(e) {
    e.preventDefault();
    const editId = document.getElementById('item-edit-id').value;
    const nome = document.getElementById('item-nome').value;
    const icone = document.getElementById('item-icone').value;
    const categoria_id = parseInt(document.getElementById('item-categoria').value);
    const numero_serie = document.getElementById('item-serial').value;
    const localizacao = document.getElementById('item-localizacao').value;
    const descricao = document.getElementById('item-descricao').value;

    try {
        let res;
        if (editId) {
            // Update
            res = await fetch(`${API_BASE}/itens/${editId}`, {
                method: 'PUT',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    nome,
                    icone,
                    categoria_id,
                    localizacao,
                    descricao
                })
            });
        } else {
            // Create
            res = await fetch(`${API_BASE}/itens`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    nome,
                    icone,
                    categoria_id,
                    numero_serie,
                    localizacao,
                    descricao
                })
            });
        }

        const data = await res.json();
        if (!res.ok) throw new Error(data.detail || 'Erro ao salvar equipamento.');

        closeModal('modal-item');
        showToast(data.mensagem || 'Equipamento salvo com sucesso!', 'success');
        await refreshAll();
    } catch (err) {
        showToast(err.message, 'error');
    }
}

async function deleteItem(itemId, itemNome) {
    if (!confirm(`Tem certeza que deseja remover '${itemNome}' do inventário familiar?`)) return;

    try {
        const res = await fetch(`${API_BASE}/itens/${itemId}`, { method: 'DELETE' });
        const data = await res.json();
        if (!res.ok) throw new Error(data.detail || 'Erro ao excluir equipamento.');

        showToast(data.mensagem, 'success');
        await refreshAll();
    } catch (err) {
        showToast(err.message, 'error');
    }
}

// ==========================================================================
// MODAL: HISTÓRICO INDIVIDUAL DO ITEM
// ==========================================================================

async function viewItemHistory(itemId) {
    try {
        const res = await fetch(`${API_BASE}/itens/${itemId}`);
        const item = await res.json();
        if (!res.ok) throw new Error(item.detail || 'Erro ao buscar dados do item.');

        document.getElementById('history-item-icon').textContent = item.icone || '📦';
        document.getElementById('history-item-nome').textContent = item.nome;
        document.getElementById('history-item-serial').textContent = `Número de Série: ${item.numero_serie} | Local: ${item.localizacao}`;

        document.getElementById('history-item-details').innerHTML = `
            <p><strong>Categoria:</strong> ${item.categoria_icone} ${item.categoria_nome} | <strong>Status Atual:</strong> ${item.status}</p>
            <p style="margin-top: 0.25rem; color: var(--text-secondary);">${escapeHtml(item.descricao || 'Sem descrição cadastrada.')}</p>
        `;

        const timeline = document.getElementById('history-item-timeline');
        if (!item.historico || item.historico.length === 0) {
            timeline.innerHTML = '<p style="color: var(--text-muted); font-size: 0.88rem;">Nenhuma saída registrada para este equipamento ainda.</p>';
        } else {
            timeline.innerHTML = item.historico.map(h => `
                <div class="timeline-entry">
                    <div style="display: flex; justify-content: space-between; font-size: 0.8rem; color: var(--text-muted);">
                        <span>Retirada: ${formatDate(h.data_retirada)}</span>
                        <span>${h.data_devolucao ? `Devolução: ${formatDate(h.data_devolucao)}` : '<strong style="color: var(--amber);">Em aberto</strong>'}</span>
                    </div>
                    <div style="margin-top: 0.25rem; font-size: 0.88rem;">
                        <strong>${h.membro_avatar} ${h.membro_nome}:</strong> “${escapeHtml(h.motivo)}”
                    </div>
                    ${h.condicao_devolucao ? `<div style="font-size: 0.78rem; color: var(--emerald); margin-top: 0.15rem;">Vistoria: ${h.condicao_devolucao}</div>` : ''}
                    ${h.castigo_aplicado ? `<div style="font-size: 0.78rem; color: var(--rose); margin-top: 0.15rem;">👡 Castigo: ${escapeHtml(h.castigo_aplicado)}</div>` : ''}
                </div>
            `).join('');
        }

        openModal('modal-item-history');
    } catch (err) {
        showToast(err.message, 'error');
    }
}

// ==========================================================================
// MODAL: PERFIL DO INTEGRANTE
// ==========================================================================

async function viewMemberProfile(memberId) {
    try {
        const res = await fetch(`${API_BASE}/membros/${memberId}`);
        const member = await res.json();
        if (!res.ok) throw new Error(member.detail || 'Erro ao carregar perfil do integrante.');

        document.getElementById('profile-avatar').textContent = member.avatar_icone || '👤';
        document.getElementById('profile-nome').textContent = `${member.nome} (${member.apelido})`;
        document.getElementById('profile-papel').textContent = `${member.papel} | Perigo: ${member.nivel_perigo}`;

        document.getElementById('profile-header-card').innerHTML = `
            <p style="font-size: 0.9rem; color: var(--text-secondary);">${escapeHtml(member.descricao)}</p>
            <div style="margin-top: 0.5rem; display: flex; gap: 1rem; font-size: 0.82rem;">
                <span>Reputação Patrimonial: <strong>${member.reputacao_score}/100</strong></span>
            </div>
        `;

        const curItemsBox = document.getElementById('profile-current-items');
        if (!member.itens_em_posse || member.itens_em_posse.length === 0) {
            curItemsBox.innerHTML = '<p style="color: var(--text-muted); font-size: 0.85rem;">Nenhum item em mãos no momento.</p>';
        } else {
            curItemsBox.innerHTML = member.itens_em_posse.map(i => `
                <div style="background: var(--bg-surface-raised); padding: 0.55rem 0.85rem; border-radius: var(--radius-md); display: flex; justify-content: space-between; align-items: center; border-left: 3px solid var(--amber);">
                    <span>${i.item_icone} <strong>${escapeHtml(i.item_nome)}</strong> (${i.numero_serie})</span>
                    <button class="btn btn-tiny" onclick="closeModal('modal-member-profile'); openReturnModal(${i.movimentacao_id});">Devolver</button>
                </div>
            `).join('');
        }

        const histTimeline = document.getElementById('profile-history-timeline');
        if (!member.historico || member.historico.length === 0) {
            histTimeline.innerHTML = '<p style="color: var(--text-muted); font-size: 0.85rem;">Nenhum histórico registrado.</p>';
        } else {
            histTimeline.innerHTML = member.historico.map(h => `
                <div class="timeline-entry">
                    <div style="font-size: 0.85rem;">${h.item_icone} Pegou <strong>${escapeHtml(h.item_nome)}</strong></div>
                    <div style="font-size: 0.78rem; color: var(--text-muted);">Motivo: “${escapeHtml(h.motivo)}”</div>
                    ${h.castigo_aplicado ? `<div style="font-size: 0.78rem; color: var(--rose); margin-top: 0.2rem;">👡 Castigo: ${escapeHtml(h.castigo_aplicado)}</div>` : ''}
                </div>
            `).join('');
        }

        openModal('modal-member-profile');
    } catch (err) {
        showToast(err.message, 'error');
    }
}

// ==========================================================================
// RESETAR BANCO
// ==========================================================================

async function resetDatabase() {
    if (!confirm('Deseja realmente restaurar os dados originais da família para demonstração?')) return;

    try {
        const res = await fetch(`${API_BASE}/stats/reset-banco`, { method: 'POST' });
        const data = await res.json();
        showToast(data.mensagem, 'info');
        await refreshAll();
    } catch (err) {
        showToast('Erro ao restaurar banco de dados.', 'error');
    }
}

// ==========================================================================
// UTILITÁRIOS & HELPERS
// ==========================================================================

async function refreshAll() {
    await Promise.all([
        fetchCategories(),
        fetchMembers(),
        fetchStats(),
        fetchItems(),
        fetchMovements()
    ]);
    renderAll();
}

function openModal(modalId) {
    document.getElementById(modalId).classList.remove('hidden');
}

function closeModal(modalId) {
    document.getElementById(modalId).classList.add('hidden');
}

function showToast(msg, type = 'info') {
    const container = document.getElementById('toast-container');
    if (!container) return;

    const icons = {
        success: '✅',
        error: '❌',
        warning: '⚠️',
        info: 'ℹ️'
    };

    const toast = document.createElement('div');
    toast.className = `toast toast-${type}`;
    toast.innerHTML = `<span>${icons[type] || 'ℹ️'}</span> <span>${escapeHtml(msg)}</span>`;
    container.appendChild(toast);

    setTimeout(() => {
        toast.style.opacity = '0';
        toast.style.transform = 'translateY(10px)';
        toast.style.transition = 'all 0.3s ease';
        setTimeout(() => toast.remove(), 300);
    }, 4500);
}

function formatDate(dateStr) {
    if (!dateStr) return '--';
    try {
        const d = new Date(dateStr);
        if (isNaN(d.getTime())) return dateStr;
        return d.toLocaleDateString('pt-BR', { day: '2-digit', month: '2-digit', year: 'numeric', hour: '2-digit', minute: '2-digit' });
    } catch {
        return dateStr;
    }
}

function escapeHtml(str) {
    if (!str) return '';
    return String(str)
        .replace(/&/g, '&amp;')
        .replace(/</g, '&lt;')
        .replace(/>/g, '&gt;')
        .replace(/"/g, '&quot;')
        .replace(/'/g, '&#039;');
}
