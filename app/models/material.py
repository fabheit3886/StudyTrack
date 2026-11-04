"""Material do catálogo escolar."""

from exceptions.erros import ValidationError
from app.models.validacao import identificador_positivo, texto_obrigatorio


class Material:
    """Recurso de apoio que pode ser associado a uma atividade."""

    def __init__(
        self,
        id_material: int,
        nome_material: str,
        tipo: str,
        descricao_material: str = "",
        link: str = "",
        categoria: str = "",
        autor: str = "",
    ) -> None:
        self._id_material = identificador_positivo(id_material, "ID do material")
        self.nome_material = nome_material
        self.tipo = tipo
        self.descricao_material = descricao_material
        self.link = link
        self.categoria = categoria
        self.autor = autor

    @property
    def id_material(self) -> int:
        """Identificador do recurso."""
        return self._id_material

    @property
    def nome_material(self) -> str:
        """Título ou nome do material."""
        return self._nome_material

    @nome_material.setter
    def nome_material(self, valor: str) -> None:
        self._nome_material = texto_obrigatorio(valor, "Nome do material", 150)

    @property
    def tipo(self) -> str:
        """Tipo do recurso, como livro, artigo ou apostila."""
        return self._tipo

    @tipo.setter
    def tipo(self, valor: str) -> None:
        self._tipo = texto_obrigatorio(valor, "Tipo", 50)

    @property
    def descricao_material(self) -> str:
        """Descrição opcional do material."""
        return self._descricao_material

    @descricao_material.setter
    def descricao_material(self, valor: str) -> None:
        if not isinstance(valor, str):
            raise ValidationError("A descrição do material deve ser texto.")
        self._descricao_material = valor.strip()

    @property
    def link(self) -> str:
        """Link opcional para consulta do recurso."""
        return self._link

    @link.setter
    def link(self, valor: str) -> None:
        if not isinstance(valor, str) or len(valor) > 500:
            raise ValidationError("O link deve ter até 500 caracteres.")
        self._link = valor.strip()

    @property
    def categoria(self) -> str:
        """Categoria temática opcional."""
        return self._categoria

    @categoria.setter
    def categoria(self, valor: str) -> None:
        if not isinstance(valor, str) or len(valor) > 80:
            raise ValidationError("A categoria deve ter até 80 caracteres.")
        self._categoria = valor.strip()

    @property
    def autor(self) -> str:
        """Autor opcional do material."""
        return self._autor

    @autor.setter
    def autor(self, valor: str) -> None:
        if not isinstance(valor, str) or len(valor) > 150:
            raise ValidationError("O autor deve ter até 150 caracteres.")
        self._autor = valor.strip()
