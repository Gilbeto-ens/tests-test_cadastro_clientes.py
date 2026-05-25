"""
Testes Unitários – Funcionalidade: Registro de Pagamentos
Chatbot de Cobrança via WhatsApp

Casos cobertos:
  TC 3.1 (Positivo / E2E) – pagamento confirmado altera status para quitado
  TC 3.2 (Negativo / Unitário) – valor zero ou negativo é rejeitado
"""

import sys
import os
import unittest
from decimal import Decimal

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from src.registro_pagamentos import (
    RegistroPagamentos,
    PagamentoInvalidoError,
    ClienteNaoEncontradoError,
)


class TestPagamentoPositivo(unittest.TestCase):
    """TC 3.1 – Pagamento confirmado: status alterado para 'quitado'."""

    CPF = "12345678900"

    def setUp(self):
        self.registro = RegistroPagamentos()
        self.registro.registrar_divida(self.CPF, 500.00)

    def test_pagamento_integral_altera_status_para_quitado(self):
        """TC 3.1: Ao pagar o valor total, status deve ser 'quitado'."""
        resultado = self.registro.confirmar_pagamento(self.CPF, 500.00)
        self.assertEqual(resultado["status"], "quitado")

    def test_pagamento_integral_zera_valor_restante(self):
        """TC 3.1 (variação): valor_restante deve ser 0 após quitar."""
        resultado = self.registro.confirmar_pagamento(self.CPF, 500.00)
        self.assertEqual(resultado["valor_restante"], 0.0)

    def test_pagamento_registrado_no_historico(self):
        """TC 3.1 (variação): histórico deve conter data e valor do pagamento."""
        resultado = self.registro.confirmar_pagamento(self.CPF, 500.00)
        self.assertEqual(len(resultado["historico"]), 1)
        self.assertIn("data", resultado["historico"][0])
        self.assertIn("valor", resultado["historico"][0])
        self.assertEqual(resultado["historico"][0]["valor"], 500.00)

    def test_cliente_quitado_sai_da_lista_de_cobranca(self):
        """TC 3.1 (variação): cliente quitado não deve aparecer na cobrança."""
        self.registro.confirmar_pagamento(self.CPF, 500.00)
        self.assertFalse(self.registro.esta_na_lista_cobranca(self.CPF))

    def test_pagamento_parcial_mantem_status_pendente(self):
        """TC 3.1 (contraponto): pagamento parcial não quita a dívida."""
        resultado = self.registro.confirmar_pagamento(self.CPF, 200.00)
        self.assertEqual(resultado["status"], "pendente")
        self.assertEqual(resultado["valor_restante"], 300.00)

    def test_multiplos_pagamentos_acumulam_historico(self):
        """TC 3.1 (variação): cada parcela gera uma entrada no histórico."""
        self.registro.confirmar_pagamento(self.CPF, 250.00)
        resultado = self.registro.confirmar_pagamento(self.CPF, 250.00)
        self.assertEqual(len(resultado["historico"]), 2)
        self.assertEqual(resultado["status"], "quitado")

    def test_pagamento_com_decimal_preciso_e_aceito(self):
        """TC 3.1 (variação): valores decimais devem ser processados corretamente."""
        self.registro.registrar_divida("99988877766", Decimal("199.99"))
        resultado = self.registro.confirmar_pagamento("99988877766", Decimal("199.99"))
        self.assertEqual(resultado["status"], "quitado")


class TestPagamentoNegativo(unittest.TestCase):
    """TC 3.2 – Rejeição de valor zero ou negativo."""

    CPF = "98765432100"

    def setUp(self):
        self.registro = RegistroPagamentos()
        self.registro.registrar_divida(self.CPF, 300.00)

    def test_valor_zero_levanta_erro(self):
        """TC 3.2: Pagamento com valor zero deve ser rejeitado."""
        with self.assertRaises(PagamentoInvalidoError):
            self.registro.confirmar_pagamento(self.CPF, 0)

    def test_valor_negativo_levanta_erro(self):
        """TC 3.2 (variação): Pagamento com valor negativo deve ser rejeitado."""
        with self.assertRaises(PagamentoInvalidoError):
            self.registro.confirmar_pagamento(self.CPF, -50.00)

    def test_valor_zero_decimal_levanta_erro(self):
        """TC 3.2 (variação): Decimal('0.00') também deve ser rejeitado."""
        with self.assertRaises(PagamentoInvalidoError):
            self.registro.confirmar_pagamento(self.CPF, Decimal("0.00"))

    def test_valor_invalido_nao_altera_historico(self):
        """TC 3.2 (variação): tentativa inválida não deve poluir o histórico."""
        try:
            self.registro.confirmar_pagamento(self.CPF, 0)
        except PagamentoInvalidoError:
            pass
        self.assertEqual(self.registro.status_cliente(self.CPF), "pendente")

    def test_cpf_inexistente_levanta_erro(self):
        """Regra auxiliar: CPF não cadastrado deve levantar erro específico."""
        with self.assertRaises(ClienteNaoEncontradoError):
            self.registro.confirmar_pagamento("00000000000", 100.00)

    def test_mensagem_de_erro_menciona_valor_invalido(self):
        """TC 3.2 (variação): mensagem de erro deve ser informativa."""
        with self.assertRaises(PagamentoInvalidoError) as ctx:
            self.registro.confirmar_pagamento(self.CPF, -10)
        self.assertIn("-10", str(ctx.exception))


if __name__ == "__main__":
    unittest.main(verbosity=2)