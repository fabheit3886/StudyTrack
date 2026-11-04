"""Perfil acadêmico que especializa a entidade Usuario."""

from app.models.usuario import Usuario
from app.models.validacao import identificador_positivo, texto_obrigatorio


class Aluno(Usuario):
    """Conta de usuário com matrícula, turma e curso."""

    def __init__(
        self,
        id_aluno: int,
        id_usuario: int,
        nome_usuario: str,
        email: str,
        senha: str,
        matricula: str,
        turma: str,
        curso: str,
    ) -> None:
        super().__init__(id_usuario, nome_usuario, email, senha)
        self._id_aluno = identificador_positivo(id_aluno, "ID do aluno")
        self.matricula = matricula
        self.turma = turma
        self.curso = curso

    @property
    def id_aluno(self) -> int:
        """Identificador do perfil acadêmico."""
        return self._id_aluno

    @property
    def matricula(self) -> str:
        """Matrícula escolar única."""
        return self._matricula

    @matricula.setter
    def matricula(self, valor: str) -> None:
        self._matricula = texto_obrigatorio(valor, "Matrícula", 30)

    @property
    def turma(self) -> str:
        """Turma do aluno."""
        return self._turma

    @turma.setter
    def turma(self, valor: str) -> None:
        self._turma = texto_obrigatorio(valor, "Turma", 30)

    @property
    def curso(self) -> str:
        """Curso do aluno."""
        return self._curso

    @curso.setter
    def curso(self, valor: str) -> None:
        self._curso = texto_obrigatorio(valor, "Curso", 100)

    @property
    def perfil(self) -> str:
        """Especializa o perfil retornado por Usuario."""
        return "Aluno"

    def resumo(self) -> str:
        """Inclui dados acadêmicos no resumo do usuário."""
        return f"{super().resumo()} | Matrícula: {self.matricula} | Curso: {self.curso}"
