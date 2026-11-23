
[README.md](https://github.com/user-attachments/files/35300729/README.md)
# RentSmart — Sistema de Orçamento de Locação

Projeto acadêmico para a R.M Imóveis, desenvolvido em Python com orientação a objetos.

## Requisitos
- Python 3.10 ou superior. **Não precisa instalar bibliotecas externas.**

## Executar
1. Abra o terminal na pasta `RentSmart`.
2. Execute `python rentsmart.py` (no Windows também pode usar `py rentsmart.py`).
3. Escolha o imóvel, número de quartos e estacionamento quando aplicável, informe a presença de crianças apenas para apartamento e escolha 1 a 5 parcelas.
4. O programa mostra a composição do orçamento e gera `projecao_12_meses.csv` na mesma pasta. O CSV usa `;` como separador e UTF-8 com BOM para facilitar abertura no Excel brasileiro.

## Executar os testes
`python -m unittest -v`

## Regras usadas
- Apartamento: R$ 700 (1 quarto); segundo quarto +R$ 200; garagem +R$ 300; sem crianças: desconto de 5% no subtotal incluindo adicionais.
- Casa: R$ 900 (1 quarto); segundo quarto +R$ 250; garagem +R$ 300; sem desconto.
- Estúdio: R$ 1.200; sem estacionamento = R$ 0; pacote inicial de 2 vagas = R$ 250; cada vaga além de 2 = R$ 60.
- Taxa contratual: R$ 2.000, separada do aluguel e distribuída em 1 a 5 parcelas nos primeiros meses; o CSV mostra aluguel, parcela e total por mês por 12 meses.
- **Premissas de interpretação:** para estúdio, o estacionamento é opcional; se contratado, começa em 2 vagas (uma vaga isolada não foi tarifada no enunciado). A taxa contratual é paga em parcelas mensais consecutivas a partir do primeiro mês, sem juros. Não há reajuste de aluguel no primeiro ano porque o enunciado não especifica índice de reajuste. Essas premissas estão documentadas no relatório teórico.

## Organização
- `rentsmart.py`: classes `Imovel`, `Apartamento`, `Casa`, `Estudio`, `Detalhe` e `Contrato`; validação de dados, interface de terminal e exportação CSV.
- `test_rentsmart.py`: testes automatizados de regras, validação, projeção e CSV.
- `projecao_exemplo.csv`: CSV de demonstração.
- `Relatorio_Teorico_RentSmart.pdf`: análise, entradas/processos/saídas, fluxograma e fundamentação.
- `Roteiro_Video_Pitch.md`: proposta de fala e demonstração em até 4 minutos.

## Publicação e entrega
1. Crie um repositório no GitHub e envie `rentsmart.py`, `test_rentsmart.py`, `README.md`, `projecao_exemplo.csv` e o relatório PDF. **Não invente um link:** use a URL verdadeira do repositório criado por você.
2. Grave a apresentação mostrando o fluxograma, o código, a execução e o CSV. Publique o vídeo como não listado e entregue o link real.
3. Confira que os dois links estão acessíveis antes da entrega.
