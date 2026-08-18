from database import get_db_connection, init_db
from datetime import datetime, timedelta

def seed_data(force=False):
    init_db()
    conn = get_db_connection()
    cursor = conn.cursor()

    if force:
        cursor.execute("DELETE FROM movimentacoes;")
        cursor.execute("DELETE FROM itens;")
        cursor.execute("DELETE FROM membros;")
        cursor.execute("DELETE FROM categorias;")

    # Verificar se já existem membros cadastrados
    cursor.execute("SELECT COUNT(*) FROM membros;")
    count = cursor.fetchone()[0]
    if count > 0 and not force:
        conn.close()
        return

    # 1. Inserir Categorias
    categorias = [
        ("Oficina & Garagem do Carlos", "🔧", "Equipamentos pesados, multímetros, furadeiras e chaves inglesas sagradas."),
        ("Arsenal Tático do Didi", "🪖", "Equipamentos militares de sobrevivência, lanternas táticas e rádios comunicadores."),
        ("Arsenal de Faxina da Cleusa", "🧹", "Aspiradores, baldes turbo, vassouras mágicas e panos sagrados."),
        ("Eletrônicos & Casa Conectada", "📺", "Controles remotos, caixas de som, carregadores e cabos HDMI."),
        ("Brinquedos & Trapaças", "🎮", "Videogames, jogos de tabuleiro, skates e diários secretos."),
        ("Artigos da Matriarca Maria", "👡", "Chinelos de mira teleguiada, caderneta do ódio e utensílios gourmet."),
        ("Artigos Pet & Mastigação", "🦴", "Mordedores, coleiras e itens sob proteção contra a Titi.")
    ]
    cursor.executemany("INSERT INTO categorias (nome, icone, descricao) VALUES (?, ?, ?);", categorias)
    conn.commit()

    # 2. Inserir os 8 Integrantes da Família
    membros = [
        (
            "Carlos",
            "O Pai Cabeça Dura",
            "Pai de Família & Chefe da Garagem",
            "Cabeça dura demais. Não aceita que mexam nas suas ferramentas sem permissão e acha que conserta qualquer coisa no soco.",
            "👨‍🦳",
            "Médio",
            85
        ),
        (
            "Maria",
            "A Matriarca Severa",
            "Matriarca & Fiscal Geral da Casa",
            "Seus castigos são bem severos. Se algum item voltar quebrado ou sujo, o infrator vai direto para a caderneta do ódio e perde regalias.",
            "👩‍🦱",
            "Baixo",
            98
        ),
        (
            "Carlinhos",
            "O Filho Sacana",
            "Especialista em Gambiarras & Trambiques",
            "O filho que puxou o lado mais sacana da família. Pega ferramentas escondido, desmonta eletrônicos e devolve colado com cuspe.",
            "👦",
            "Crítico",
            40
        ),
        (
            "Aninha",
            "Sorriso Maldoso",
            "Terrorista Doméstica Mirim",
            "Sorriso na cara, maldade na mente. Pega itens sem pedir, esconde os manuais e joga a culpa no Carlinhos.",
            "👧",
            "Alto",
            50
        ),
        (
            "Cleusa",
            "A Rainha da Faxina",
            "Governanta & Senhora da Limpeza",
            "Desce molhando e sobe secando. Se alguém pisar no piso molhado ou sumir com o pano de microfibra, a casa vira um inferno.",
            "🧹",
            "Baixo",
            92
        ),
        (
            "Julinha",
            "A Amiga Brincalhona",
            "Visitante Frequente & Desintegradora de Peças",
            "Amiga da Aninha, gosta de brincar demais. Tem um talento sobrenatural para perder botões, parafusos e controles.",
            "👱‍♀️",
            "Alto",
            60
        ),
        (
            "Didi",
            "O Veterano de Guerra",
            "Tio Tático & Sobrevivencialista",
            "Veterano de guerra casca grossa. Mantém o inventário sob disciplina militar e faz vistoria com lupa e lanterna ultravioleta.",
            "🪖",
            "Baixo",
            95
        ),
        (
            "Titi",
            "O Cão Mordedor de Cabos",
            "Segurança de Quatro Patas",
            "Roe, lambe e late. Mas não morde pessoas... só controles remotos, cabos de carregador e chinelos de borracha.",
            "🐶",
            "Caótico",
            30
        )
    ]

    cursor.executemany("""
        INSERT INTO membros (nome, apelido, papel, descricao, avatar_icone, nivel_perigo, reputacao_score)
        VALUES (?, ?, ?, ?, ?, ?, ?);
    """, membros)
    conn.commit()

    # 3. Inserir Itens / Equipamentos
    # Pegar IDs das categorias
    cursor.execute("SELECT id, nome FROM categorias;")
    cat_map = {row["nome"]: row["id"] for row in cursor.fetchall()}

    itens = [
        (
            "Multímetro Digital Profissional True-RMS",
            cat_map["Oficina & Garagem do Carlos"],
            "FERR-001-MULT",
            "Multímetro sagrado do Carlos para medir baterias e gambiarras elétricas. Proibido emprestar para o Carlinhos.",
            "Garagem - Bancada de Trabalho",
            "📟",
            "DISPONIVEL"
        ),
        (
            "Furadeira de Impacto 750W",
            cat_map["Oficina & Garagem do Carlos"],
            "FERR-002-FURAD",
            "Furadeira potente com brocas de vídia. Carlos usa para furar canos sem querer.",
            "Garagem - Caixa de Ferramentas",
            "🛠️",
            "EMPRESTADO"
        ),
        (
            "Jogo de Chaves Soquete Cromo Vanádio 46 Peças",
            cat_map["Oficina & Garagem do Carlos"],
            "FERR-003-CHV",
            "Conjunto completo. Falta apenas a chave 10mm que o Carlinhos já sumiu no passado.",
            "Garagem - Prateleira A",
            "🧰",
            "DISPONIVEL"
        ),
        (
            "Binóculo Tático Militar 10x50 com Visão Noturna",
            cat_map["Arsenal Tático do Didi"],
            "MIL-001-BINO",
            "Equipamento oficial do Didi para vigiar o portão da rua e vizinhos suspeitos.",
            "Quarto do Didi - Baú Trancado",
            "🔭",
            "DISPONIVEL"
        ),
        (
            "Lanterna Tática de Choque 5000 Lumens",
            cat_map["Arsenal Tático do Didi"],
            "MIL-002-LANT",
            "Ilumina até a alma. À prova d'água e de quedas de até 10 metros.",
            "Quarto do Didi - Suporte de Parede",
            "🔦",
            "DISPONIVEL"
        ),
        (
            "Aspirador Robô Turbo Inteligente (Cleytinho)",
            cat_map["Arsenal de Faxina da Cleusa"],
            "LIM-001-ROBO",
            "Robô aspirador apelidado de Cleytinho. Cleusa desce molhando enquanto ele passa aspirando.",
            "Área de Serviço",
            "🤖",
            "DISPONIVEL"
        ),
        (
            "Mop Giratório Turbo com Balde de Inox",
            cat_map["Arsenal de Faxina da Cleusa"],
            "LIM-002-MOP",
            "A arma secreta da Cleusa. Gira a 1200 RPM e seca qualquer piso em segundos.",
            "Lavanderia",
            "🪣",
            "EMPRESTADO"
        ),
        (
            "Controle Remoto Universal da Smart TV 4K",
            cat_map["Eletrônicos & Casa Conectada"],
            "ELET-001-CTR",
            "Item mais disputado da casa aos domingos. Possui marcas leves de dentes da Titi.",
            "Mesa de Centro da Sala",
            "📺",
            "EMPRESTADO"
        ),
        (
            "Caixa de Som Bluetooth à Prova de Explosão",
            cat_map["Eletrônicos & Casa Conectada"],
            "ELET-002-SOM",
            "Caixa de som com graves reforçados usada pela Aninha para perturbar o bairro.",
            "Rack da Sala",
            "🔊",
            "DISPONIVEL"
        ),
        (
            "Console Portátil Retrô 10.000 Jogos",
            cat_map["Brinquedos & Trapaças"],
            "BRINQ-001-GAME",
            "Videogame portátil onde Carlinhos e Aninha disputam partidas com socos no braço.",
            "Quarto das Crianças",
            "🎮",
            "EMPRESTADO"
        ),
        (
            "Chinelo Havaianas de Couro com Mira Laser (Dona Maria)",
            cat_map["Artigos da Matriarca Maria"],
            "MARIA-001-CHIN",
            "O instrumento de castigo mais temido da família. Nunca erra o alvo a até 15 metros de distância.",
            "Ao lado da Cama da Maria",
            "👡",
            "DISPONIVEL"
        ),
        (
            "Ferro de Passar a Vapor Antiaderente",
            cat_map["Arsenal de Faxina da Cleusa"],
            "LIM-003-FERRO",
            "Ferro potente. Atualmente em manutenção porque esqueceram ligado em cima da tábua.",
            "Armário da Lavanderia",
            "🧺",
            "MANUTENCAO"
        ),
        (
            "Mordedor Ultrarresistente Formato Pneu",
            cat_map["Artigos Pet & Mastigação"],
            "PET-001-PNEU",
            "Único brinquedo que sobreviveu aos dentes da Titi por mais de duas semanas.",
            "Casinha da Titi no Quintal",
            "🐕",
            "DISPONIVEL"
        )
    ]

    cursor.executemany("""
        INSERT INTO itens (nome, categoria_id, numero_serie, descricao, localizacao, icone, status)
        VALUES (?, ?, ?, ?, ?, ?, ?);
    """, itens)
    conn.commit()

    # 4. Inserir Movimentações Ativas e Históricas para demonstração
    cursor.execute("SELECT id, nome FROM membros;")
    membro_map = {row["nome"]: row["id"] for row in cursor.fetchall()}

    cursor.execute("SELECT id, numero_serie FROM itens;")
    item_map = {row["numero_serie"]: row["id"] for row in cursor.fetchall()}

    agora = datetime.now()
    ontem = agora - timedelta(days=1)
    anteontem = agora - timedelta(days=2)
    semana_passada = agora - timedelta(days=7)
    pra_amanha = agora + timedelta(days=1)
    pra_ontem = agora - timedelta(days=1)

    movimentacoes = [
        # 1. Furadeira emprestada para o Carlinhos (Ativo)
        (
            item_map["FERR-002-FURAD"],
            membro_map["Carlinhos"],
            ontem.strftime("%Y-%m-%d %H:%M:%S"),
            pra_amanha.strftime("%Y-%m-%d %H:%M:%S"),
            None,
            "Montar uma rampa de skate no quintal sem autorização do pai.",
            "ABERTO",
            None,
            None,
            "Carlos já avisou que se voltar com cheiro de queimado vai ter bronca."
        ),
        # 2. Mop Giratório emprestado para a Cleusa (Ativo)
        (
            item_map["LIM-002-MOP"],
            membro_map["Cleusa"],
            agora.strftime("%Y-%m-%d %H:%M:%S"),
            pra_amanha.strftime("%Y-%m-%d %H:%M:%S"),
            None,
            "Operação Faxina Pesada: descer molhando e subir secando.",
            "ABERTO",
            None,
            None,
            "Ninguém pode pisar na sala até as 18h."
        ),
        # 3. Controle Universal emprestado para o Carlinhos (Ativo e atrasado!)
        (
            item_map["ELET-001-CTR"],
            membro_map["Carlinhos"],
            anteontem.strftime("%Y-%m-%d %H:%M:%S"),
            pra_ontem.strftime("%Y-%m-%d %H:%M:%S"),
            None,
            "Mudar de canal escondido enquanto o pai assiste o jogo.",
            "ATRASADO",
            None,
            None,
            "Controle sumiu entre as almofadas do sofá."
        ),
        # 4. Console Portátil com a Julinha (Ativo)
        (
            item_map["BRINQ-001-GAME"],
            membro_map["Julinha"],
            ontem.strftime("%Y-%m-%d %H:%M:%S"),
            pra_amanha.strftime("%Y-%m-%d %H:%M:%S"),
            None,
            "Jogar coop com a Aninha até tarde da noite.",
            "ABERTO",
            None,
            None,
            "Prometeu que não vai desconfigurar os botões."
        ),
        # 5. Histórico: Multímetro retirado e devolvido pelo Carlos (Concluído Perfeito)
        (
            item_map["FERR-001-MULT"],
            membro_map["Carlos"],
            semana_passada.strftime("%Y-%m-%d %H:%M:%S"),
            (semana_passada + timedelta(days=2)).strftime("%Y-%m-%d %H:%M:%S"),
            (semana_passada + timedelta(days=1)).strftime("%Y-%m-%d %H:%M:%S"),
            "Testar a fiação do chuveiro que estava dando choque.",
            "CONCLUIDO",
            "PERFEITO",
            None,
            "Devolvido limpo e guardado na gaveta com chave."
        ),
        # 6. Histórico: Lanterna pega pela Aninha e devolvida com avaria (Concluído com Castigo!)
        (
            item_map["MIL-002-LANT"],
            membro_map["Aninha"],
            semana_passada.strftime("%Y-%m-%d %H:%M:%S"),
            (semana_passada + timedelta(days=1)).strftime("%Y-%m-%d %H:%M:%S"),
            (semana_passada + timedelta(days=1)).strftime("%Y-%m-%d %H:%M:%S"),
            "Assustar o Carlinhos no corredor escuro.",
            "CONCLUIDO",
            "ARRANHADO",
            "Dona Maria confiscou o celular por 24 horas e mandou lavar a louça.",
            "Deixou cair no chão da cozinha quando a Cleusa gritou."
        )
    ]

    cursor.executemany("""
        INSERT INTO movimentacoes (
            item_id, membro_id, data_retirada, data_prevista, data_devolucao,
            motivo, status, condicao_devolucao, castigo_aplicado, observacoes
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?);
    """, movimentacoes)

    conn.commit()
    conn.close()
    print("Seed executado com sucesso! Membros, categorias, itens e movimentações criados.")

if __name__ == "__main__":
    seed_data(force=True)
