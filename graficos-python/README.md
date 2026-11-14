# Gráficos da Carteira Cripto

O script lê o backup JSON do site, gera PNGs e imprime um resumo em USDT. Aceita backups v4 com múltiplas carteiras e v3 com compras e vendas na raiz.

## Instalar e testar no Windows

Instale o Python 3.11 ou superior e habilite a opção de adicionar o Python ao PATH, se disponível. [Instaladores oficiais](https://www.python.org/downloads/windows/)

Abra um terminal PowerShell na pasta graficos-python e rode:

```powershell
python --version
python -m pip install -r requirements.txt
python -m pytest
```

## Gerar com seus dados

No site, clique em **baixar backup** no rodapé. Guarde o JSON em Downloads e troque NOME-DO-BACKUP.json pelo nome baixado.

```powershell
python graficos.py "$env:USERPROFILE\Downloads\NOME-DO-BACKUP.json"
```

A saída padrão fica em **Downloads → graficos-carteira**. Para escolher outra pasta e filtrar uma carteira, rode:

```powershell
python graficos.py "$env:USERPROFILE\Downloads\NOME-DO-BACKUP.json" --carteira "Pedro" --saida "$env:USERPROFILE\Downloads\graficos-teste"
```

| Arquivo | Como ler |
| --- | --- |
| *_distribuicao.png | Pizza com o custo e a participação de cada moeda. Posições zeradas ficam fora. |
| *_realizado_mensal.png | Barras de lucro ou prejuízo das vendas com data válida, por mês. |
| *_investimento_acumulado.png | Barras do gasto acumulado em compras com data válida, incluindo taxas. |
| comparacao_carteiras.png | Barras de custo e resultado não realizado. Aparece com mais de uma carteira selecionada e operações. |

O resultado não realizado por moeda aparece no resumo do terminal, junto de PM, saldo, custo e preço atual. O resumo também mostra o lucro realizado total, avisos de vendas acima do saldo e os arquivos gerados. Registros sem data válida entram nos totais e ficam fora dos gráficos por tempo.

Para conferir uma nova execução, use uma pasta nova com --saida. PNGs antigos, incluindo *_nao_realizado.png, permanecem na pasta em que foram gerados.

## Privacidade

Guarde os backups e PNGs reais fora do repositório. O .gitignore ignora novos JSONs, PNGs e caches do Python. Arquivos já rastreados e inclusões forçadas com git add -f ainda podem entrar em commits.

## Arquivos

- calculos.py contém a validação e os cálculos em funções puras com a biblioteca padrão.
- graficos.py contém o CLI e a geração dos PNGs com Matplotlib em modo Agg.
- test_calculos.py cobre PM, taxas, vendas, tolerância de saldo, datas e backups v3/v4.
- requirements.txt lista as dependências.
