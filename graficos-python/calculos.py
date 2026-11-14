"""Validação e cálculos puros de backups da Carteira Cripto, em USDT."""

from datetime import date
from math import fsum, isfinite
import re


def data_valida(valor):
    """Retorna uma data ISO existente ou None para registros sem data válida."""
    if not isinstance(valor, str) or not re.fullmatch(r"\d{4}-\d{2}-\d{2}", valor):
        return None
    try:
        return date.fromisoformat(valor)
    except ValueError:
        return None


def numero(registro, campo, contexto, opcional=False, positivo=True):
    """Lê um número finito e aponta o campo exato em caso de erro."""
    valor = registro.get(campo)
    if opcional and valor is None:
        return 0.0
    if valor is None:
        raise ValueError(f"{contexto}: campo ausente ou nulo: {campo}")
    if isinstance(valor, bool) or not isinstance(valor, (int, float)):
        raise ValueError(f"{contexto}: {campo} deve ser um número JSON")
    try:
        valor = float(valor)
    except OverflowError as erro:
        raise ValueError(f"{contexto}: {campo} é grande demais") from erro
    if not isfinite(valor) or (valor <= 0 if positivo else valor < 0):
        limite = "maior que zero" if positivo else "não negativo"
        raise ValueError(f"{contexto}: {campo} deve ser finito e {limite}")
    return valor


def normalizar_registros(registros, venda, contexto):
    """Valida transações sem modificar a lista original nem descartar operações."""
    if not isinstance(registros, list):
        raise ValueError(f"{contexto}: deve ser uma lista")
    resultado = []
    campos = ("qty", "sellPrice") if venda else ("qty", "usdtSpent", "price", "currentPrice")
    for indice, registro in enumerate(registros, 1):
        local = f"{contexto}, registro {indice}"
        if not isinstance(registro, dict):
            raise ValueError(f"{local}: deve ser um objeto")
        moeda = registro.get("coin")
        if not isinstance(moeda, str) or not moeda.strip():
            raise ValueError(f"{local}: campo coin ausente ou inválido")
        item = {campo: numero(registro, campo, local) for campo in campos}
        item.update(coin=moeda.strip().upper(), date=registro.get("date", ""))
        item["fee"] = numero(registro, "fee", local, opcional=True, positivo=False)
        resultado.append(item)
    return resultado


def normalizar_backup(backup):
    """Aceita versões 3/4 e devolve carteiras validadas; ignora campos extras."""
    if not isinstance(backup, dict):
        raise ValueError("O backup deve conter um objeto JSON")
    versao = backup.get("version")
    if versao == 3:
        carteiras = [{"name": "Carteira", "purchases": backup.get("purchases"),
                      "sales": backup.get("sales")}]
    elif versao == 4:
        carteiras = backup.get("wallets")
    else:
        raise ValueError("Campo version ausente ou não suportado; use versão 3 ou 4")
    if not isinstance(carteiras, list):
        raise ValueError("Campo wallets ausente ou inválido")
    resultado = []
    for indice, carteira in enumerate(carteiras, 1):
        if not isinstance(carteira, dict):
            raise ValueError(f"Carteira {indice}: deve ser um objeto")
        nome = carteira.get("name")
        if not isinstance(nome, str) or not nome.strip():
            raise ValueError(f"Carteira {indice}: campo name ausente ou inválido")
        cor = carteira.get("color", "#CCD0CF")
        if not isinstance(cor, str) or not re.fullmatch(r"#[0-9a-fA-F]{6}", cor):
            cor = "#CCD0CF"
        resultado.append({
            "name": nome.strip(), "color": cor,
            "purchases": normalizar_registros(carteira.get("purchases"), False, f"{nome}/purchases"),
            "sales": normalizar_registros(carteira.get("sales"), True, f"{nome}/sales"),
        })
    return resultado


def tolerancia(quantidade):
    """Calcula a tolerância relativa usada para zerar posições."""
    return max(1e-9, quantidade * 1e-9)


def preco_atual(compras):
    """Usa a compra de data válida mais recente; sem datas, a última da lista.

    Empates de data usam a primeira compra, como a ordenação estável do site.
    """
    if not compras:
        return 0.0
    datadas = [(data_valida(compra.get("date")), compra) for compra in compras]
    datadas = [(dia, compra) for dia, compra in datadas if dia is not None]
    compra = max(datadas, key=lambda item: item[0])[1] if datadas else compras[-1]
    return compra["currentPrice"]


def calcular_moeda(moeda, compras, vendas):
    """Calcula PM e resultados sem reduzir o PM pelas vendas."""
    comprada = fsum(p["qty"] for p in compras)
    vendida = fsum(s["qty"] for s in vendas)
    custo = fsum(p["usdtSpent"] + (p.get("fee") or 0) for p in compras)
    pm = custo / comprada if comprada else 0.0
    restante = max(0.0, comprada - vendida)
    if restante <= tolerancia(comprada):
        restante = 0.0
    atual = preco_atual(compras)
    custo_carteira = restante * pm
    valor_atual = restante * atual
    resultado = valor_atual - custo_carteira
    detalhes = [dict(s, lucro=s["qty"] * s["sellPrice"] - (s.get("fee") or 0) - s["qty"] * pm)
                for s in vendas]
    return {
        "coin": moeda, "pm": pm, "break_even": pm, "comprada": comprada,
        "vendida": vendida, "restante": restante, "custo_total": custo,
        "custo_carteira": custo_carteira, "preco_atual": atual, "valor_atual": valor_atual,
        "nao_realizado": resultado,
        "nao_realizado_pct": resultado / custo_carteira * 100 if custo_carteira else 0.0,
        "realizado": fsum(s["lucro"] for s in detalhes), "vendas": detalhes,
        "saldo_inconsistente": vendida - comprada > tolerancia(comprada),
    }


def calcular_carteira(carteira):
    """Inclui também moedas presentes somente nas vendas para avisar inconsistências."""
    compras, vendas = carteira["purchases"], carteira["sales"]
    moedas = sorted({p["coin"] for p in compras} | {s["coin"] for s in vendas})
    return [calcular_moeda(moeda, [p for p in compras if p["coin"] == moeda],
                          [s for s in vendas if s["coin"] == moeda]) for moeda in moedas]


def realizado_por_mes(resultados):
    """Soma vendas datadas por mês, usando o PM atual de toda a moeda."""
    meses = {}
    for moeda in resultados:
        for venda in moeda["vendas"]:
            dia = data_valida(venda.get("date"))
            if dia is not None:
                meses.setdefault(dia.strftime("%Y-%m"), []).append(venda["lucro"])
    return [(mes, fsum(valores)) for mes, valores in sorted(meses.items())]


def investimento_acumulado(compras):
    """Acumula gastos e taxas por data de compra, sem subtrair vendas."""
    dias = {}
    for compra in compras:
        dia = data_valida(compra.get("date"))
        if dia is not None:
            dias.setdefault(dia, []).append(compra["usdtSpent"] + (compra.get("fee") or 0))
    resultado, total = [], 0.0
    for dia, valores in sorted(dias.items()):
        total = fsum([total, *valores])
        resultado.append((dia, total))
    return resultado
