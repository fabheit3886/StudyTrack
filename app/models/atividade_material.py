"""Vínculo entre uma atividade e um recurso do catálogo."""

from app.models.validacao import identificador_positivo


class AtividadeMaterial:
    """Associação muitos-para-muitos entre atividade e material."""

    def __init__(self, id_atividade: int, id_material: int) -> None:
        self._id_atividade = identificador_positivo(id_atividade, "ID da atividade")
        self._id_material = identificador_positivo(id_material, "ID do material")

    @property
    def id_atividade(self) -> int:
        """Identificador da atividade vinculada."""
        return self._id_atividade

    @property
    def id_material(self) -> int:
        """Identificador do material vinculado."""
        return self._id_material
