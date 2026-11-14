import json

import pytest

from calculos import calcular_moeda, investimento_acumulado, realizado_por_mes
from graficos import ler_backup


def compra(gasto=500, preco=50000, taxa=None, atual=60000, dia="2026-03-10"):
    return dict(coin="BTC", usdtSpent=gasto, price=preco, qty=gasto / preco,
                fee=taxa, currentPrice=atual, date=dia)


def venda(qty, preco, taxa=2, dia="2026-05-20"):
    return dict(coin="BTC", qty=qty, sellPrice=preco, fee=taxa, date=dia)


def test_pm_com_taxa():
    resultado = calcular_moeda("BTC", [compra(taxa=5)], [])
    assert resultado["pm"] == resultado["break_even"] == 50500
    assert resultado["nao_realizado"] == pytest.approx(95)


def test_pm_ponderado_e_preco_recente():
    compras = [compra(600, 60000, atual=70000, dia="2026-05-01"), compra()]
    resultado = calcular_moeda("BTC", compras, [])
    assert resultado["pm"] == pytest.approx(55000)
    assert resultado["preco_atual"] == 70000
    assert calcular_moeda("BTC", [compra(dia=""), compra(atual=5, dia="")], [])["preco_atual"] == 5


@pytest.mark.parametrize(("preco", "esperado"), [(60000, 48), (40000, -52)])
def test_venda_parcial(preco, esperado):
    resultado = calcular_moeda("BTC", [compra()], [venda(0.005, preco)])
    assert resultado["pm"] == 50000
    assert resultado["restante"] == pytest.approx(0.005)
    assert resultado["realizado"] == pytest.approx(esperado)
    assert realizado_por_mes([resultado])[0][1] == pytest.approx(esperado)


def test_venda_total_e_tolerancia():
    assert calcular_moeda("BTC", [compra()], [venda(0.01, 60000)])["restante"] == 0
    compras = [compra(203, 0.000001)]
    assert calcular_moeda("BTC", compras, [venda(202999999.99, 0.000002)])["restante"] == 0
    assert calcular_moeda("BTC", compras, [venda(204000000, 0.000002)])["saldo_inconsistente"]


def test_vazio_e_datas_invalidas():
    assert calcular_moeda("BTC", [], [])["pm"] == 0
    compras = [compra(dia="2026-02-31")]
    resultado = calcular_moeda("BTC", compras, [venda(0.005, 60000, dia="")])
    assert resultado["realizado"] == pytest.approx(48)
    assert realizado_por_mes([resultado]) == investimento_acumulado(compras) == []


@pytest.mark.parametrize("versao", [3, 4])
def test_leitura_backup(tmp_path, versao):
    dados = {"purchases": [compra()], "sales": []}
    backup = {"version": versao}
    backup.update(dados if versao == 3 else {"wallets": [dict(dados, name="Pedro")]})
    arquivo = tmp_path / "backup.json"
    arquivo.write_text(json.dumps(backup), encoding="utf-8")
    carteira, = ler_backup(arquivo)
    assert carteira["name"] == ("Carteira" if versao == 3 else "Pedro")
    assert calcular_moeda("BTC", carteira["purchases"], carteira["sales"])["pm"] == 50000
