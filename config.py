"""
Configurações gerais do Gerenciador de Tarefas.

Centraliza os caminhos dos arquivos de dados e a chave de depuração,
para que nenhum outro módulo precise "adivinhar" esses valores.
"""

from pathlib import Path

# ==========================================================
# CONSTANTES DE CONFIGURAÇÃO
# ==========================================================

# Quando True, cada função imprime "Executando a função X" ao ser chamada
# (requisito de rastreamento para testes). Mude para False para uso normal.
DEBUG = True

# Pasta onde ficam o programa e seus arquivos de dados.
PASTA_PROGRAMA = Path(__file__).resolve().parent

ARQUIVO_TAREFAS = PASTA_PROGRAMA / "tarefas.json"
ARQUIVO_ARQUIVADAS = PASTA_PROGRAMA / "tarefas_arquivadas.json"

# Tarefas concluídas há mais desse número de dias são arquivadas.
DIAS_PARA_ARQUIVAR = 7


# ==========================================================
# FUNÇÕES
# ==========================================================

def debug(nome_funcao):
    """
    Imprime uma linha indicando qual função está sendo executada.

    Parâmetros:
        nome_funcao (str): nome da função que está sendo executada.

    Retorno: nenhum
    """
    if DEBUG:
        print(f"[debug] Executando a função {nome_funcao}")
