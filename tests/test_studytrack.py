"""Testes básicos dos fluxos principais da V1."""

import unittest
from pathlib import Path
from uuid import uuid4

from app.repositories.database import JsonRepository
from app.services.studytrack_service import StudyTrackService
from exceptions.erros import DuplicateError, NotFoundError, ValidationError


class StudyTrackServiceTests(unittest.TestCase):
    """Verifica regras, vínculos e persistência entre execuções."""

    def setUp(self) -> None:
        pasta_dados = Path(__file__).resolve().parents[1] / "data"
        self.caminho_dados = pasta_dados / f"teste-{uuid4().hex}.json"
        repositorio = JsonRepository(self.caminho_dados)
        self.servico = StudyTrackService(repositorio)

    def tearDown(self) -> None:
        self.caminho_dados.unlink(missing_ok=True)
        self.caminho_dados.with_suffix(".json.tmp").unlink(missing_ok=True)

    def _preparar_estudo(self) -> tuple[dict, dict, dict]:
        aluno = self.servico.cadastrar_aluno(
            "Ana", "ana@example.com", "senha-segura", "2026001", "2INFO", "Informática",
        )
        plano = self.servico.criar_plano(aluno["id_aluno"], "Revisão", "Estudar POO")
        disciplina = self.servico.criar_disciplina("Programação Orientada a Objetos")
        return aluno, plano, disciplina

    def test_persiste_e_recarrega_registros(self) -> None:
        aluno, plano, disciplina = self._preparar_estudo()
        atividade = self.servico.criar_atividade(
            plano["id_plano"], disciplina["id_disciplina"], "Revisar classes",
        )
        material = self.servico.cadastrar_material(
            "POO em Python", "livro", categoria="Programação", autor="Equipe StudyTrack",
        )
        self.servico.associar_material(atividade["id_atividade"], material["id_material"])

        novo_servico = StudyTrackService(self.servico.repositorio)
        encontrados = novo_servico.buscar_catalogo("python", disciplina["id_disciplina"])
        self.assertEqual([material["id_material"]], [item["id_material"] for item in encontrados])
        self.assertEqual("concluida", novo_servico.atualizar_atividade(
            atividade["id_atividade"], status="concluida",
        )["status"])
        self.assertIn("Aluno", novo_servico.resumo_usuario(aluno["id_aluno"]))
        novo_servico.excluir("atividades", atividade["id_atividade"])
        self.assertEqual([], novo_servico.listar("atividade_materiais"))

    def test_rejeita_email_duplicado_e_prioridade_invalida(self) -> None:
        self._preparar_estudo()
        with self.assertRaises(DuplicateError):
            self.servico.cadastrar_aluno(
                "Outra pessoa", "ANA@example.com", "senha-segura", "2026002", "2INFO", "Informática",
            )
        plano, disciplina = self._preparar_estudo_com_conta_nova()
        with self.assertRaises(ValidationError):
            self.servico.criar_atividade(
                plano["id_plano"], disciplina["id_disciplina"], "Revisão", prioridade="urgente",
            )

    def test_planos_e_atividades_sao_individuais_por_aluno(self) -> None:
        ana, plano_ana, disciplina = self._preparar_estudo()
        tarefa = self.servico.criar_atividade_aluno(
            ana["id_aluno"], plano_ana["id_plano"], disciplina["id_disciplina"], "Tarefa da Ana",
        )
        bruno = self.servico.cadastrar_aluno(
            "Bruno", "bruno@example.com", "senha-segura", "2026002", "2INFO", "Informática",
        )
        self.assertEqual([], self.servico.listar_planos_aluno(bruno["id_aluno"]))
        self.assertEqual([], self.servico.listar_atividades_aluno(bruno["id_aluno"]))
        with self.assertRaises(NotFoundError):
            self.servico.atualizar_atividade_aluno(bruno["id_aluno"], tarefa["id_atividade"], status="concluida")

    def test_inicializa_cenario_demo_e_autentica_aluno(self) -> None:
        self.servico.garantir_dados_demo()
        ana = self.servico.autenticar_aluno("ana.demo@studytrack.local", "Estudos123")
        bruno = self.servico.autenticar_aluno("bruno.demo@studytrack.local", "Estudos123")
        self.assertNotEqual(ana["id_aluno"], bruno["id_aluno"])
        self.assertTrue(self.servico.listar_planos_aluno(ana["id_aluno"]))
        self.assertTrue(self.servico.listar_atividades_aluno(ana["id_aluno"]))
        self.assertGreaterEqual(len(self.servico.buscar_catalogo()), 6)

    def _preparar_estudo_com_conta_nova(self) -> tuple[dict, dict]:
        aluno = self.servico.cadastrar_aluno(
            "Bia", "bia@example.com", "outra-senha", "2026002", "2INFO", "Informática",
        )
        plano = self.servico.criar_plano(aluno["id_aluno"], "Plano Bia", "Revisar")
        disciplina = self.servico.criar_disciplina("Matemática")
        return plano, disciplina


if __name__ == "__main__":
    unittest.main()
