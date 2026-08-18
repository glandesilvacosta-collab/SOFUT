# 🏠⚙️ Patrimônio da Família - Sistema de Gestão de Ativos e Equipamentos

Sistema Full-Stack completo de controle de inventário, empréstimos, devoluções e vistorias de equipamentos, adaptado com o tema e as personalidades dos **8 Integrantes da Família**.

---

## 👥 Integrantes da Família (Personagens & Entidades)

| Integrante | Papel | Características & Comportamento no Sistema |
| :--- | :--- | :--- |
| **Carlos** | Pai de Família & Chefe da Garagem | Cabeça dura demais. Dono das ferramentas sagradas e multímetros. |
| **Maria** | Matriarca & Fiscal Geral | Seus castigos são bem severos. Aplica punições e confisca itens. |
| **Carlinhos** | Especialista em Trambiques | Puxou o lado "sacana". Pega itens escondido e devolve avariado. |
| **Aninha** | Terrorista Mirim | Sorriso na cara, maldade na mente. Some com peças e culpa os outros. |
| **Cleusa** | Governanta & Rainha da Faxina | Desce molhando e sobe secando. Controla os produtos de limpeza. |
| **Julinha** | Amiga Brincalhona | Gosta de brincar demais e tem talento para desintegrar peças. |
| **Didi** | Veterano de Guerra | Mantém disciplina militar no inventário e faz vistoria tática. |
| **Titi** | Cão de Guarda | Roe, lambe e late. Mas não morde pessoas... só mastiga cabos e controles. |

---

## 🚀 Como Executar

### Opção 1: Clicar no Arquivo Batch (Windows)
Dê um duplo clique no arquivo:
```
iniciar_sistema.bat
```

### Opção 2: Pelo Terminal / PowerShell
No diretório `C:\Users\PROG05\Desktop\Estrupicio\sotuf`:
```bash
python run.py
```
O navegador abrirá automaticamente em `http://127.0.0.1:8000`.

---

## 🗄️ Modelagem Relacional do Banco de Dados (SQLite)

O banco é criado automaticamente em `backend/familia_ativos.db`:

1. **`membros`**: Cadastro dos 8 integrantes com seus perfis, avatares, nível de perigo e índice de reputação.
2. **`categorias`**: Organização dos itens (Oficina do Carlos, Arsenal do Didi, Faxina da Cleusa, etc.).
3. **`itens`**: Equipamentos cadastrados com número de série único, localização na casa e status (`DISPONIVEL`, `EMPRESTADO`, `MANUTENCAO`, `CONFISCADO_MARIA`).
4. **`movimentacoes`**: Histórico relacional de empréstimos, registrando quem pegou, data de retirada, prazo previsto, data de devolução, estado na vistoria (`PERFEITO`, `ARRANHADO`, `ROIDO_PELA_TITI`, `QUEBRADO_CARLINHOS`, `MOLHADO_CLEUSA`) e castigos da Dona Maria.

---

## 📡 Endpoints da API REST (FastAPI)

Acesse a documentação interativa Swagger em: `http://127.0.0.1:8000/docs`

### 📦 Equipamentos / Ativos (`/api/itens`)
- `GET /api/itens` - Listar inventário com filtros de busca, status e categoria
- `GET /api/itens/{id}` - Obter detalhes e linha do tempo de um item
- `POST /api/itens` - Registrar novo equipamento com número de série único
- `PUT /api/itens/{id}` - Atualizar informações do equipamento
- `DELETE /api/itens/{id}` - Remover equipamento do inventário
- `GET /api/itens/categorias` - Listar categorias disponíveis

### 👥 Integrantes da Família (`/api/membros`)
- `GET /api/membros` - Listar os 8 integrantes com contadores de itens em posse e castigos
- `GET /api/membros/{id}` - Ficha detalhada do membro e histórico individual

### 🔄 Movimentações & Vistorias (`/api/movimentacoes`)
- `POST /api/movimentacoes/retirada` - Registrar saída / empréstimo para um membro
- `POST /api/movimentacoes/devolucao` - Registrar devolução com vistoria de danos e aplicação de castigos
- `GET /api/movimentacoes` - Histórico completo das movimentações

### 📊 Estatísticas (`/api/stats`)
- `GET /api/stats` - KPIs do painel, ranking do mais folgado e itens mais disputados
- `POST /api/stats/reset-banco` - Restaurar dados de demonstração da família

---

## 🎨 Funcionalidades do Frontend
- **Design System Moderno**: Dark slate & warm amber theme, cards elegantes e tipografia nítida (Google Fonts Outfit + Plus Jakarta Sans).
- **Dashboard com KPIs em Tempo Real**: Total de itens, emprestados, disponíveis, em reparo e destaque do "Campeão de Trambiques".
- **Filtros e Busca Instantânea**: Pesquise por nome, serial ou cômodo da casa.
- **Modais Dinâmicos**: Retirada com preview do integrante, devolução com vistoria e aplicação de castigos da Dona Maria, cadastro com gerador de número de tombo.
- **Livro Negro da Família**: Feed cronológico de ocorrências, avarias e punições.
