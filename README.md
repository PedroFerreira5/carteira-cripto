# Carteira Cripto

Eu estava com dificuldade de acompanhar meus resultados em cripto: fazia várias compras em momentos diferentes, com preços diferentes, e ficava difícil saber se estava ganhando ou perdendo em cada uma. Criei essa ferramenta para resolver isso, controlando tanto os ativos em carteira quanto os lucros e prejuízos já realizados nas vendas.

🔗 **Acesse:** [https://pedroferreira5.github.io/carteira-cripto/](https://pedroferreira5.github.io/carteira-cripto/)

## Como usar

Abra o `index.html` em um navegador moderno. No primeiro acesso sem dados, o painel de ajuda abre automaticamente. Use **? ajuda** para rever o guia ou **ⓘ como ler as tabelas de compras** para consultar as colunas.

- **Carteiras:** crie carteiras independentes pelas abas no topo. Use **Renomear** para mudar o nome e escolher uma das seis cores. A aba selecionada é lembrada neste navegador.
- **Compras:** informe a moeda, o gasto em USDT e o preço pago. Taxa, câmbio e data são opcionais. O site calcula a quantidade. Novas compras de uma moeda existente mantêm seu preço atual.
- **Vendas:** registre vendas parciais ou use **vender tudo** para preencher o saldo exato. Filtre o histórico por mês. A remoção de uma compra é bloqueada se deixar vendas sem saldo.
- **Simulação:** digite um preço em **vender a** para estimar quanto receberia e ver o resultado sem registrar uma venda.
- **Organização:** busque moedas e ordene por nome ou valor investido. **Excluir moeda** remove as compras e vendas daquela moeda. **Apagar esta carteira** limpa as operações e mantém a aba. **Excluir**, no topo, remove a carteira ativa se houver outra.

## Importar compras

1. Selecione a carteira de destino e abra **Importar Tabela**.
2. Copie as células do Excel ou Google Sheets e cole na caixa de texto. Se estiver digitando, use ponto e vírgula entre os campos, como no exemplo abaixo.
3. Clique em **Importar** e confira o resultado antes de colar outra tabela.

```text
Moeda;Gasto em USDT;Preço unitário em USDT;Câmbio;Data
BTC;500;350.000,00;5,30;2026-03-10
ETH;300;3200;;2026-05-02
PEPE;100;0,0000098
```

O cabeçalho, o câmbio e a data são opcionais. Para informar a data sem câmbio, deixe a coluna de câmbio vazia, como na linha do ETH. Use datas no formato `AAAA-MM-DD` e vírgula para decimais. O valor `5.500` é lido como 5500. Para informar taxa, cadastre a compra em **+ Nova Compra**.

## Preços, câmbio e cálculos

- A Binance fornece preços ao abrir a página, trocar de carteira ou usar os botões de atualização. Buscas automáticas preservam preços manuais. Uma busca solicitada pelo botão pode substituí-los. A interface indica o horário dos preços atualizados.
- O seletor alterna entre USDT e R$. A cotação USDT/BRL é global e mostra origem e horário quando disponíveis. O campo também aceita a cotação do dólar informada à mão.
- Em R$, o valor atual prioriza a cotação de hoje e pode usar o câmbio das compras como aproximação. Valores sem conversão aparecem como **—**. Ao selecionar R$ sem câmbio suficiente, o site pode voltar para USDT e explicar o motivo.
- Taxas de compra entram no preço médio (PM) e no break-even. Taxas de venda reduzem o valor recebido. O lucro realizado usa o PM atual da moeda, então uma compra nova pode recalcular vendas anteriores.

## Dados, backups e privacidade

- Compras e vendas ficam no `localStorage` do navegador. A página usa a Binance para consultas de preço e o Google Fonts para carregar fontes. Você pode preencher preços e câmbio manualmente.
- **Baixar backup** exporta todas as carteiras e configurações em JSON v4. **Carregar backup** aceita v3 e v4 e pede confirmação antes de substituir dados, indicando correções, descartes e inconsistências de saldo.
- **Exportar para CSV** exporta as compras e vendas da carteira ativa. Usa UTF-8 com BOM, ponto e vírgula e neutralização de fórmulas em campos de texto.
- Falhas de gravação exibem um aviso. Se houver dados problemáticos no armazenamento, o site tenta preservar o original e oferece **baixar cópia preservada** quando a cópia é criada.
- Alterações em outra aba do navegador atualizam os dados. A digitação é preservada quando a carteira ativa ainda existe.
- Guarde backups e gráficos com dados reais fora do repositório. O `.gitignore` ignora novos arquivos JSON, PNG e caches do Python.

O site usa HTML, CSS e JavaScript em um único arquivo, com tema escuro responsivo e escape do texto inserido na página.

## Gráficos e testes

O gerador Python lê o backup, cria PNGs e imprime um resumo em USDT. Os testes automatizados cobrem os cálculos em Python e a leitura dos backups. [Instalação e comandos](graficos-python/README.md)

## ⚠️ Aviso legal

Esta ferramenta foi desenvolvida para organização e controle pessoal, com fins informativos.

- **Sem recomendações:** os valores, cálculos e simulações exibidos não constituem recomendação de investimento, compra ou venda de criptoativos.
- **Não é cálculo de imposto:** o app não substitui a apuração oficial de ganho de capital nem a declaração de imposto de renda. Consulte um contador se necessário.
- **Precisão das cotações:** as cotações automáticas dependem da API pública da Binance e podem sofrer atrasos ou oscilações. Confirme sempre suas operações na sua corretora (*exchange*).
