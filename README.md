# TrabMassakiNotasAlunos

Programa em Python que simula o **módulo de fechamento de notas de uma turma**.

## O que faz

- Pede o **nome do aluno** e funciona em laço (`while`) até o usuário digitar **SAIR** no campo do nome (aceita `SAIR`, `sair`, `Sair`...).
- Para cada aluno, lê **3 notas decimais de 0.0 a 10.0** (aceita ponto ou vírgula; repete a pergunta se o valor for inválido ou estiver fora da faixa).
- Calcula a **média aritmética simples**: `(n1 + n2 + n3) / 3`. Os parênteses garantem que a soma é feita antes da divisão, respeitando a precedência dos operadores.
- Informa a **situação**: **Aprovado** se a média for maior ou igual a 6.0, senão **Reprovado**. A nota de corte está na constante `MEDIA_APROVACAO` do arquivo `fechamento_notas.py`, e é só trocar o valor se o professor definir outra.
- Ao encerrar, mostra uma tabela-resumo com as notas, a média e a situação de cada aluno, e quantos foram aprovados e reprovados.

## Como rodar no VS Code

1. Instale o Python (https://www.python.org) e o VS Code, com a extensão **Python**.
2. Abra a pasta do projeto no VS Code (**File → Open Folder**).
3. Abra o arquivo `fechamento_notas.py` e clique em **Run Python File** (botão ▶ no canto superior direito).
4. Responda no terminal do VS Code. Para encerrar, digite `SAIR` no nome.

Ou, no terminal: `python fechamento_notas.py`

## Versão web (Flask)

O arquivo `app.py` é a mesma lógica em um site: formulário com nome e 3 notas, tabela com as médias e botão **Encerrar cadastro (SAIR)**. Digitar SAIR no nome também encerra. Visual futurista (vidro, neon e animações), com média ao vivo enquanto você digita, indicadores no topo e um anel de nota para cada aluno. Cada visitante tem a própria lista.

Para testar no computador: `pip install -r requirements.txt` e depois `python app.py` (abre em http://localhost:5000).

### Colocar no PythonAnywhere

Troque `USUARIO` pelo nome da sua conta do PythonAnywhere.

1. Aba **Consoles** → **Bash** e rode: `git clone https://github.com/GaGoat2267/TrabMassakiNotasAlunos.git`
2. Aba **Web** → **Add a new web app** → Next → **Manual configuration** → escolha o Python mais novo.
3. Em **Code**, preencha **Source code** e **Working directory** com `/home/USUARIO/TrabMassakiNotasAlunos`
4. Clique no link do **WSGI configuration file**, apague tudo e cole:

```python
import sys
sys.path.insert(0, '/home/USUARIO/TrabMassakiNotasAlunos')
from app import app as application
```

5. Salve, volte na aba **Web** e clique em **Reload**. O site fica em `https://USUARIO.pythonanywhere.com`.

Para atualizar depois: no Bash, `cd ~/TrabMassakiNotasAlunos && git pull`, e **Reload** na aba Web.

## Exemplo

```
Nome do aluno (ou SAIR para encerrar): Ana
  Nota 1 (0.0 a 10.0): 8
  Nota 2 (0.0 a 10.0): 7,5
  Nota 3 (0.0 a 10.0): 10
  Média de Ana: 8.50
```
