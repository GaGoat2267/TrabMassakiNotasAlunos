"""Fechamento de notas de uma turma.

Lê o nome de cada aluno e 3 notas (0.0 a 10.0), calcula a média aritmética
simples e repete até o usuário digitar SAIR no campo do nome.
"""

QTD_NOTAS = 3
NOTA_MINIMA = 0.0
NOTA_MAXIMA = 10.0


def ler_nome():
    """Pede o nome do aluno. Repete se vier vazio. Devolve o texto digitado."""
    while True:
        nome = input("\nNome do aluno (ou SAIR para encerrar): ").strip()
        if nome:
            return nome
        print("  Digite um nome ou SAIR.")


def ler_nota(numero):
    """Pede uma nota decimal entre 0.0 e 10.0. Aceita ponto ou vírgula."""
    while True:
        texto = input(f"  Nota {numero} (0.0 a 10.0): ").strip().replace(",", ".")
        try:
            nota = float(texto)
        except ValueError:
            print("  Valor inválido. Digite um número, por exemplo 7.5.")
            continue
        if NOTA_MINIMA <= nota <= NOTA_MAXIMA:
            return nota
        print(f"  A nota deve estar entre {NOTA_MINIMA} e {NOTA_MAXIMA}.")


def calcular_media(n1, n2, n3):
    """Média aritmética simples. Os parênteses fazem a soma ocorrer antes da
    divisão (a divisão tem precedência sobre a soma)."""
    return (n1 + n2 + n3) / 3


def main():
    print("=== FECHAMENTO DE NOTAS DA TURMA ===")
    alunos = []

    while True:
        nome = ler_nome()
        if nome.lower() == "sair":  # SAIR, sair, Sair... todos encerram
            break

        notas = [ler_nota(i) for i in range(1, QTD_NOTAS + 1)]
        media = calcular_media(*notas)
        alunos.append((nome, notas, media))
        print(f"  Média de {nome}: {media:.2f}")

    print("\n=== RESUMO ===")
    if not alunos:
        print("Nenhum aluno cadastrado.")
        return
    print(f"{'Aluno':<20}{'Nota 1':>8}{'Nota 2':>8}{'Nota 3':>8}{'Média':>8}")
    for nome, notas, media in alunos:
        print(f"{nome:<20}{notas[0]:>8.1f}{notas[1]:>8.1f}{notas[2]:>8.1f}{media:>8.2f}")
    print(f"\nAlunos cadastrados: {len(alunos)}")


if __name__ == "__main__":
    try:
        main()
    except (KeyboardInterrupt, EOFError):
        print("\nPrograma encerrado.")
