"""CLI para gerar relatórios PNG de backups da Carteira Cripto."""

import argparse
import json
from math import fsum
from pathlib import Path
import re
import sys

from calculos import (calcular_carteira, data_valida, investimento_acumulado,
                      normalizar_backup, realizado_por_mes)

FUNDO = "#06141B"
SUPERFICIE = "#11212D"
TEXTO = "#CCD0CF"
SECUNDARIO = "#9BA8AB"
GRADE = "#253745"
GANHO = "#5FBF8F"
PERDA = "#E78678"


def ler_backup(caminho):
    """Lê JSON UTF-8 (com ou sem BOM) e valida versões e campos conhecidos."""
    try:
        with Path(caminho).open(encoding="utf-8-sig") as arquivo:
            backup = json.load(arquivo)
    except FileNotFoundError as erro:
        raise ValueError(f"Arquivo não encontrado: {caminho}") from erro
    except (json.JSONDecodeError, UnicodeDecodeError) as erro:
        raise ValueError(f"JSON inválido ou arquivo fora de UTF-8: {caminho}") from erro
    except OSError as erro:
        raise ValueError(f"Não foi possível ler {caminho}: {erro}") from erro
    return normalizar_backup(backup)


def formatar_numero(valor, casas=2):
    """Formata milhares e decimais em pt-BR sem depender do locale instalado."""
    if valor and abs(valor) < 1:
        casas = 8
    texto = f"{valor:,.{casas}f}"
    return texto.translate(str.maketrans({",": ".", ".": ","}))


def nome_seguro(nome):
    """Remove caracteres inválidos em nomes de arquivos do Windows."""
    nome = re.sub(r'[<>:"/\\|?*\x00-\x1f]', "_", nome).strip(" .")[:80].rstrip(" .")
    return nome or "Carteira"


def nomes_unicos(carteiras):
    """Evita colisões entre nomes que se tornam iguais após a limpeza."""
    usados, nomes = set(), []
    for carteira in carteiras:
        base = nome_seguro(carteira["name"])
        nome, indice = base, 2
        while nome.casefold() in usados:
            nome = f"{base}_{indice}"
            indice += 1
        usados.add(nome.casefold())
        nomes.append(nome)
    return nomes


def configurar_graficos():
    """Carrega matplotlib sem janela e configura o tema escuro."""
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    plt.rcParams.update({
        "figure.facecolor": FUNDO, "axes.facecolor": SUPERFICIE,
        "text.color": TEXTO, "axes.labelcolor": TEXTO, "axes.titlecolor": TEXTO,
        "xtick.color": SECUNDARIO, "ytick.color": SECUNDARIO,
        "axes.edgecolor": GRADE, "grid.color": GRADE, "font.size": 11,
        "savefig.facecolor": FUNDO, "axes.axisbelow": True,
    })
    return plt


def novo_grafico(plt, titulo, quantidade=0):
    """Cria figura com altura suficiente para listas de moedas/carteiras."""
    figura, eixo = plt.subplots(figsize=(11, max(5, quantidade * 0.45 + 2)), layout="constrained")
    eixo.set_title(titulo, pad=18)
    return figura, eixo


def eixo_monetario(eixo, horizontal=False):
    """Aplica rótulos em USDT e formatação brasileira ao eixo monetário."""
    from matplotlib.ticker import FuncFormatter
    alvo = eixo.xaxis if horizontal else eixo.yaxis
    alvo.set_major_formatter(FuncFormatter(lambda valor, _: formatar_numero(valor)))
    if horizontal:
        eixo.set_xlabel("USDT")
        eixo.grid(axis="x", alpha=0.6)
    else:
        eixo.set_ylabel("USDT")
        eixo.grid(axis="y", alpha=0.6)


def salvar(plt, figura, caminho):
    """Salva PNG e libera a figura mesmo quando a gravação falha."""
    try:
        figura.savefig(caminho, dpi=160)
    finally:
        plt.close(figura)
    return caminho


def gerar_carteira(plt, pasta, carteira, resultados, nome):
    """Gera até três gráficos e avisa quando faltar informação para algum deles."""
    arquivos = []
    titulo, cor = carteira["name"], carteira["color"]
    abertas = [r for r in resultados if r["restante"] > 0]
    if abertas:
        figura, eixo = novo_grafico(plt, f"{titulo} — Custo em carteira por moeda")
        abertas.sort(key=lambda item: item["custo_carteira"], reverse=True)
        valores = [item["custo_carteira"] for item in abertas]
        total = fsum(valores)
        cores = [cor, "#7FB3D5", "#5FB3B3", "#A59BC9", "#C9B98F", "#D9A27A"]
        cores = list(dict.fromkeys(cores + [TEXTO]))
        fatias, _ = eixo.pie(valores, startangle=90, colors=cores,
                             wedgeprops={"edgecolor": FUNDO, "linewidth": 1.5})
        rotulos = [
            f"{item['coin']} · {formatar_numero(item['custo_carteira'])} USDT"
            f" ({formatar_numero(item['custo_carteira'] / total * 100, 1)}%)"
            for item in abertas
        ]
        eixo.legend(fatias, rotulos, loc="center left", bbox_to_anchor=(1, 0.5),
                    frameon=False, labelcolor=TEXTO)
        arquivos.append(salvar(plt, figura, pasta / f"{nome}_distribuicao.png"))
    else:
        print(f"Aviso [{titulo}]: distribuição não gerada; nenhuma posição aberta.")

    meses = realizado_por_mes(resultados)
    if meses:
        figura, eixo = novo_grafico(plt, f"{titulo} — Resultado realizado por mês")
        valores = [valor for _, valor in meses]
        eixo.bar([mes[5:] + "/" + mes[:4] for mes, _ in meses], valores,
                 color=[GANHO if valor > 0 else PERDA if valor < 0 else SECUNDARIO for valor in valores])
        eixo.axhline(0, color=SECUNDARIO, linewidth=0.8)
        eixo.set_xlabel("Mês da venda")
        eixo.tick_params(axis="x", labelrotation=45)
        eixo_monetario(eixo)
        arquivos.append(salvar(plt, figura, pasta / f"{nome}_realizado_mensal.png"))
    else:
        print(f"Aviso [{titulo}]: resultado mensal não gerado; nenhuma venda com data válida.")

    acumulado = investimento_acumulado(carteira["purchases"])
    if acumulado:
        from matplotlib import dates as mdates
        figura, eixo = novo_grafico(plt, f"{titulo} — Compras acumuladas com taxas")
        dias = [dia for dia, _ in acumulado]
        menor_intervalo = min(
            ((atual - anterior).days for anterior, atual in zip(dias, dias[1:])),
            default=1,
        )
        eixo.bar(dias, [valor for _, valor in acumulado],
                 color=cor, width=menor_intervalo * 0.8)
        eixo.xaxis.set_major_locator(mdates.AutoDateLocator(minticks=3, maxticks=8))
        eixo.xaxis.set_major_formatter(mdates.DateFormatter("%d/%m/%Y"))
        eixo.tick_params(axis="x", labelrotation=30)
        eixo.set_xlabel("Data da compra")
        eixo_monetario(eixo)
        arquivos.append(salvar(plt, figura, pasta / f"{nome}_investimento_acumulado.png"))
    else:
        print(f"Aviso [{titulo}]: evolução não gerada; nenhuma compra com data válida.")

    return arquivos


def gerar_comparacao(plt, pasta, carteiras, resultados):
    """Compara custo e resultado; cores de lucro/prejuízo mantêm seu significado."""
    figura, eixo = novo_grafico(plt, "Comparação entre carteiras", len(carteiras) * 2)
    posicoes = list(range(len(carteiras)))
    custos = [fsum(r["custo_carteira"] for r in itens) for itens in resultados]
    ganhos = [fsum(r["nao_realizado"] for r in itens) for itens in resultados]
    eixo.barh([p - 0.2 for p in posicoes], custos, height=0.35,
              color=[c["color"] for c in carteiras])
    eixo.barh([p + 0.2 for p in posicoes], ganhos, height=0.35,
              color=[GANHO if v > 0 else PERDA if v < 0 else SECUNDARIO for v in ganhos])
    eixo.set_yticks(posicoes, [c["name"] for c in carteiras])
    eixo.invert_yaxis()
    eixo.axvline(0, color=SECUNDARIO, linewidth=0.8)
    eixo_monetario(eixo, horizontal=True)
    from matplotlib.patches import Patch
    eixo.legend(handles=[Patch(color=TEXTO, label="Custo em carteira (cor da carteira)"),
                         Patch(color=GANHO, label="Lucro não realizado"),
                         Patch(color=PERDA, label="Prejuízo não realizado")],
                facecolor=SUPERFICIE, edgecolor=GRADE, labelcolor=TEXTO)
    return salvar(plt, figura, pasta / "comparacao_carteiras.png")


def imprimir_resumo(carteira, resultados):
    """Imprime tabela por moeda, lucro realizado e avisos de saldo/datas."""
    print(f"\nCarteira: {carteira['name']} — valores em USDT")
    cabecalho = ["Moeda", "PM", "Qtd. restante", "Custo em carteira", "Preço atual", "Não realizado"]
    linhas = [[r["coin"], formatar_numero(r["pm"], 8), formatar_numero(r["restante"], 8),
               formatar_numero(r["custo_carteira"]), formatar_numero(r["preco_atual"], 8),
               formatar_numero(r["nao_realizado"])] for r in resultados]
    larguras = [max(len(linha[i]) for linha in [cabecalho, *linhas]) for i in range(len(cabecalho))]
    for linha in [cabecalho, *linhas]:
        print(" | ".join(valor.ljust(larguras[i]) if i == 0 else valor.rjust(larguras[i])
                         for i, valor in enumerate(linha)))
    if not resultados:
        print("Carteira sem compras ou vendas.")
    print("Lucro realizado total: " + formatar_numero(fsum(r["realizado"] for r in resultados)) + " USDT")
    for r in resultados:
        if r["saldo_inconsistente"]:
            print(f"Aviso [{r['coin']}]: quantidade vendida ({formatar_numero(r['vendida'], 8)}) "
                  f"excede a comprada ({formatar_numero(r['comprada'], 8)}).")
    for campo, descricao in [("purchases", "compras"), ("sales", "vendas")]:
        sem_data = sum(data_valida(item.get("date")) is None for item in carteira[campo])
        if sem_data:
            print(f"Aviso: {sem_data} {descricao} sem data válida; excluídas somente dos gráficos por tempo.")


def main(argv=None):
    """Executa o CLI e devolve código de saída para uso em terminal e testes."""
    parser = argparse.ArgumentParser(description="Gera gráficos PNG de backups da Carteira Cripto, em USDT.")
    parser.add_argument("backup", type=Path, help="Arquivo JSON, versão 3 ou 4")
    saida_padrao = Path.home() / "Downloads" / "graficos-carteira"
    parser.add_argument("--saida", type=Path, default=saida_padrao, metavar="PASTA",
                        help=f"Pasta dos PNGs (padrão: {saida_padrao})")
    parser.add_argument("--carteira", metavar="NOME", help="Filtra pelo nome, ignorando maiúsculas")
    args = parser.parse_args(argv)
    try:
        carteiras = ler_backup(args.backup)
        if args.carteira is not None:
            carteiras = [c for c in carteiras if c["name"].casefold() == args.carteira.strip().casefold()]
            if not carteiras:
                raise ValueError(f"Carteira inexistente: {args.carteira}")
        resultados = [calcular_carteira(c) for c in carteiras]
        arquivos = []
        if any(resultados):
            plt = configurar_graficos()
            args.saida.mkdir(parents=True, exist_ok=True)
            for carteira, itens, nome in zip(carteiras, resultados, nomes_unicos(carteiras)):
                arquivos.extend(gerar_carteira(plt, args.saida, carteira, itens, nome))
            if len(carteiras) > 1:
                arquivos.append(gerar_comparacao(plt, args.saida, carteiras, resultados))
        else:
            print("Aviso: não há compras ou vendas nas carteiras selecionadas; nenhum gráfico gerado.")
        for carteira, itens in zip(carteiras, resultados):
            imprimir_resumo(carteira, itens)
        print("\nArquivos gerados:")
        for arquivo in arquivos:
            print(f"  {arquivo.resolve()}")
        if not arquivos:
            print("  Nenhum.")
        return 0
    except ImportError:
        print("Erro: dependências ausentes. Execute python -m pip install -r requirements.txt", file=sys.stderr)
    except (ValueError, OSError, OverflowError) as erro:
        print(f"Erro: {erro}", file=sys.stderr)
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
