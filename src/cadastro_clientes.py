"""
Módulo de Cadastro de Clientes
Chatbot de Cobrança via WhatsApp
"""
import re


class ClienteJaCadastradoError(Exception):
    """Levantada quando o CPF já existe no banco."""


class DadosInvalidosError(Exception):
    """Levantada quando os dados do cliente são inválidos."""


class CadastroClientes:
    def __init__(self):
        self._clientes: dict[str, dict] = {}

    @staticmethod
    def _validar_nome(nome: str) -> None:
        if not nome or not nome.strip():
            raise DadosInvalidosError("Nome é obrigatório.")

    @staticmethod
    def _validar_telefone(telefone: str) -> None:
        padrao = r"^(\+?55)?(\(?\d{2}\)?[\s-]?)(\d{4,5}[\s-]?\d{4})$"
        if not re.match(padrao, telefone.strip()):
            raise DadosInvalidosError(
                f"Telefone '{telefone}' não está em formato válido."
            )

    @staticmethod
    def _validar_cpf_formato(cpf: str) -> None:
        apenas_digitos = re.sub(r"\D", "", cpf)
        if len(apenas_digitos) != 11:
            raise DadosInvalidosError(f"CPF '{cpf}' inválido (deve ter 11 dígitos).")

    def cadastrar(self, nome: str, telefone: str, cpf: str) -> dict:
        self._validar_nome(nome)
        self._validar_telefone(telefone)
        self._validar_cpf_formato(cpf)

        cpf_normalizado = re.sub(r"\D", "", cpf)
        if cpf_normalizado in self._clientes:
            raise ClienteJaCadastradoError(
                f"Cliente com CPF {cpf} já cadastrado."
            )

        cliente = {
            "nome": nome.strip(),
            "telefone": telefone.strip(),
            "cpf": cpf_normalizado,
        }
        self._clientes[cpf_normalizado] = cliente
        return cliente

    def buscar_por_cpf(self, cpf: str) -> dict | None:
        cpf_normalizado = re.sub(r"\D", "", cpf)
        return self._clientes.get(cpf_normalizado)

    def total_clientes(self) -> int:
        return len(self._clientes)