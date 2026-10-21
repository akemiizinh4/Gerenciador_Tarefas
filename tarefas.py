"""
Regras de negócio do ciclo de vida das tarefas.

Cada etapa do ciclo (criar, pegar a próxima tarefa, atualizar prioridade,
concluir, arquivar, excluir e gerar relatórios) é uma função independente.
As funções que alteram dados devolvem uma tupla (sucesso, mensagem) para
que o menu decida o que mostrar ao usuário.

As listas globais ficam no módulo persistencia e são sempre acessadas como
persistencia.tarefas / persistencia.tarefas_arquivadas, para enxergar
sempre a versão mais recente delas.
"""

from datetime import datetime, timedelta

import persistencia
from config import DIAS_PARA_ARQUIVAR, debug
from validacao import PRIORIDADES, validar_titulo, validar_prioridade, validar_origem


# ==========================================================
# FUNÇÕES AUXILIARES
# ==========================================================

def buscar_tarefa(id_tarefa):
    """
    Procura uma tarefa ativa pelo ID.

    Parâmetros:
        id_tarefa (int): ID da tarefa procurada.

    Retorno:
        dict | None: a tarefa encontrada, ou None se não existir.
    """
    debug("buscar_tarefa")
    for tarefa in persistencia.tarefas:
        if tarefa.get("id") == id_tarefa:
            return tarefa
    return None


def tarefa_em_execucao():
    """
    Procura a tarefa que está com status "Fazendo" (só pode haver uma).

    Parâmetros: nenhum

    Retorno:
        dict | None: a tarefa em execução, ou None se não houver.
    """
    debug("tarefa_em_execucao")
    for tarefa in persistencia.tarefas:
        if tarefa.get("status") == "Fazendo":
            return tarefa
    return None


def formatar_data(data):
    """
    Formata uma data para exibição no padrão brasileiro.

    Parâmetros:
        data (datetime | None): data a ser formatada.

    Retorno:
        str: data no formato dd/mm/aaaa hh:mm, ou "-" se não houver data.
    """
    debug("formatar_data")
    if not isinstance(data, datetime):
        return "-"
    return data.strftime("%d/%m/%Y %H:%M")


def formatar_duracao(duracao):
    """
    Transforma um intervalo de tempo em texto legível (ex.: "2 dia(s), 3h 15min").

    Parâmetros:
        duracao (timedelta): intervalo de tempo.

    Retorno:
        str: duração formatada.
    """
    debug("formatar_duracao")
    total_minutos = max(int(duracao.total_seconds() // 60), 0)
    dias, resto = divmod(total_minutos, 60 * 24)
    horas, minutos = divmod(resto, 60)
    if dias:
        return f"{dias} dia(s), {horas}h {minutos:02d}min"
    if horas:
        return f"{horas}h {minutos:02d}min"
    return f"{minutos} min"


def calcular_tempo_execucao(tarefa):
    """
    Calcula quanto tempo a tarefa levou, da criação até a conclusão.

    Parâmetros:
        tarefa (dict): tarefa concluída.

    Retorno:
        timedelta | None: tempo de execução, ou None se faltar alguma data.
    """
    debug("calcular_tempo_execucao")
    inicio = tarefa.get("data_criacao")
    fim = tarefa.get("data_conclusao")
    if isinstance(inicio, datetime) and isinstance(fim, datetime):
        return fim - inicio
    return None


def exibir_tarefa(tarefa):
    """
    Mostra na tela todas as informações de uma tarefa.

    Parâmetros:
        tarefa (dict): tarefa a ser exibida.

    Retorno: nenhum
    """
    debug("exibir_tarefa")
    print(f"ID: {tarefa.get('id')}  |  {tarefa.get('titulo')}")
    print(f"  Descrição:         {tarefa.get('descricao') or '-'}")
    print(f"  Prioridade:        {tarefa.get('prioridade')}")
    print(f"  Status:            {tarefa.get('status')}")
    print(f"  Origem:            {tarefa.get('origem')}")
    print(f"  Criada em:         {formatar_data(tarefa.get('data_criacao'))}")
    if tarefa.get("data_inicio"):
        print(f"  Iniciada em:       {formatar_data(tarefa.get('data_inicio'))}")
    if tarefa.get("data_conclusao"):
        print(f"  Concluída em:      {formatar_data(tarefa.get('data_conclusao'))}")
        tempo = calcular_tempo_execucao(tarefa)
        if tempo is not None:
            print(f"  Tempo de execução: {formatar_duracao(tempo)}")
    print("-" * 50)


# ==========================================================
# CICLO DE VIDA DA TAREFA
# ==========================================================

def criar_tarefa(titulo, descricao, prioridade, origem):
    """
    1. Criação: valida os dados e adiciona uma nova tarefa à lista,
    sempre com status inicial "Pendente".

    Parâmetros:
        titulo (str): o que deve ser feito (obrigatório).
        descricao (str): detalhes da tarefa (opcional).
        prioridade (str): Urgente, Alta, Média ou Baixa (obrigatório).
        origem (str): E-mail, Telefone ou Chamado do Sistema (obrigatório).

    Retorno:
        tuple[bool, str]: (sucesso, mensagem para o usuário).
    """
    debug("criar_tarefa")
    if not validar_titulo(titulo):
        return False, "O título é obrigatório."

    prioridade_valida = validar_prioridade(prioridade)
    if prioridade_valida is None:
        return False, f"Prioridade inválida. Opções: {', '.join(PRIORIDADES)}."

    origem_valida = validar_origem(origem)
    if origem_valida is None:
        return False, "Origem inválida. Opções: E-mail, Telefone, Chamado do Sistema."

    nova_tarefa = {
        "id": persistencia.gerar_id(),
        "titulo": titulo.strip(),
        "descricao": (descricao or "").strip(),
        "prioridade": prioridade_valida,
        "status": "Pendente",
        "origem": origem_valida,
        "data_criacao": datetime.now(),
        "data_inicio": None,
        "data_conclusao": None,
    }
    persistencia.tarefas.append(nova_tarefa)
    persistencia.salvar_tarefas()
    return True, f"Tarefa criada com ID {nova_tarefa['id']}."


def pegar_proxima_tarefa():
    """
    2. Verificação de urgência: escolhe a próxima tarefa a ser feita.

    Procura a primeira tarefa "Pendente" de prioridade Urgente; se não houver,
    passa para Alta, depois Média e por fim Baixa. A tarefa escolhida passa
    para o status "Fazendo". Como só uma tarefa pode estar em execução por
    vez, se já houver uma "Fazendo", ela é mostrada no lugar.

    Parâmetros: nenhum

    Retorno:
        tuple[bool, str, dict | None]: (sucesso, mensagem, tarefa escolhida).
    """
    debug("pegar_proxima_tarefa")
    atual = tarefa_em_execucao()
    if atual is not None:
        return (False,
                "Já existe uma tarefa em execução. Conclua-a antes de pegar outra.",
                atual)

    for prioridade in PRIORIDADES:
        for tarefa in persistencia.tarefas:
            if tarefa.get("status") == "Pendente" and tarefa.get("prioridade") == prioridade:
                tarefa["status"] = "Fazendo"
                tarefa["data_inicio"] = datetime.now()
                persistencia.salvar_tarefas()
                return True, f"Tarefa de prioridade {prioridade} iniciada.", tarefa

    return False, "Não há tarefas pendentes.", None


def atualizar_prioridade(id_tarefa, nova_prioridade):
    """
    3. Atualização de prioridade: troca a prioridade de uma tarefa,
    validando se a nova prioridade existe no sistema.

    Parâmetros:
        id_tarefa (int): ID da tarefa.
        nova_prioridade (str): nova prioridade desejada.

    Retorno:
        tuple[bool, str]: (sucesso, mensagem para o usuário).
    """
    debug("atualizar_prioridade")
    tarefa = buscar_tarefa(id_tarefa)
    if tarefa is None:
        return False, "Tarefa não encontrada."
    if tarefa.get("status") == "Concluída":
        return False, "Não é possível mudar a prioridade de uma tarefa concluída."

    prioridade_valida = validar_prioridade(nova_prioridade)
    if prioridade_valida is None:
        return False, f"Prioridade inválida. Opções: {', '.join(PRIORIDADES)}."

    prioridade_antiga = tarefa["prioridade"]
    tarefa["prioridade"] = prioridade_valida
    persistencia.salvar_tarefas()
    return True, f"Prioridade alterada de {prioridade_antiga} para {prioridade_valida}."


def concluir_tarefa(id_tarefa):
    """
    4. Conclusão: marca a tarefa como "Concluída" e registra a data e hora
    de conclusão (usada depois para calcular o tempo de execução).

    Parâmetros:
        id_tarefa (int): ID da tarefa.

    Retorno:
        tuple[bool, str]: (sucesso, mensagem para o usuário).
    """
    debug("concluir_tarefa")
    tarefa = buscar_tarefa(id_tarefa)
    if tarefa is None:
        return False, "Tarefa não encontrada."
    if tarefa.get("status") == "Concluída":
        return False, "Essa tarefa já está concluída."

    tarefa["status"] = "Concluída"
    tarefa["data_conclusao"] = datetime.now()
    persistencia.salvar_tarefas()
    tempo = formatar_duracao(calcular_tempo_execucao(tarefa))
    return True, f"Tarefa {id_tarefa} concluída. Tempo de execução: {tempo}."


def arquivar_tarefas_antigas(dias=DIAS_PARA_ARQUIVAR):
    """
    5. Arquivamento: tarefas concluídas há mais de `dias` dias recebem o
    status "Arquivado" e são registradas em tarefas_arquivadas.json antes
    de saírem da lista ativa.

    Parâmetros:
        dias (int): idade mínima, em dias, da conclusão (padrão: 7).

    Retorno:
        int: quantidade de tarefas arquivadas.
    """
    debug("arquivar_tarefas_antigas")
    limite = datetime.now() - timedelta(days=dias)
    para_arquivar = [
        t for t in persistencia.tarefas
        if t.get("status") == "Concluída"
        and isinstance(t.get("data_conclusao"), datetime)
        and t["data_conclusao"] < limite
    ]

    quantidade = 0
    for tarefa in para_arquivar:
        tarefa["status"] = "Arquivado"
        if persistencia.mover_para_historico(tarefa):
            quantidade += 1
        else:
            tarefa["status"] = "Concluída"
    return quantidade


def excluir_tarefa(id_tarefa):
    """
    6. Exclusão lógica: a tarefa não é apagada. Seu status muda para
    "Excluída" e ela é guardada no histórico (tarefas_arquivadas.json).

    Parâmetros:
        id_tarefa (int): ID da tarefa.

    Retorno:
        tuple[bool, str]: (sucesso, mensagem para o usuário).
    """
    debug("excluir_tarefa")
    tarefa = buscar_tarefa(id_tarefa)
    if tarefa is None:
        return False, "Tarefa não encontrada."

    status_anterior = tarefa["status"]
    tarefa["status"] = "Excluída"
    if not persistencia.mover_para_historico(tarefa):
        tarefa["status"] = status_anterior
        return False, "Não foi possível registrar a exclusão. Nada foi alterado."
    return True, f"Tarefa {id_tarefa} excluída (guardada no histórico)."


# ==========================================================
# RELATÓRIOS
# ==========================================================

def relatorio_tarefas():
    """
    7. Relatório: mostra todas as informações das tarefas ativas.
    Para as concluídas, mostra também o tempo de execução.

    Parâmetros: nenhum
    Retorno: nenhum
    """
    debug("relatorio_tarefas")
    if not persistencia.tarefas:
        print("Nenhuma tarefa ativa.")
        return

    print("\n================ RELATÓRIO DE TAREFAS ================")
    for tarefa in persistencia.tarefas:
        exibir_tarefa(tarefa)
    print(f"Total: {len(persistencia.tarefas)} tarefa(s).")


def relatorio_arquivados():
    """
    8. Relatório de arquivados: mostra as tarefas com status "Arquivado".
    Tarefas excluídas ficam no histórico, mas não aparecem aqui.

    Parâmetros: nenhum
    Retorno: nenhum
    """
    debug("relatorio_arquivados")
    arquivadas = [t for t in persistencia.tarefas_arquivadas
                  if t.get("status") == "Arquivado"]
    if not arquivadas:
        print("Nenhuma tarefa arquivada.")
        return

    print("\n=============== RELATÓRIO DE ARQUIVADAS ===============")
    for tarefa in arquivadas:
        exibir_tarefa(tarefa)
    print(f"Total: {len(arquivadas)} tarefa(s) arquivada(s).")


def listar_resumo():
    """
    Mostra uma lista curta (ID, status, prioridade e título) das tarefas
    ativas, para ajudar o usuário a escolher um ID.

    Parâmetros: nenhum
    Retorno:
        bool: True se havia tarefas para mostrar.
    """
    debug("listar_resumo")
    if not persistencia.tarefas:
        print("Nenhuma tarefa ativa.")
        return False
    for tarefa in persistencia.tarefas:
        print(f"  [{tarefa['id']}] {tarefa['status']:<9} | "
              f"{tarefa['prioridade']:<7} | {tarefa['titulo']}")
    return True
