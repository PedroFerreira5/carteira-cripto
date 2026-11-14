# Gráficos da Carteira Cripto

Instale o Python 3.11 ou superior pelo instalador do Python para Windows e habilite a opção de adicionar o Python ao PATH. Abra a pasta `graficos-python` no VS Code e execute no terminal do PowerShell.

```powershell
python -m pip install -r requirements.txt
python -m pytest
python graficos.py backup.json
```

Use um backup JSON exportado pela Carteira Cripto. Os PNGs ficam na pasta `graficos` por padrão. Para escolher a saída e filtrar uma carteira, use:

```powershell
python graficos.py "C:\caminho\backup.json" --saida relatorio --carteira "Pedro"
```

O terminal mostra o resumo em USDT e os caminhos dos arquivos gerados. Registros sem data válida entram no resumo e ficam fora dos gráficos por tempo.
