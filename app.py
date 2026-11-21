"""Versão web do fechamento de notas (Flask).

Mesmas regras do programa de terminal (fechamento_notas.py):
- o nome SAIR (qualquer combinação de maiúsculas/minúsculas) encerra o cadastro;
- 3 notas decimais de 0.0 a 10.0 por aluno;
- média aritmética simples (n1 + n2 + n3) / 3.
Cada visitante tem a própria lista (guardada no cookie de sessão).
"""
import os
import secrets

from flask import Flask, redirect, render_template_string, request, session, url_for

from fechamento_notas import MEDIA_APROVACAO, NOTA_MAXIMA, NOTA_MINIMA, QTD_NOTAS, calcular_media, situacao

BASE = os.path.dirname(os.path.abspath(__file__))
MAX_ALUNOS = 200  # limite para o cookie de sessão não crescer sem fim

app = Flask(__name__)


def carregar_chave():
    """Chave que assina o cookie: variável SECRET_KEY ou arquivo secret.key (criado na 1ª vez)."""
    if os.environ.get("SECRET_KEY"):
        return os.environ["SECRET_KEY"]
    caminho = os.path.join(BASE, "secret.key")
    if not os.path.exists(caminho):
        with open(caminho, "w") as f:
            f.write(secrets.token_hex(32))
    with open(caminho) as f:
        return f.read().strip()


app.secret_key = carregar_chave()
app.config.update(SESSION_COOKIE_HTTPONLY=True, SESSION_COOKIE_SAMESITE="Lax")


def ler_nota(texto):
    """Converte o texto em nota (aceita vírgula). Devolve (nota, erro)."""
    try:
        nota = float((texto or "").strip().replace(",", "."))
    except ValueError:
        return None, "valor inválido"
    if not (NOTA_MINIMA <= nota <= NOTA_MAXIMA):
        return None, f"deve estar entre {NOTA_MINIMA} e {NOTA_MAXIMA}"
    return nota, None


PAGINA = """<!doctype html>
<html lang="pt-br"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>Fechamento de notas</title>
<style>
:root{--azul:#0131CD;--lima:#B9FC01;--tinta:#0B1440;--mudo:#5A6592;--linha:#D9E0F5;--fundo:#F1F4FD}
*{box-sizing:border-box}body{margin:0;font-family:system-ui,Segoe UI,Arial,sans-serif;background:var(--fundo);color:var(--tinta)}
header{background:var(--azul);color:#fff;padding:22px 16px}header div,main{max-width:860px;margin:0 auto}
header h1{margin:0;font-size:1.5rem}header p{margin:4px 0 0;color:#DCE5FF}
header b{background:var(--lima);color:var(--azul);border-radius:6px;padding:1px 8px;margin-right:8px}
main{padding:20px 16px 40px}
.card{background:#fff;border:1px solid var(--linha);border-radius:14px;padding:18px;margin-bottom:18px;box-shadow:0 2px 10px rgba(1,49,205,.06)}
h2{margin:0 0 12px;font-size:1.1rem}
form.novo{display:grid;grid-template-columns:2fr 1fr 1fr 1fr;gap:12px;align-items:end}
label{display:grid;gap:5px;font-size:.85rem;color:var(--mudo);font-weight:600}
input{font:inherit;padding:10px;border:1px solid #C9D3F0;border-radius:9px;color:var(--tinta);width:100%}
input:focus{outline:0;border-color:var(--azul);box-shadow:0 0 0 3px rgba(1,49,205,.15)}
.acoes{grid-column:1/-1;display:flex;gap:10px;flex-wrap:wrap}
button{font:inherit;font-weight:700;border-radius:9px;padding:10px 18px;cursor:pointer;border:1px solid #9ED300;background:var(--lima);color:var(--tinta)}
button.sec{background:#fff;border-color:#C9D3F0}button:hover{border-color:var(--azul)}
.erro{background:#FDE6E9;border:1px solid #F2B5BC;color:#9B1C2B;border-radius:9px;padding:10px 12px;margin-bottom:14px}
.ok{background:#F6FFD0;border:1px solid #B9FC01;color:#3F4F00;border-radius:9px;padding:10px 12px;margin-bottom:14px}
table{width:100%;border-collapse:collapse}th,td{padding:10px 8px;border-bottom:1px solid #E6EBFA;text-align:right}
th:first-child,td:first-child{text-align:left}th{font-size:.78rem;text-transform:uppercase;color:var(--mudo);letter-spacing:.04em}
td.media{font-weight:800;color:var(--azul)}
.sit{display:inline-block;border-radius:999px;padding:2px 10px;font-size:.8rem;font-weight:700}
.sit.ap{background:#E4EBFF;color:var(--azul)}.sit.rp{background:#FDE6E9;color:#9B1C2B}.vazio{color:var(--mudo)}
@media(max-width:640px){form.novo{grid-template-columns:1fr 1fr}form.novo label:first-child{grid-column:1/-1}}
</style></head><body>
<header><div><h1><b>Notas</b>Fechamento de notas da turma</h1>
<p>Cadastre o aluno e as 3 notas. Para encerrar, digite SAIR no nome.</p></div></header>
<main>
{% if encerrado %}
  <div class="ok">Cadastro encerrado. Veja o resumo abaixo.</div>
{% else %}
  <section class="card"><h2>Novo aluno</h2>
  {% if erros %}<div class="erro">{% for e in erros %}{{ e }}<br>{% endfor %}</div>{% endif %}
  <form class="novo" method="post" action="{{ url_for('cadastrar') }}">
    <label>Nome do aluno<input name="nome" value="{{ nome }}" autocomplete="off" autofocus maxlength="60"></label>
    {% for i in range(1, qtd + 1) %}
    <label>Nota {{ i }}<input name="nota{{ i }}" value="{{ valores[i-1] }}" inputmode="decimal" placeholder="0 a 10" autocomplete="off"></label>
    {% endfor %}
    <div class="acoes">
      <button type="submit">Cadastrar aluno</button>
      <button class="sec" type="submit" formaction="{{ url_for('encerrar') }}" formnovalidate>Encerrar cadastro (SAIR)</button>
    </div>
  </form></section>
{% endif %}
<section class="card"><h2>Alunos cadastrados ({{ alunos|length }})</h2>
{% if alunos %}
  <table><thead><tr><th>Aluno</th>{% for i in range(1, qtd + 1) %}<th>Nota {{ i }}</th>{% endfor %}<th>Média</th><th>Situação</th></tr></thead><tbody>
  {% for a in alunos %}<tr><td>{{ a.nome }}</td>{% for n in a.notas %}<td>{{ '%.1f'|format(n) }}</td>{% endfor %}<td class="media">{{ '%.2f'|format(a.media) }}</td><td>{% if a.media >= aprovacao %}<span class="sit ap">Aprovado</span>{% else %}<span class="sit rp">Reprovado</span>{% endif %}</td></tr>{% endfor %}
  </tbody></table>
<p class="vazio" style="margin:12px 0 0">Aprovados: {{ aprovados }} · Reprovados: {{ alunos|length - aprovados }} · Aprovação com média a partir de {{ '%.1f'|format(aprovacao) }}</p>
{% else %}<p class="vazio">Nenhum aluno cadastrado.</p>{% endif %}
{% if encerrado or alunos %}
  <form method="post" action="{{ url_for('reiniciar') }}" style="margin-top:14px"><button class="sec" type="submit">Novo fechamento (limpar)</button></form>
{% endif %}
</section></main></body></html>"""


def desenhar(erros=None, nome="", valores=("", "", "")):
    alunos = session.get("alunos", [])
    return render_template_string(PAGINA, alunos=alunos, encerrado=session.get("encerrado", False),
                                 erros=erros or [], nome=nome, valores=valores, qtd=QTD_NOTAS,
                                 aprovacao=MEDIA_APROVACAO,
                                 aprovados=sum(1 for a in alunos if a["media"] >= MEDIA_APROVACAO))


@app.get("/")
def inicio():
    return desenhar()


@app.post("/cadastrar")
def cadastrar():
    nome = request.form.get("nome", "").strip()
    if nome.lower() == "sair":  # condição de parada
        return encerrar()
    textos = [request.form.get(f"nota{i}", "") for i in range(1, QTD_NOTAS + 1)]
    erros, notas = [], []
    if not nome:
        erros.append("Digite o nome do aluno (ou SAIR para encerrar).")
    for i, t in enumerate(textos, 1):
        nota, erro = ler_nota(t)
        if erro:
            erros.append(f"Nota {i}: {erro}.")
        else:
            notas.append(nota)
    alunos = session.get("alunos", [])
    if not erros and len(alunos) >= MAX_ALUNOS:
        erros.append(f"Limite de {MAX_ALUNOS} alunos atingido.")
    if erros:
        return desenhar(erros, nome, textos)
    alunos.append({"nome": nome, "notas": notas, "media": calcular_media(*notas)})
    session["alunos"] = alunos
    session["encerrado"] = False
    return redirect(url_for("inicio"))


@app.post("/encerrar")
def encerrar():
    session["encerrado"] = True
    return redirect(url_for("inicio"))


@app.post("/reiniciar")
def reiniciar():
    session.clear()
    return redirect(url_for("inicio"))


if __name__ == "__main__":
    app.run(debug=False)
