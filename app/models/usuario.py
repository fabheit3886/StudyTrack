"""Entidade de usuário do StudyTrack."""

import re

from exceptions.erros import ValidationError
from app.models.validacao import identificador_positivo, texto_obrigatorio


class Usuario:
    """Representa uma conta, mantendo seus dados encapsulados."""

    def __init__(self, id_usuario: int, nome_usuario: str, email: str, senha: str) -> None:
        self._id_usuario = identificador_positivo(id_usuario, "ID do usuário")
        self.nome_usuario = nome_usuario
        self.email = email
        self.senha = senha

    @property
    def id_usuario(self) -> int:
        """Identificador da conta."""
        return self._id_usuario

    @property
    def nome_usuario(self) -> str:
        """Nome de exibição do usuário."""
        return self._nome_usuario

    @nome_usuario.setter
    def nome_usuario(self, valor: str) -> None:
        self._nome_usuario = texto_obrigatorio(valor, "Nome", 100)

    @property
    def email(self) -> str:
        """E-mail normalizado da conta."""
        return self._email

    @email.setter
    def email(self, valor: str) -> None:
        email = texto_obrigatorio(valor, "E-mail", 150).lower()
        if not re.fullmatch(r"[^\s@]+@[^\s@]+\.[^\s@]+", email):
            raise ValidationError("Informe um e-mail válido.")
        self._email = email

    @property
    def senha(self) -> str:
        """Hash da senha; a senha em texto puro não é armazenada."""
        return self._senha

    @senha.setter
    def senha(self, valor: str) -> None:
        self._senha = texto_obrigatorio(valor, "Senha", 255)

    @property
    def perfil(self) -> str:
        """Rótulo polimórfico do tipo de usuário."""
        return "Usuário"

    def resumo(self) -> str:
        """Retorna uma apresentação segura, sem expor a senha."""
        return f"{self.nome_usuario} ({self.email}) - {self.perfil}"
