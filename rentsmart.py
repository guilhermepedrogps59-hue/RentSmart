"""RentSmart - orçamentos de locação para a R.M Imóveis (Python 3.10+)."""
from __future__ import annotations

import csv
from dataclasses import dataclass
from decimal import Decimal, ROUND_HALF_UP
from pathlib import Path

CENTAVO = Decimal('0.01')
TAXA_CONTRATUAL = Decimal('2000.00')


def moeda(valor: Decimal) -> str:
    s = f'{valor.quantize(CENTAVO, rounding=ROUND_HALF_UP):,.2f}'
    return 'R$ ' + s.replace(',', '#').replace('.', ',').replace('#', '.')


def arredondar(valor: Decimal) -> Decimal:
    return valor.quantize(CENTAVO, rounding=ROUND_HALF_UP)


@dataclass(frozen=True)
class Detalhe:
    base: Decimal
    quartos: Decimal
    estacionamento: Decimal
    desconto: Decimal

    @property
    def subtotal(self) -> Decimal:
        return self.base + self.quartos + self.estacionamento

    @property
    def mensal(self) -> Decimal:
        return arredondar(self.subtotal - self.desconto)


class Imovel:
    """Abstração do imóvel: cada tipo calcula sua própria composição mensal."""
    nome = 'Imóvel'

    def detalhar(self) -> Detalhe:
        raise NotImplementedError


@dataclass(frozen=True)
class Apartamento(Imovel):
    quartos: int
    garagem: bool
    tem_criancas: bool
    nome = 'Apartamento'

    def __post_init__(self):
        if type(self.quartos) is not int or self.quartos not in (1, 2):
            raise ValueError('Apartamento deve possuir 1 ou 2 quartos.')
        if type(self.garagem) is not bool or type(self.tem_criancas) is not bool:
            raise ValueError('Garagem e presença de crianças devem ser booleanos.')

    def detalhar(self) -> Detalhe:
        base = Decimal('700.00')
        quartos = Decimal('200.00') if self.quartos == 2 else Decimal('0.00')
        estacionamento = Decimal('300.00') if self.garagem else Decimal('0.00')
        subtotal = base + quartos + estacionamento
        desconto = arredondar(subtotal * Decimal('0.05')) if not self.tem_criancas else Decimal('0.00')
        return Detalhe(base, quartos, estacionamento, desconto)


@dataclass(frozen=True)
class Casa(Imovel):
    quartos: int
    garagem: bool
    nome = 'Casa'

    def __post_init__(self):
        if type(self.quartos) is not int or self.quartos not in (1, 2):
            raise ValueError('Casa deve possuir 1 ou 2 quartos.')
        if type(self.garagem) is not bool:
            raise ValueError('Garagem deve ser booleana.')

    def detalhar(self) -> Detalhe:
        return Detalhe(Decimal('900.00'),
                       Decimal('250.00') if self.quartos == 2 else Decimal('0.00'),
                       Decimal('300.00') if self.garagem else Decimal('0.00'),
                       Decimal('0.00'))


@dataclass(frozen=True)
class Estudio(Imovel):
    vagas: int
    nome = 'Estúdio'

    def __post_init__(self):
        # O enunciado define somente pacote de 2 vagas (ou mais), não uma vaga avulsa.
        if type(self.vagas) is not int or (self.vagas != 0 and self.vagas < 2):
            raise ValueError('Estúdio aceita 0 vagas ou pacote de 2 ou mais vagas.')

    def detalhar(self) -> Detalhe:
        estacionamento = (Decimal('0.00') if self.vagas == 0 else
                          Decimal('250.00') + Decimal('60.00') * (self.vagas - 2))
        return Detalhe(Decimal('1200.00'), Decimal('0.00'), estacionamento, Decimal('0.00'))


@dataclass(frozen=True)
class Contrato:
    imovel: Imovel
    parcelas: int

    def __post_init__(self):
        if not isinstance(self.imovel, Imovel):
            raise TypeError('É necessário informar um imóvel válido.')
        if type(self.parcelas) is not int or not 1 <= self.parcelas <= 5:
            raise ValueError('A taxa contratual deve ser paga em 1 a 5 parcelas.')

    @property
    def aluguel_mensal(self) -> Decimal:
        return self.imovel.detalhar().mensal

    def valor_parcela(self, numero: int) -> Decimal:
        """Distribui centavos residuais para somar exatamente R$ 2.000,00."""
        if type(numero) is not int or not 1 <= numero <= self.parcelas:
            raise ValueError('Número de parcela inválido.')
        centavos = 200000
        quociente, resto = divmod(centavos, self.parcelas)
        return Decimal(quociente + (1 if numero <= resto else 0)) / 100

    def projecao(self) -> list[dict]:
        linhas = []
        for mes in range(1, 13):
            taxa = self.valor_parcela(mes) if mes <= self.parcelas else Decimal('0.00')
            linhas.append({'mes': mes, 'aluguel': self.aluguel_mensal,
                           'taxa_contratual': taxa, 'total': self.aluguel_mensal + taxa})
        return linhas

    def exportar_csv(self, destino: str | Path = 'projecao_12_meses.csv') -> Path:
        caminho = Path(destino)
        caminho.parent.mkdir(parents=True, exist_ok=True)
        with caminho.open('w', newline='', encoding='utf-8-sig') as arquivo:
            escritor = csv.writer(arquivo, delimiter=';')
            escritor.writerow(['Mês', 'Aluguel mensal (R$)', 'Parcela taxa contratual (R$)', 'Total previsto (R$)'])
            for linha in self.projecao():
                escritor.writerow([linha['mes'], f"{linha['aluguel']:.2f}",
                                   f"{linha['taxa_contratual']:.2f}", f"{linha['total']:.2f}"])
        return caminho


def ler_opcao(pergunta: str, validos: tuple[int, ...]) -> int:
    while True:
        try:
            opcao = int(input(pergunta).strip())
            if opcao in validos:
                return opcao
        except (ValueError, EOFError):
            pass
        print('Entrada inválida. Escolha uma das opções:', ', '.join(map(str, validos)))


def ler_sim_nao(pergunta: str) -> bool:
    while True:
        try:
            resposta = input(pergunta + ' (s/n): ').strip().lower()
        except EOFError:
            resposta = ''
        if resposta in ('s', 'sim'):
            return True
        if resposta in ('n', 'não', 'nao'):
            return False
        print('Entrada inválida. Responda s ou n.')


def ler_vagas() -> int:
    while True:
        try:
            n = int(input('Quantas vagas para o estúdio? (0 ou 2 ou mais): ').strip())
            if n == 0 or n >= 2:
                return n
        except (ValueError, EOFError):
            pass
        print('Informe 0 (sem estacionamento) ou 2 ou mais (pacote inicial).')


def montar_imovel() -> Imovel:
    tipo = ler_opcao('Tipo: 1-Apartamento, 2-Casa, 3-Estúdio: ', (1, 2, 3))
    if tipo == 3:
        return Estudio(ler_vagas())
    quartos = ler_opcao('Quartos (1 ou 2): ', (1, 2))
    garagem = ler_sim_nao('Deseja 1 vaga de garagem?')
    if tipo == 1:
        criancas = ler_sim_nao('Há crianças no imóvel?')
        return Apartamento(quartos, garagem, criancas)
    return Casa(quartos, garagem)


def apresentar(contrato: Contrato) -> None:
    d = contrato.imovel.detalhar()
    print('\n' + '=' * 58)
    print('RENTSMART | ORÇAMENTO DE LOCAÇÃO - R.M IMÓVEIS')
    print('=' * 58)
    print('Tipo:', contrato.imovel.nome)
    print('Aluguel-base:             ', moeda(d.base))
    print('Adicional de quartos:     ', moeda(d.quartos))
    print('Adicional estacionamento: ', moeda(d.estacionamento))
    print('Subtotal:                 ', moeda(d.subtotal))
    print('Desconto:                 ', moeda(d.desconto))
    print('ALUGUEL MENSAL:           ', moeda(d.mensal))
    print('-' * 58)
    print('TAXA CONTRATUAL (separada):', moeda(TAXA_CONTRATUAL))
    print('Parcelamento:', contrato.parcelas, 'parcela(s)')
    print('Valores das parcelas:', ', '.join(moeda(contrato.valor_parcela(i)) for i in range(1, contrato.parcelas + 1)))
    print('-' * 58)
    print('MÊS | ALUGUEL         | TAXA CONTRATO    | TOTAL PREVISTO')
    for linha in contrato.projecao():
        print(f"{linha['mes']:>3} | {moeda(linha['aluguel']):<15} | {moeda(linha['taxa_contratual']):<16} | {moeda(linha['total'])}")
    print('=' * 58)


def main() -> None:
    print('Bem-vindo ao RentSmart!')
    imovel = montar_imovel()
    parcelas = ler_opcao('Parcelas da taxa contratual (1 a 5): ', (1, 2, 3, 4, 5))
    contrato = Contrato(imovel, parcelas)
    apresentar(contrato)
    caminho = contrato.exportar_csv()
    print('CSV gerado:', caminho.resolve())


if __name__ == '__main__':
    main()
