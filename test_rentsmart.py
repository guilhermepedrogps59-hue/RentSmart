"""Execute: python -m unittest -v"""
import csv
import tempfile
import unittest
from decimal import Decimal
from pathlib import Path
from rentsmart import Apartamento, Casa, Estudio, Contrato


class TesteRentSmart(unittest.TestCase):
    def test_apartamento_1_quarto_sem_adicionais(self):
        self.assertEqual(Apartamento(1, False, True).detalhar().mensal, Decimal('700.00'))

    def test_apartamento_desconto_apos_adicionais(self):
        d = Apartamento(2, True, False).detalhar()
        self.assertEqual(d.subtotal, Decimal('1200.00'))
        self.assertEqual(d.desconto, Decimal('60.00'))
        self.assertEqual(d.mensal, Decimal('1140.00'))

    def test_casa_com_adicionais(self):
        self.assertEqual(Casa(2, True).detalhar().mensal, Decimal('1450.00'))

    def test_estudio_sem_vagas(self):
        self.assertEqual(Estudio(0).detalhar().mensal, Decimal('1200.00'))

    def test_estudio_pacote_duas_vagas(self):
        self.assertEqual(Estudio(2).detalhar().mensal, Decimal('1450.00'))

    def test_estudio_quatro_vagas(self):
        self.assertEqual(Estudio(4).detalhar().mensal, Decimal('1570.00'))

    def test_rejeita_entradas_incorretas(self):
        for classe, args in ((Apartamento, (3, True, True)), (Casa, (0, False)),
                             (Estudio, (1,)), (Estudio, (-1,))):
            with self.subTest(classe=classe, args=args), self.assertRaises(ValueError):
                classe(*args)
        for p in (0, 6, 1.5, True):
            with self.subTest(parcelas=p), self.assertRaises(ValueError):
                Contrato(Casa(1, False), p)

    def test_taxa_integral_12_meses(self):
        for parcelas in range(1, 6):
            c = Contrato(Apartamento(1, False, True), parcelas)
            linhas = c.projecao()
            self.assertEqual(len(linhas), 12)
            self.assertEqual(sum((x['taxa_contratual'] for x in linhas), Decimal(0)), Decimal('2000.00'))
            self.assertEqual(sum((x['total'] for x in linhas), Decimal(0)), Decimal('10400.00'))
            self.assertTrue(all(x['taxa_contratual'] == 0 for x in linhas[parcelas:]))

    def test_exportacao_csv(self):
        with tempfile.TemporaryDirectory() as pasta:
            arquivo = Contrato(Estudio(3), 3).exportar_csv(Path(pasta) / 'relatorio.csv')
            with arquivo.open(encoding='utf-8-sig', newline='') as f:
                linhas = list(csv.reader(f, delimiter=';'))
            self.assertEqual(len(linhas), 13)
            self.assertEqual(linhas[1][0], '1')
            self.assertEqual(linhas[1][1], '1510.00')
            self.assertEqual(linhas[-1][2], '0.00')


if __name__ == '__main__':
    unittest.main()
