"""
Estado global do sistema e persistência em arquivos JSON.

Este módulo guarda as variáveis globais (lista de tarefas, histórico de
arquivadas e contador de IDs) e é o único responsável por ler e gravar
os arquivos tarefas.json e tarefas_arquivadas.json.

Em memória, as datas são objetos datetime (permitem calcular tempo de
execução). No arquivo JSON, são gravadas como texto no formato ISO,
porque o JSON não tem um tipo próprio para data e hora.
"""

import json
import os
from datetime import datetime

from config import ARQUIVO_TAREFAS, ARQUIVO_ARQUIVADAS, debug

# ==========================================================
# VARIÁVEIS GLOBAIS
# ==========================================================

# Lista principal: tarefas ativas (Pendente, Fazendo ou Concluída).
tarefas = []

# Histórico acumulado de tarefas arquivadas e excluídas.
tarefas_arquivadas = []

# Contador de controle do sistema: próximo ID a ser usado.
proximo_id = 1

# Campos de cada tarefa que guardam data e hora.
CAMPOS_DE_DATA = ("data_criacao", "data_inicio", "data_conclusao")


# ==========================================================
# FUNÇÕES AUXILIARES DE CONVERSÃO
# ==========================================================

def tarefa_para_json(tarefa):
    """
    Cria uma cópia da tarefa com as datas convertidas para texto ISO,
    pronta para ser gravada no arquivo JSON.

    Parâmetros:
        tarefa (dict): tarefa com datas do tipo datetime.

    Retorno:
        dict: cópia da tarefa com datas em texto.
    """
    debug("tarefa_para_json")
    copia = dict(tarefa)
    for campo in CAMPOS_DE_DATA:
        if isinstance(copia.get(campo), datetime):
            copia[campo] = copia[campo].isoformat(timespec="seconds")
    return copia


def tarefa_do_json(tarefa):
    """
    Converte as datas de uma tarefa lida do JSON (texto) para datetime.
    Datas em formato inválido viram None em vez de quebrar o programa.

    Parâmetros:
        tarefa (dict): tarefa lida do arquivo.

    Retorno:
        dict: a mesma tarefa com as datas no tipo datetime.
    """
    debug("tarefa_do_json")
    for campo in CAMPOS_DE_DATA:
        valor = tarefa.get(campo)
        if isinstance(valor, str):
            try:
                tarefa[campo] = datetime.fromisoformat(valor)
            except ValueError:
                tarefa[campo] = None
        else:
            tarefa.setdefault(campo, None)
    return tarefa


# ==========================================================
# FUNÇÕES DE ARQUIVO
# ==========================================================

def garantir_arquivos():
    """
    Verifica se os arquivos de dados existem e, se não existirem,
    cria cada um com uma lista vazia (item extra do enunciado).

    Parâmetros: nenhum
    Retorno: nenhum
    """
    debug("garantir_arquivos")
    for caminho in (ARQUIVO_TAREFAS, ARQUIVO_ARQUIVADAS):
        if not caminho.exists():
            try:
                caminho.write_text("[]", encoding="utf-8")
            except OSError as erro:
                print(f"Aviso: não foi possível criar {caminho.name}: {erro}")


def ler_arquivo_json(caminho):
    """
    Lê uma lista de tarefas de um arquivo JSON.

    Se o arquivo estiver corrompido, ele é renomeado como backup em vez de
    ser sobrescrito, para que nenhum dado seja perdido sem aviso.

    Parâmetros:
        caminho (Path): arquivo a ser lido.

    Retorno:
        list[dict]: tarefas lidas (lista vazia se não houver dados válidos).
    """
    debug("ler_arquivo_json")
    try:
        with open(caminho, "r", encoding="utf-8") as arquivo:
            conteudo = arquivo.read().strip()
        dados = json.loads(conteudo) if conteudo else []
        if not isinstance(dados, list):
            raise ValueError("o arquivo não contém uma lista")
        return [tarefa_do_json(t) for t in dados if isinstance(t, dict)]
    except FileNotFoundError:
        return []
    except (ValueError, OSError) as erro:
        carimbo = datetime.now().strftime("%Y%m%d-%H%M%S")
        backup = caminho.with_name(f"{caminho.stem}.corrompido-{carimbo}.json")
        try:
            os.replace(caminho, backup)
            print(f"Aviso: {caminho.name} estava inválido ({erro}). "
                  f"Uma cópia foi guardada em {backup.name}.")
        except OSError:
            print(f"Aviso: {caminho.name} estava inválido ({erro}).")
        return []


def gravar_arquivo_json(caminho, lista):
    """
    Grava uma lista de tarefas em um arquivo JSON de forma segura:
    escreve primeiro em um arquivo temporário e só depois substitui o
    original, evitando arquivo pela metade se algo der errado.

    Parâmetros:
        caminho (Path): arquivo de destino.
        lista (list[dict]): tarefas a gravar.

    Retorno:
        bool: True se a gravação deu certo.
    """
    debug("gravar_arquivo_json")
    temporario = caminho.with_suffix(".tmp")
    try:
        with open(temporario, "w", encoding="utf-8") as arquivo:
            json.dump([tarefa_para_json(t) for t in lista], arquivo,
                      ensure_ascii=False, indent=4)
        os.replace(temporario, caminho)
        return True
    except OSError as erro:
        print(f"Erro ao salvar {caminho.name}: {erro}")
        return False


def carregar_dados():
    """
    Lê os dois arquivos JSON e carrega seu conteúdo nas variáveis globais.
    Também recalcula o próximo ID a partir do maior ID já usado.

    Parâmetros: nenhum
    Retorno: nenhum
    """
    debug("carregar_dados")
    global tarefas, tarefas_arquivadas, proximo_id

    tarefas = ler_arquivo_json(ARQUIVO_TAREFAS)
    tarefas_arquivadas = ler_arquivo_json(ARQUIVO_ARQUIVADAS)

    ids_usados = [t.get("id", 0) for t in tarefas + tarefas_arquivadas
                  if isinstance(t.get("id"), int)]
    proximo_id = max(ids_usados, default=0) + 1

    print(f"Dados carregados: {len(tarefas)} tarefa(s) ativa(s), "
          f"{len(tarefas_arquivadas)} no histórico.")


def salvar_tarefas():
    """
    Grava a lista global de tarefas ativas em tarefas.json.

    Parâmetros: nenhum
    Retorno:
        bool: True se a gravação deu certo.
    """
    debug("salvar_tarefas")
    return gravar_arquivo_json(ARQUIVO_TAREFAS, tarefas)


def salvar_arquivadas():
    """
    Grava o histórico global de tarefas em tarefas_arquivadas.json.

    Parâmetros: nenhum
    Retorno:
        bool: True se a gravação deu certo.
    """
    debug("salvar_arquivadas")
    return gravar_arquivo_json(ARQUIVO_ARQUIVADAS, tarefas_arquivadas)


def salvar_dados():
    """
    Grava os dois arquivos JSON (tarefas ativas e histórico).

    Parâmetros: nenhum
    Retorno:
        bool: True se os dois arquivos foram gravados.
    """
    debug("salvar_dados")
    ok_tarefas = salvar_tarefas()
    ok_arquivadas = salvar_arquivadas()
    return ok_tarefas and ok_arquivadas


# ==========================================================
# FUNÇÕES QUE ALTERAM O ESTADO GLOBAL
# ==========================================================

def gerar_id():
    """
    Devolve um ID numérico único para uma nova tarefa e avança o contador.

    Parâmetros: nenhum
    Retorno:
        int: o ID reservado para a nova tarefa.
    """
    debug("gerar_id")
    global proximo_id
    novo_id = proximo_id
    proximo_id += 1
    return novo_id


def mover_para_historico(tarefa):
    """
    Registra a tarefa em tarefas_arquivadas.json e só depois a retira da
    lista de tarefas ativas, como pede o enunciado (nada é apagado).

    Parâmetros:
        tarefa (dict): tarefa já com status "Arquivado" ou "Excluída".

    Retorno:
        bool: True se a tarefa foi movida com sucesso.
    """
    debug("mover_para_historico")
    global tarefas, tarefas_arquivadas

    tarefas_arquivadas.append(tarefa)
    if not salvar_arquivadas():
        # Não conseguiu registrar no histórico: desfaz para não perder a tarefa.
        tarefas_arquivadas.remove(tarefa)
        return False

    tarefas = [t for t in tarefas if t is not tarefa]
    salvar_tarefas()
    return True
