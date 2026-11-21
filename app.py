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


PAGINA = r"""<!doctype html>
<html lang="pt-br"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>Fechamento de notas</title>
<style>
:root{--azul:#0131CD;--lima:#B9FC01;--rosa:#FF4D6D;--bg:#040817;--txt:#EAF0FF;--mudo:#8FA0D6;--vidro:rgba(255,255,255,.06);--borda:rgba(255,255,255,.14)}
*{box-sizing:border-box}
html{background:var(--bg)}
body{margin:0;min-height:100vh;font-family:system-ui,"Segoe UI",Arial,sans-serif;color:var(--txt);
 background:radial-gradient(900px 500px at 12% -10%,rgba(1,49,205,.75),transparent 60%),radial-gradient(700px 420px at 100% 0%,rgba(185,252,1,.14),transparent 60%),var(--bg);position:relative;overflow-x:hidden}
body::before{content:"";position:fixed;inset:0;pointer-events:none;
 background-image:linear-gradient(rgba(143,160,214,.08) 1px,transparent 1px),linear-gradient(90deg,rgba(143,160,214,.08) 1px,transparent 1px);
 background-size:44px 44px;mask-image:radial-gradient(ellipse at 50% 0%,#000 25%,transparent 75%);-webkit-mask-image:radial-gradient(ellipse at 50% 0%,#000 25%,transparent 75%)}
.wrap{position:relative;max-width:940px;margin:0 auto;padding:26px 16px 56px}
header{display:flex;flex-wrap:wrap;gap:14px;align-items:center;justify-content:space-between;margin-bottom:22px}
h1{margin:0;font-size:clamp(1.5rem,4vw,2.1rem);letter-spacing:-.02em}
h1 span{color:var(--lima);text-shadow:0 0 18px rgba(185,252,1,.55)}
.sub{margin:6px 0 0;color:var(--mudo)}
.pill{display:inline-flex;align-items:center;gap:8px;border:1px solid var(--borda);background:var(--vidro);border-radius:999px;padding:6px 14px;font-size:.78rem;letter-spacing:.12em;color:var(--mudo)}
.pill i{width:8px;height:8px;border-radius:50%;background:var(--lima);box-shadow:0 0 10px var(--lima);animation:pulso 1.8s infinite}
@keyframes pulso{50%{opacity:.35;transform:scale(.7)}}
.stats{display:grid;grid-template-columns:repeat(4,1fr);gap:12px;margin-bottom:18px}
.glass{background:var(--vidro);border:1px solid var(--borda);border-radius:18px;backdrop-filter:blur(14px);-webkit-backdrop-filter:blur(14px);box-shadow:0 10px 40px rgba(0,0,40,.35)}
.stat{padding:16px}.stat small{display:block;color:var(--mudo);font-size:.72rem;letter-spacing:.12em;text-transform:uppercase}
.stat b{display:block;margin-top:6px;font-size:1.7rem;font-variant-numeric:tabular-nums}
.stat.hl b{color:var(--lima);text-shadow:0 0 16px rgba(185,252,1,.45)}
.card{padding:20px;margin-bottom:18px}
h2{margin:0 0 14px;font-size:.85rem;letter-spacing:.16em;text-transform:uppercase;color:var(--mudo)}
form.novo{display:grid;grid-template-columns:2fr 1fr 1fr 1fr;gap:12px;align-items:end}
label{display:grid;gap:6px;font-size:.78rem;color:var(--mudo);letter-spacing:.06em}
input{font:inherit;color:var(--txt);width:100%;padding:12px;border-radius:12px;border:1px solid var(--borda);background:rgba(4,8,23,.55);transition:.2s}
input::placeholder{color:#5F6FA8}
input:focus{outline:0;border-color:var(--lima);box-shadow:0 0 0 3px rgba(185,252,1,.18),0 0 22px rgba(185,252,1,.18)}
.acoes{grid-column:1/-1;display:flex;gap:10px;flex-wrap:wrap;align-items:center}
button{font:inherit;font-weight:800;border-radius:12px;padding:12px 20px;cursor:pointer;transition:.18s;border:1px solid transparent}
.prim{background:var(--lima);color:#06103A;box-shadow:0 0 24px rgba(185,252,1,.38)}
.prim:hover{transform:translateY(-2px);box-shadow:0 0 34px rgba(185,252,1,.6)}
.sec{background:transparent;color:var(--txt);border-color:var(--borda)}.sec:hover{border-color:var(--lima);color:var(--lima)}
.prev[hidden]{display:none}
.prev{margin-left:auto;display:flex;align-items:center;gap:12px;color:var(--mudo);font-size:.82rem}
.alerta{border-radius:12px;padding:12px 14px;margin-bottom:14px;background:rgba(255,77,109,.12);border:1px solid rgba(255,77,109,.45);color:#FFB3C0}
.ok{border-radius:12px;padding:12px 14px;margin-bottom:18px;background:rgba(185,252,1,.1);border:1px solid rgba(185,252,1,.4);color:var(--lima)}
.ring{--p:0;--c:var(--lima);width:54px;height:54px;border-radius:50%;display:grid;place-items:center;flex:none;
 background:conic-gradient(var(--c) calc(var(--p)*1%),rgba(255,255,255,.12) 0);box-shadow:0 0 16px color-mix(in srgb,var(--c) 40%,transparent);transition:.4s}
.ring span{width:42px;height:42px;border-radius:50%;background:#0A1236;display:grid;place-items:center;font-weight:800;font-size:.9rem;font-variant-numeric:tabular-nums}
.ring.rp{--c:var(--rosa)}
.lista{display:grid;gap:10px}
.aluno{display:grid;grid-template-columns:54px 1.4fr repeat(3,.6fr) auto;gap:14px;align-items:center;padding:12px 16px;border-radius:16px;background:rgba(255,255,255,.04);border:1px solid var(--borda);animation:entra .5s both}
@keyframes entra{from{opacity:0;transform:translateY(12px)}}
.aluno .nome{font-weight:700}.aluno .n{color:var(--mudo);font-variant-numeric:tabular-nums;font-size:.9rem}.aluno .n b{display:block;color:var(--txt);font-size:1rem}
.aluno .n small{display:block;font-size:.65rem;letter-spacing:.1em;text-transform:uppercase}
.sit{border-radius:999px;padding:5px 14px;font-size:.78rem;font-weight:800;letter-spacing:.06em;white-space:nowrap}
.sit.ap{background:rgba(185,252,1,.14);color:var(--lima);border:1px solid rgba(185,252,1,.5);box-shadow:0 0 14px rgba(185,252,1,.25)}
.sit.rp{background:rgba(255,77,109,.14);color:var(--rosa);border:1px solid rgba(255,77,109,.5);box-shadow:0 0 14px rgba(255,77,109,.25)}
.vazio{color:var(--mudo);margin:0}
.rodape{margin-top:14px;color:var(--mudo);font-size:.82rem}
@media(max-width:700px){.stats{grid-template-columns:1fr 1fr}form.novo{grid-template-columns:1fr 1fr}form.novo label:first-child{grid-column:1/-1}
 .aluno{grid-template-columns:54px 1fr auto;row-gap:8px}.aluno .n{display:none}.prev{margin-left:0;width:100%}}
@media(prefers-reduced-motion:reduce){*{animation:none!important;transition:none!important}}
</style></head><body><div class="wrap">
<header><div><h1><span>//</span> Fechamento de notas</h1><p class="sub">Cadastre o aluno e as 3 notas. Para encerrar, digite SAIR no nome.</p></div>
<div class="pill"><i></i>SISTEMA ONLINE</div></header>

<section class="stats">
 <div class="glass stat"><small>Alunos</small><b data-n="{{ alunos|length }}" data-d="0">0</b></div>
 <div class="glass stat hl"><small>Média da turma</small><b data-n="{{ media_turma }}" data-d="2">0</b></div>
 <div class="glass stat"><small>Maior média</small><b data-n="{{ maior }}" data-d="2">0</b></div>
 <div class="glass stat"><small>Aprovação</small><b data-n="{{ pct }}" data-d="0" data-s="%">0</b></div>
</section>

{% if encerrado %}<div class="ok">Cadastro encerrado. Veja o resumo abaixo.</div>
{% else %}
<section class="glass card"><h2>Novo aluno</h2>
{% if erros %}<div class="alerta">{% for e in erros %}{{ e }}<br>{% endfor %}</div>{% endif %}
<form class="novo" method="post" action="{{ url_for('cadastrar') }}" id="f">
 <label>NOME DO ALUNO<input name="nome" value="{{ nome }}" autocomplete="off" autofocus maxlength="60"></label>
 {% for i in range(1, qtd + 1) %}<label>NOTA {{ i }}<input name="nota{{ i }}" value="{{ valores[i-1] }}" inputmode="decimal" placeholder="0 a 10" autocomplete="off"></label>{% endfor %}
 <div class="acoes">
  <button class="prim" type="submit">Cadastrar aluno</button>
  <button class="sec" type="submit" formaction="{{ url_for('encerrar') }}" formnovalidate>Encerrar (SAIR)</button>
  <div class="prev" id="prev" hidden><div class="ring" id="ring"><span id="rv">0.0</span></div><div><b id="rs"></b><br>média ao vivo</div></div>
 </div>
</form></section>
{% endif %}

<section class="glass card"><h2>Alunos cadastrados ({{ alunos|length }})</h2>
{% if alunos %}<div class="lista">
{% for a in alunos %}{% set ok = a.media >= aprovacao %}
 <div class="aluno" style="animation-delay:{{ loop.index0 * 60 }}ms">
  <div class="ring {{ '' if ok else 'rp' }}" style="--p:{{ (a.media * 10)|round(0) }}"><span>{{ '%.1f'|format(a.media) }}</span></div>
  <div class="nome">{{ a.nome }}</div>
  {% for n in a.notas %}<div class="n"><small>Nota {{ loop.index }}</small><b>{{ '%.1f'|format(n) }}</b></div>{% endfor %}
  <span class="sit {{ 'ap' if ok else 'rp' }}">{{ 'APROVADO' if ok else 'REPROVADO' }}</span>
 </div>{% endfor %}</div>
<p class="rodape">Aprovados: {{ aprovados }} · Reprovados: {{ alunos|length - aprovados }} · Aprovação com média a partir de {{ '%.1f'|format(aprovacao) }}</p>
{% else %}<p class="vazio">Nenhum aluno cadastrado.</p>{% endif %}
{% if encerrado or alunos %}<form method="post" action="{{ url_for('reiniciar') }}" style="margin-top:16px"><button class="sec" type="submit">Novo fechamento (limpar)</button></form>{% endif %}
</section></div>
<script>
// contagem animada dos números do topo
document.querySelectorAll('.stat b').forEach(function(el){
  var alvo=parseFloat(el.dataset.n)||0, d=+el.dataset.d, suf=el.dataset.s||'', t0=null;
  function passo(t){ if(!t0)t0=t; var k=Math.min((t-t0)/700,1), v=alvo*(1-Math.pow(1-k,3)); el.textContent=v.toFixed(d)+suf; if(k<1)requestAnimationFrame(passo); }
  requestAnimationFrame(passo);
});
// média ao vivo enquanto digita
(function(){
  var f=document.getElementById('f'); if(!f)return;
  var corte={{ aprovacao }}, ring=document.getElementById('ring'), rv=document.getElementById('rv'), rs=document.getElementById('rs'), prev=document.getElementById('prev');
  function calc(){
    var n=[1,2,3].map(function(i){return parseFloat((f['nota'+i].value||'').replace(',','.'));});
    if(n.some(function(x){return isNaN(x)||x<0||x>10;})){prev.hidden=true;return;}
    var m=(n[0]+n[1]+n[2])/3, ok=m>=corte;
    prev.hidden=false; rv.textContent=m.toFixed(1); ring.style.setProperty('--p',Math.round(m*10));
    ring.classList.toggle('rp',!ok); rs.textContent=ok?'APROVADO':'REPROVADO'; rs.style.color=ok?'var(--lima)':'var(--rosa)';
  }
  ['nota1','nota2','nota3'].forEach(function(n){f[n].addEventListener('input',calc);}); calc();
})();
</script></body></html>"""


def desenhar(erros=None, nome="", valores=("", "", "")):
    alunos = session.get("alunos", [])
    medias = [x["media"] for x in alunos]
    aprovados = sum(1 for m in medias if m >= MEDIA_APROVACAO)
    media_turma = round(sum(medias) / len(medias), 2) if medias else 0
    maior = round(max(medias), 2) if medias else 0
    pct = round(aprovados * 100 / len(medias)) if medias else 0
    return render_template_string(PAGINA, alunos=alunos, encerrado=session.get("encerrado", False),
                                 media_turma=media_turma, maior=maior, pct=pct,
                                 erros=erros or [], nome=nome, valores=valores, qtd=QTD_NOTAS,
                                 aprovacao=MEDIA_APROVACAO,
                                 aprovados=aprovados)


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
