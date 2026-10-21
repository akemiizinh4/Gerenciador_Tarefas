"""
Ponto de entrada do Gerenciador de Tarefas.

Execute com:  python main.py
"""

import persistencia
import tarefas
from config import debug
from menu import menu


# ==========================================================
# CORPO PRINCIPAL DO PROGRAMA
# ==========================================================

def main():
    """
    Prepara o sistema e inicia o menu:
    1. cria os arquivos JSON caso ainda não existam;
    2. carrega os dados salvos;
    3. arquiva automaticamente as tarefas concluídas há mais de uma semana;
    4. abre o menu principal.

    Se o usuário interromper o programa (Ctrl+C), os dados são salvos
    antes de encerrar.

    Parâmetros: nenhum
    Retorno: nenhum
    """
    debug("main")
    persistencia.garantir_arquivos()
    persistencia.carregar_dados()

    arquivadas = tarefas.arquivar_tarefas_antigas()
    if arquivadas:
        print(f"{arquivadas} tarefa(s) antiga(s) arquivada(s) automaticamente.")

    try:
        menu()
    except (KeyboardInterrupt, EOFError):
        print("\nInterrompido. Salvando os dados antes de sair...")
        persistencia.salvar_dados()
        exit()


if __name__ == "__main__":
    main()
