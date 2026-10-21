"""
Funções de validação de dados (1ª linha de defesa).

Toda entrada digitada pelo usuário passa por uma destas funções antes de
ser usada pelo sistema. Elas aceitam variações de escrita (maiúsculas,
acentos, número da opção) e devolvem sempre a forma "oficial" do valor.
"""

import unicodedata

from config import debug

# ==========================================================
# CONSTANTES (valores aceitos pelo sistema)
# ==========================================================

# A ordem da lista define a importância: o primeiro item é a prioridade máxima.
PRIORIDADES = ["Urgente", "Alta", "Média", "Baixa"]

ORIGENS = ["E-mail", "Telefone", "Chamado do Sistema"]

STATUS = ["Pendente", "Fazendo", "Concluída", "Arquivado", "Excluída"]

# Formas alternativas aceitas para a origem (já sem acento e em minúsculas).
SINONIMOS_ORIGEM = {
    "email": "E-mail",
    "chamado": "Chamado do Sistema",
    "sistema": "Chamado do Sistema",
}


# ==========================================================
# FUNÇÕES
# ==========================================================

def normalizar_texto(texto):
    """
    Deixa um texto em minúsculas, sem acentos e sem espaços nas pontas,
    para que "Média", "media" e " MÉDIA " sejam tratados como iguais.

    Parâmetros:
        texto (str): texto digitado pelo usuário.

    Retorno:
        str: texto normalizado.
    """
    debug("normalizar_texto")
    texto_local = (texto or "").strip().lower()
    decomposto = unicodedata.normalize("NFD", texto_local)
    return "".join(c for c in decomposto if unicodedata.category(c) != "Mn")


def converter_inteiro(texto):
    """
    Converte um texto em número inteiro sem deixar o programa quebrar
    (2ª linha de defesa: tratamento de exceção).

    Parâmetros:
        texto (str): texto que deveria conter um número inteiro.

    Retorno:
        int | None: o número convertido, ou None se o texto não for um inteiro.
    """
    debug("converter_inteiro")
    try:
        return int(str(texto).strip())
    except (ValueError, TypeError):
        return None


def escolher_da_lista(entrada, opcoes, sinonimos=None):
    """
    Identifica qual item de uma lista de opções o usuário escolheu.
    Aceita o número da opção (começando em 1), o nome ou um sinônimo.

    Parâmetros:
        entrada (str): o que o usuário digitou.
        opcoes (list[str]): opções válidas, na forma oficial.
        sinonimos (dict[str, str] | None): formas alternativas aceitas.

    Retorno:
        str | None: a opção na forma oficial, ou None se for inválida.
    """
    debug("escolher_da_lista")
    numero = converter_inteiro(entrada)
    if numero is not None:
        if 1 <= numero <= len(opcoes):
            return opcoes[numero - 1]
        return None

    chave = normalizar_texto(entrada)
    for opcao in opcoes:
        if normalizar_texto(opcao) == chave:
            return opcao
    if sinonimos and chave in sinonimos:
        return sinonimos[chave]
    return None


def validar_prioridade(entrada):
    """
    Valida a prioridade informada pelo usuário.

    Parâmetros:
        entrada (str): prioridade digitada (nome ou número da opção).

    Retorno:
        str | None: prioridade oficial ("Urgente", "Alta", "Média" ou "Baixa"),
        ou None se for inválida.
    """
    debug("validar_prioridade")
    return escolher_da_lista(entrada, PRIORIDADES)


def validar_origem(entrada):
    """
    Valida a origem da tarefa informada pelo usuário.

    Parâmetros:
        entrada (str): origem digitada (nome, sinônimo ou número da opção).

    Retorno:
        str | None: origem oficial ("E-mail", "Telefone" ou "Chamado do Sistema"),
        ou None se for inválida.
    """
    debug("validar_origem")
    return escolher_da_lista(entrada, ORIGENS, SINONIMOS_ORIGEM)


def validar_titulo(titulo):
    """
    Verifica se o título foi preenchido (campo obrigatório).

    Parâmetros:
        titulo (str): título digitado.

    Retorno:
        bool: True se o título tiver ao menos um caractere visível.
    """
    debug("validar_titulo")
    return bool((titulo or "").strip())


def validar_opcao_menu(opcao, opcoes_validas):
    """
    Verifica se a opção digitada no menu existe antes de executá-la.

    Parâmetros:
        opcao (str): opção digitada.
        opcoes_validas (dict | list): opções existentes no menu.

    Retorno:
        bool: True se a opção existir.
    """
    debug("validar_opcao_menu")
    return (opcao or "").strip() in opcoes_validas
