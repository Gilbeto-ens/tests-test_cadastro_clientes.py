"""
Módulo de Registro de Pagamentos
Chatbot de Cobrança via WhatsApp
"""
from datetime import datetime
from decimal import Decimal


class PagamentoInvalidoError(Exception):
    """Levantada quando o valor do pagamento é inválido (zero ou negativo)."""


class ClienteNaoEncontradoError(Exception):
    """Levantada quando o CPF não existe no sistema de cobranças."""


class RegistroPagamentos:
    def __init__(self):
        self._contas: dict[str, dict] = {}

    def registrar_divida(self, cpf: str, valor: float | Decimal) -> None:
        self._contas[cpf] = {
            "valor_devido": Decimal(str(valor)),
            "status": "pendente",
            "historico": [],
        }

    def confirmar_pagamento(self, cpf: str, valor: float | Decimal) -> dict:
        valor_decimal = Decimal(str(valor))

        if valor_decimal <= 0:
            raise PagamentoInvalidoError(
                f"Valor de pagamento inválido: {valor}. Deve ser maior que zero."
            )

        if cpf not in self._contas:
            raise ClienteNaoEncontradoError(f"CPF {cpf} não encontrado nas cobranças.")

        conta = self._contas[cpf]
        entrada_historico = {
            "data": datetime.now().isoformat(timespec="seconds"),
            "valor": float(valor_decimal),
        }
        conta["historico"].append(entrada_historico)
        conta["valor_devido"] -= valor_decimal

        if conta["valor_devido"] <= 0:
            conta["status"] = "quitado"
            conta["valor_devido"] = Decimal("0")

        return {
            "cpf": cpf,
            "status": conta["status"],
            "valor_restante": float(conta["valor_devido"]),
            "historico": conta["historico"],
        }

    def status_cliente(self, cpf: str) -> str | None:
        conta = self._contas.get(cpf)
        return conta["status"] if conta else None

    def esta_na_lista_cobranca(self, cpf: str) -> bool:
        conta = self._contas.get(cpf)
        return conta is not None and conta["status"] == "pendente"