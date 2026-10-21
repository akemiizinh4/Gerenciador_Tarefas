# Gerenciador de Tarefas

Sistema de linha de comando em Python para organizar tarefas por **prioridade** e **status**, com dados salvos em arquivos JSON.

Projeto desenvolvido como Atividade Final da disciplina **Técnicas de Desenvolvimento de Algoritmos**, na Universidade Braz Cubas (2025), sob orientação do Prof. Gilberto Aparecido da Silva.

## Funcionalidades

- **Criar tarefa** com título, descrição, prioridade e origem. O sistema mostra as opções válidas de cada campo.
- **Pegar a próxima tarefa por urgência.** O sistema escolhe a primeira tarefa pendente de maior prioridade (Urgente → Alta → Média → Baixa) e a coloca como "Fazendo". Só uma tarefa pode estar em execução por vez.
- **Atualizar a prioridade** de uma tarefa, com validação.
- **Concluir tarefa**, registrando a data e a hora de conclusão e calculando o tempo de execução.
- **Arquivar automaticamente** as tarefas concluídas há mais de 7 dias (ao iniciar o programa ou pelo menu).
- **Excluir tarefa** de forma lógica: nada é apagado, a tarefa vai para o histórico com status "Excluída".
- **Relatórios** de tarefas ativas e de tarefas arquivadas.

### Ciclo de vida de uma tarefa

```
Pendente ──► Fazendo ──► Concluída ──► Arquivado (após 7 dias)
    │           │            │
    └───────────┴────────────┴──► Excluída (exclusão lógica)
```

### Campos de uma tarefa

| Campo            | Obrigatório | Valores                                   |
|------------------|:-----------:|-------------------------------------------|
| `titulo`         | sim         | texto livre                               |
| `descricao`      | não         | texto livre                               |
| `prioridade`     | sim         | Urgente, Alta, Média, Baixa               |
| `origem`         | sim         | E-mail, Telefone, Chamado do Sistema      |
| `status`         | automático  | Pendente, Fazendo, Concluída, Arquivado, Excluída |
| `data_criacao`   | automático  | data e hora da criação                    |
| `data_inicio`    | automático  | quando a tarefa passou para "Fazendo"     |
| `data_conclusao` | automático  | preenchida só para tarefas concluídas     |

## Como executar

É preciso ter o **Python 3.8 ou superior**. O projeto não usa bibliotecas externas.

```bash
python main.py
```

Na primeira execução, os arquivos `tarefas.json` e `tarefas_arquivadas.json` são criados automaticamente na pasta do programa.

### Modo de depuração

Para os testes, cada função imprime `[debug] Executando a função X` ao ser chamada. Para usar o sistema sem essas mensagens, mude em `config.py`:

```python
DEBUG = False
```

## Estrutura do projeto

| Arquivo           | Responsabilidade                                                  |
|-------------------|-------------------------------------------------------------------|
| `main.py`         | Ponto de entrada: prepara os arquivos, carrega os dados e abre o menu |
| `menu.py`         | Menu principal e leitura das entradas do usuário                  |
| `tarefas.py`      | Regras de negócio do ciclo de vida e relatórios                   |
| `persistencia.py` | Variáveis globais e leitura/gravação dos arquivos JSON           |
| `validacao.py`    | Funções de validação das entradas                                 |
| `config.py`       | Caminhos dos arquivos, prazo de arquivamento e modo debug         |

### Decisões de implementação

- **Duas linhas de defesa:** as funções de `validacao.py` checam a lógica dos dados, e o `try/except` trata erros técnicos (por exemplo, letras digitadas no lugar de um ID). Assim o programa nunca para de forma abrupta.
- **Datas:** em memória, as datas são objetos `datetime`, para permitir o cálculo do tempo de execução. No JSON, são gravadas como texto ISO, porque o JSON não tem tipo de data.
- **Segurança dos dados:** a gravação passa por um arquivo temporário antes de substituir o original. Se um JSON estiver corrompido, ele é renomeado como backup em vez de ser sobrescrito.
- **Saída segura:** ao escolher "Sair", ou ao interromper com Ctrl+C, os dados são salvos antes do `exit()`.


