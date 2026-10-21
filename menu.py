"""
Menu principal e funções de interação com o usuário.

Cada opção do menu chama uma função própria (modularização). As entradas
são sempre validadas antes de chegar às regras de negócio.
"""

import persistencia
import tarefas
from config import debug
from validacao import (
    PRIORIDADES, ORIGENS, converter_inteiro, validar_titulo,
    validar_prioridade, validar_origem, validar_opcao_menu,
)


# ==========================================================
# FUNÇÕES DE ENTRADA DE DADOS
# ==========================================================

def mostrar_opcoes(opcoes):
    """
    Monta o texto numerado com as opções aceitas por um campo.

    Parâmetros:
        opcoes (list[str]): opções válidas.

    Retorno:
        str: texto no formato "1-Urgente, 2-Alta, ...".
    """
    debug("mostrar_opcoes")
    return ", ".join(f"{i}-{opcao}" for i, opcao in enumerate(opcoes, start=1))


def ler_titulo():
    """
    Pede o título da tarefa até o usuário digitar um valor não vazio.

    Parâmetros: nenhum
    Retorno:
        str: título informado.
    """
    debug("ler_titulo")
    while True:
        titulo = input("Título (obrigatório): ").strip()
        if validar_titulo(titulo):
            return titulo
        print("O título não pode ficar em branco.")


def ler_prioridade(rotulo="Prioridade"):
    """
    Pede uma prioridade, mostrando as opções, até receber uma válida.

    Parâmetros:
        rotulo (str): texto exibido antes das opções.

    Retorno:
        str: prioridade na forma oficial.
    """
    debug("ler_prioridade")
    while True:
        entrada = input(f"{rotulo} ({mostrar_opcoes(PRIORIDADES)}): ")
        prioridade = validar_prioridade(entrada)
        if prioridade is not None:
            return prioridade
        print("Prioridade inválida. Digite o número ou o nome de uma das opções.")


def ler_origem():
    """
    Pede a origem da tarefa, mostrando as opções, até receber uma válida.

    Parâmetros: nenhum
    Retorno:
        str: origem na forma oficial.
    """
    debug("ler_origem")
    while True:
        entrada = input(f"Origem ({mostrar_opcoes(ORIGENS)}): ")
        origem = validar_origem(entrada)
        if origem is not None:
            return origem
        print("Origem inválida. Digite o número ou o nome de uma das opções.")


def ler_id():
    """
    Mostra as tarefas ativas e pede o ID de uma delas. Se o usuário digitar
    algo que não é número, mostra uma mensagem amigável em vez de quebrar.

    Parâmetros: nenhum
    Retorno:
        int | None: ID digitado, ou None se não houver tarefas ou o valor for inválido.
    """
    debug("ler_id")
    if not tarefas.listar_resumo():
        return None
    id_tarefa = converter_inteiro(input("ID da tarefa: "))
    if id_tarefa is None:
        print("ID inválido: digite apenas números.")
    return id_tarefa


# ==========================================================
# AÇÕES DO MENU (uma função por opção)
# ==========================================================

def opcao_criar():
    """
    Coleta os dados de uma nova tarefa e a cadastra.

    Parâmetros: nenhum
    Retorno: nenhum
    """
    debug("opcao_criar")
    titulo = ler_titulo()
    descricao = input("Descrição (opcional, Enter para pular): ").strip()
    prioridade = ler_prioridade()
    origem = ler_origem()
    _, mensagem = tarefas.criar_tarefa(titulo, descricao, prioridade, origem)
    print(mensagem)


def opcao_pegar_proxima():
    """
    Pega a próxima tarefa por ordem de urgência e a coloca em execução.

    Parâmetros: nenhum
    Retorno: nenhum
    """
    debug("opcao_pegar_proxima")
    _, mensagem, tarefa = tarefas.pegar_proxima_tarefa()
    print(mensagem)
    if tarefa is not None:
        tarefas.exibir_tarefa(tarefa)


def opcao_atualizar_prioridade():
    """
    Altera a prioridade de uma tarefa escolhida pelo usuário.

    Parâmetros: nenhum
    Retorno: nenhum
    """
    debug("opcao_atualizar_prioridade")
    id_tarefa = ler_id()
    if id_tarefa is None:
        return
    nova = ler_prioridade("Nova prioridade")
    _, mensagem = tarefas.atualizar_prioridade(id_tarefa, nova)
    print(mensagem)


def opcao_concluir():
    """
    Conclui uma tarefa escolhida pelo usuário.

    Parâmetros: nenhum
    Retorno: nenhum
    """
    debug("opcao_concluir")
    id_tarefa = ler_id()
    if id_tarefa is None:
        return
    _, mensagem = tarefas.concluir_tarefa(id_tarefa)
    print(mensagem)


def opcao_arquivar():
    """
    Arquiva manualmente as tarefas concluídas há mais de uma semana
    (isso também acontece automaticamente ao iniciar o programa).

    Parâmetros: nenhum
    Retorno: nenhum
    """
    debug("opcao_arquivar")
    quantidade = tarefas.arquivar_tarefas_antigas()
    print(f"{quantidade} tarefa(s) arquivada(s).")


def opcao_excluir():
    """
    Exclui logicamente uma tarefa escolhida pelo usuário, após confirmação.

    Parâmetros: nenhum
    Retorno: nenhum
    """
    debug("opcao_excluir")
    id_tarefa = ler_id()
    if id_tarefa is None:
        return
    if tarefas.buscar_tarefa(id_tarefa) is None:
        print("Tarefa não encontrada.")
        return
    confirmacao = input(f"Confirma a exclusão da tarefa {id_tarefa}? (s/n): ")
    if confirmacao.strip().lower() not in ("s", "sim"):
        print("Exclusão cancelada.")
        return
    _, mensagem = tarefas.excluir_tarefa(id_tarefa)
    print(mensagem)


def opcao_sair():
    """
    Salva os dados nos arquivos JSON e só então encerra o programa com exit().

    Parâmetros: nenhum
    Retorno: nenhum (o programa é encerrado)
    """
    debug("opcao_sair")
    if persistencia.salvar_dados():
        print("Dados salvos. Até logo!")
    else:
        print("Atenção: houve erro ao salvar os dados.")
    exit()


# ==========================================================
# MENU PRINCIPAL
# ==========================================================

# Opções do menu: tecla -> (texto exibido, função executada)
OPCOES_MENU = {
    "1": ("Criar tarefa", opcao_criar),
    "2": ("Pegar próxima tarefa (por urgência)", opcao_pegar_proxima),
    "3": ("Atualizar prioridade", opcao_atualizar_prioridade),
    "4": ("Concluir tarefa", opcao_concluir),
    "5": ("Arquivar tarefas concluídas há mais de 7 dias", opcao_arquivar),
    "6": ("Excluir tarefa", opcao_excluir),
    "7": ("Relatório de tarefas", tarefas.relatorio_tarefas),
    "8": ("Relatório de arquivadas", tarefas.relatorio_arquivados),
    "0": ("Sair", opcao_sair),
}


def exibir_menu():
    """
    Mostra todas as opções disponíveis no menu principal.

    Parâmetros: nenhum
    Retorno: nenhum
    """
    debug("exibir_menu")
    print("\n============= GERENCIADOR DE TAREFAS =============")
    for tecla, (texto, _) in OPCOES_MENU.items():
        print(f"  {tecla}. {texto}")
    print("==================================================")


def menu():
    """
    Laço principal: mostra o menu, valida a opção escolhida e executa a
    função correspondente, até o usuário escolher "Sair".

    Parâmetros: nenhum
    Retorno: nenhum
    """
    debug("menu")
    while True:
        exibir_menu()
        opcao = input("Escolha uma opção: ").strip()
        if not validar_opcao_menu(opcao, OPCOES_MENU):
            print("Opção inválida. Escolha um dos números do menu.")
            continue
        _, acao = OPCOES_MENU[opcao]
        acao()
