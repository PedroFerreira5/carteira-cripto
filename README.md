# Carteira Cripto

Eu estava com dificuldade de acompanhar meus resultados em cripto: fazia várias compras em momentos diferentes, com preços diferentes, e ficava difícil saber se estava ganhando ou perdendo em cada uma. Criei essa ferramenta para resolver isso, controlando tanto os ativos em carteira quanto os lucros e prejuízos já realizados nas vendas.

🔗 **Acesse:** [https://pedroferreira5.github.io/carteira-cripto/](https://pedroferreira5.github.io/carteira-cripto/)

---

## 📌 O que faz

### 💼 Gestão de compras e carteira
- **Cadastro individual de compras:** informe o gasto em USDT, o preço pago e, opcionalmente, a taxa e a cotação do dólar (USD/BRL). A quantidade adquirida é calculada automaticamente.
- **Preço médio (PM):** calcula o preço médio ponderado por moeda, incorporando as taxas pagas no custo base do ativo.
- **Break-even:** mostra o valor unitário de venda necessário para empatar o investimento, já considerando as taxas.
- **Simulador de venda:** digite um preço hipotético e veja o valor a receber, o lucro ou prejuízo e o percentual de retorno antes de realizar a ordem.
- **Resultado por ordem:** custo, valor atual e resultado não realizado ($ e %) de cada compra e do consolidado da moeda.

### 💸 Vendas e histórico
- **Vendas parciais ou totais:** abate o saldo disponível e apura o **lucro/prejuízo realizado** usando o preço médio (PM) da moeda.
- **Histórico com filtro por mês:** tabela dedicada às vendas, com resultado do período selecionado. O lucro realizado é recalculado automaticamente se novas compras alterarem o PM.

### 💱 Cotações e câmbio
- **Alternância USDT / BRL:** troque toda a visualização entre dólar (USDT) e reais (R$).
- **Cotação do dólar informada por você:** defina a taxa USD/BRL de hoje para converter o valor de mercado das posições para reais. Cada compra e venda também pode guardar o câmbio do dia.
- **Preço atual via Binance:** busca os pares contra USDT na API pública da Binance ao abrir a página, por botão individual ou geral. Se a busca falhar, você pode preencher o preço manualmente.

### 🗂️ Organização e importação
- **Busca e ordenação:** filtre moedas pelo nome e ordene por ordem alfabética ou por maior valor investido.
- **Importação em massa:** cole várias compras direto do Excel ou Google Sheets.
- **Exportação CSV e backup JSON:** exporte o histórico em CSV ou faça um backup completo para restaurar em outro navegador.

---

## 📥 Modelo de tabela para importação em massa

Na aba **Importar Tabela**, cole suas compras neste formato (colunas separadas por TAB ou vírgula, uma compra por linha):

| Moeda | Usdt | Preco | Cambio | Data |
| :--- | :--- | :--- | :--- | :--- |
| BTC | 500 | 65000 | 5.30 | 2026-03-10 |
| ETH | 300 | 3200 | | 2026-05-02 |
| PEPE | 100 | 0.0000098 | | |

- **Moeda:** ticker do ativo (ex: BTC, ETH, PEPE).
- **Usdt:** valor total gasto em USDT.
- **Preco:** preço unitário da moeda, em USDT, na data da compra.
- **Cambio:** cotação USD/BRL na data da compra *(opcional)*.
- **Data:** formato AAAA-MM-DD *(opcional)*.

*Selecione as células na planilha (com ou sem cabeçalho) e cole direto na caixa de texto. A taxa não entra na importação em massa: se precisar dela, cadastre a compra manualmente.*

---

## 🔒 Armazenamento, privacidade e segurança

Os dados ficam **exclusivamente no seu navegador**, via `localStorage`. Não existe backend, servidor central ou envio das suas informações financeiras.

- **Privacidade:** nenhum dado da sua carteira é transmitido a terceiros. As únicas requisições externas são a consulta pública de preços à API da Binance e o carregamento das fontes do Google Fonts (a página continua funcionando com fontes padrão se estiver sem internet).
- **Uso offline:** você pode baixar o `index.html` e abri-lo direto no computador (os preços precisam ser preenchidos manualmente).
- **Portabilidade:** use **baixar backup** e **carregar backup** no rodapé para levar seus dados entre navegadores ou computadores.
- **Proteção contra XSS:** todo texto vindo do usuário (nome da moeda, busca, datas, mensagens de importação) é escapado antes de ser inserido na página.
- **Validação de dados:** o conteúdo do `localStorage` e dos arquivos de backup é validado e normalizado ao carregar. Registros inválidos são descartados em vez de quebrar a tela.
- **CSV seguro:** a exportação neutraliza textos que começam com `=`, `+`, `-` ou `@`, evitando injeção de fórmulas ao abrir no Excel.

---

## 🛠️ Tecnologias

- **HTML5 e CSS3:** layout responsivo com CSS Grid, Flexbox, variáveis CSS e tema escuro.
- **JavaScript puro (ES6+):** sem frameworks nem dependências, em arquivo único, com IIFE para isolar o escopo.
- **API REST (Binance):** requisições assíncronas (`fetch` / `async/await`) para os preços.
- **Arquivos:** geração e leitura de JSON para backup e exportação de CSV com UTF-8 BOM e separador compatível com o Excel em português.

---

## ▶️ Como rodar localmente

Não precisa de servidor, Node.js nem build:

1. Baixe o repositório ou salve o arquivo `index.html`.
2. Dê dois cliques no arquivo para abrir em qualquer navegador moderno.

---

## 🧠 Decisões de projeto e limitações

- **Custo da venda usa o PM atual da moeda**, e não um método por lote (como FIFO). Por isso, cadastrar uma compra nova altera retroativamente o lucro realizado das vendas anteriores. É uma escolha deliberada de simplicidade e está explicada na própria tela.
- **Taxas de compra entram no custo base**, ou seja, no PM e no break-even. Taxas de venda são descontadas do valor recebido.
- **Preço atual por moeda:** hoje o preço atual é replicado dentro de cada compra. Um mapa único por moeda seria mais enxuto.
- **Sem testes automatizados** para a lógica de cálculo (PM, lucro realizado e não realizado). É o principal ponto a evoluir.
- **Câmbio:** quando uma compra ou venda não tem cotação informada, o app usa a cotação de hoje e, na falta dela, o câmbio médio das compras da moeda como aproximação.

### Próximos passos
- Testes unitários para as funções de cálculo.
- Preço atual centralizado por moeda.
- Gráficos de evolução da carteira.

---

## ⚠️ Aviso legal

Esta ferramenta foi desenvolvida para organização e controle pessoal, com fins informativos.

- **Sem recomendações:** os valores, cálculos e simulações exibidos não constituem recomendação de investimento, compra ou venda de criptoativos.
- **Não é cálculo de imposto:** o app não substitui a apuração oficial de ganho de capital nem a declaração de imposto de renda. Consulte um contador se necessário.
- **Precisão das cotações:** as cotações automáticas dependem da API pública da Binance e podem sofrer atrasos ou oscilações. Confirme sempre suas operações na sua corretora (*exchange*).
