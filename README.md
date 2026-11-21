# TrabMassakiNotasAlunos

Programa em Python que simula o **módulo de fechamento de notas de uma turma**.

## O que faz

- Pede o **nome do aluno** e funciona em laço (`while`) até o usuário digitar **SAIR** no campo do nome (aceita `SAIR`, `sair`, `Sair`...).
- Para cada aluno, lê **3 notas decimais de 0.0 a 10.0** (aceita ponto ou vírgula; repete a pergunta se o valor for inválido ou estiver fora da faixa).
- Calcula a **média aritmética simples**: `(n1 + n2 + n3) / 3`. Os parênteses garantem que a soma é feita antes da divisão, respeitando a precedência dos operadores.
- Ao encerrar, mostra uma tabela-resumo com as notas e a média de cada aluno.

## Como rodar no VS Code

1. Instale o Python (https://www.python.org) e o VS Code, com a extensão **Python**.
2. Abra a pasta do projeto no VS Code (**File → Open Folder**).
3. Abra o arquivo `fechamento_notas.py` e clique em **Run Python File** (botão ▶ no canto superior direito).
4. Responda no terminal do VS Code. Para encerrar, digite `SAIR` no nome.

Ou, no terminal: `python fechamento_notas.py`

## Exemplo

```
Nome do aluno (ou SAIR para encerrar): Ana
  Nota 1 (0.0 a 10.0): 8
  Nota 2 (0.0 a 10.0): 7,5
  Nota 3 (0.0 a 10.0): 10
  Média de Ana: 8.50
```
