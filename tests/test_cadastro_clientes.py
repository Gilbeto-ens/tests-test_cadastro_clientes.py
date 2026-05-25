"""
Testes Unitários – Funcionalidade: Cadastro de Clientes
Chatbot de Cobrança via WhatsApp

Casos cobertos:
  TC 1.1 (Positivo / Unitário) – cadastrar cliente com dados válidos
  TC 1.2 (Negativo / Integração simulada) – bloquear duplicidade por CPF
"""

import sys
import os
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from src.cadastro_clientes import (
    CadastroClientes,
    ClienteJaCadastradoError,
    DadosInvalidosError,
)


class TestCadastroClientePositivo(unittest.TestCase):
    """TC 1.1 – Cadastro com dados válidos."""

    def setUp(self):
        self.cadastro = CadastroClientes()

    def test_cadastro_com_dados_validos_retorna_cliente(self):
        """TC 1.1: Cadastro realizado com nome, telefone e CPF válidos."""
        cliente = self.cadastro.cadastrar(
            nome="Maria Oliveira",
            telefone="(11) 91234-5678",
            cpf="123.456.789-09",
        )
        self.assertEqual(cliente["nome"], "Maria Oliveira")
        self.assertEqual(cliente["cpf"], "12345678909")

    def test_cadastro_incrementa_total_de_clientes(self):
        """TC 1.1 (variação): total de clientes deve aumentar após cadastro."""
        self.assertEqual(self.cadastro.total_clientes(), 0)
        self.cadastro.cadastrar("João Silva", "11987654321", "987.654.321-00")
        self.assertEqual(self.cadastro.total_clientes(), 1)

    def test_cliente_cadastrado_pode_ser_recuperado_por_cpf(self):
        """TC 1.1 (variação): cliente deve ser localizável após o cadastro."""
        self.cadastro.cadastrar("Ana Lima", "(21) 98765-4321", "111.222.333-44")
        encontrado = self.cadastro.buscar_por_cpf("111.222.333-44")
        self.assertIsNotNone(encontrado)
        self.assertEqual(encontrado["nome"], "Ana Lima")

    def test_telefone_no_formato_internacional_e_aceito(self):
        """TC 1.1 (variação): telefone com DDI +55 deve ser válido."""
        cliente = self.cadastro.cadastrar(
            nome="Carlos Mota",
            telefone="+5511912345678",
            cpf="555.666.777-88",
        )
        self.assertEqual(cliente["nome"], "Carlos Mota")

    def test_nome_com_espacos_nas_bordas_e_normalizado(self):
        """TC 1.1 (variação): nome deve ser salvo sem espaços extras."""
        cliente = self.cadastro.cadastrar(
            nome="  Fernanda Costa  ",
            telefone="11911112222",
            cpf="000.111.222-33",
        )
        self.assertEqual(cliente["nome"], "Fernanda Costa")

    def test_nome_vazio_levanta_erro(self):
        """Regra: Nome é obrigatório."""
        with self.assertRaises(DadosInvalidosError):
            self.cadastro.cadastrar("", "11911112222", "000.111.222-33")

    def test_nome_apenas_espacos_levanta_erro(self):
        """Regra: Nome apenas com espaços também é inválido."""
        with self.assertRaises(DadosInvalidosError):
            self.cadastro.cadastrar("   ", "11911112222", "000.111.222-33")

    def test_telefone_invalido_levanta_erro(self):
        """Regra: Telefone deve estar em formato válido."""
        with self.assertRaises(DadosInvalidosError):
            self.cadastro.cadastrar("Pedro Alves", "ABCDE-FGHI", "000.111.222-33")

    def test_cpf_com_menos_de_11_digitos_levanta_erro(self):
        """Regra: CPF deve ter 11 dígitos."""
        with self.assertRaises(DadosInvalidosError):
            self.cadastro.cadastrar("Teste", "11911112222", "123.456")


class TestCadastroClienteDuplicidade(unittest.TestCase):
    """TC 1.2 – Bloqueio de duplicidade por CPF."""

    def setUp(self):
        self.cadastro = CadastroClientes()
        self.cadastro.cadastrar(
            nome="Luiz Pereira",
            telefone="(31) 91234-5678",
            cpf="444.555.666-77",
        )

    def test_cpf_duplicado_levanta_erro(self):
        """TC 1.2: Sistema deve bloquear segundo cadastro com mesmo CPF."""
        with self.assertRaises(ClienteJaCadastradoError):
            self.cadastro.cadastrar(
                nome="Outro Nome",
                telefone="(31) 98888-7777",
                cpf="444.555.666-77",
            )

    def test_cpf_duplicado_com_formatacao_diferente_levanta_erro(self):
        """TC 1.2 (variação): CPF sem máscara deve ser tratado igual ao com máscara."""
        with self.assertRaises(ClienteJaCadastradoError):
            self.cadastro.cadastrar(
                nome="Clone",
                telefone="31912345678",
                cpf="44455566677",
            )

    def test_cpf_duplicado_nao_sobrescreve_dados_originais(self):
        """TC 1.2 (variação): dados do primeiro cadastro devem permanecer intactos."""
        try:
            self.cadastro.cadastrar(
                nome="Invasor",
                telefone="31988887777",
                cpf="444.555.666-77",
            )
        except ClienteJaCadastradoError:
            pass

        original = self.cadastro.buscar_por_cpf("444.555.666-77")
        self.assertEqual(original["nome"], "Luiz Pereira")

    def test_cpfs_diferentes_permitem_dois_cadastros(self):
        """TC 1.2 (contraponto): CPFs distintos não devem gerar conflito."""
        self.cadastro.cadastrar(
            nome="Novo Cliente",
            telefone="11911112222",
            cpf="111.222.333-44",
        )
        self.assertEqual(self.cadastro.total_clientes(), 2)


if __name__ == "__main__":
    unittest.main(verbosity=2)