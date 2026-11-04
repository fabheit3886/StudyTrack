"""Testes principais do StudyTrack."""

import unittest
from pathlib import Path

from app.repositories.database import JsonRepository
from app.services.studytrack_service import StudyTrackService
from exceptions.erros import (DuplicateError, NotFoundError, ValidationError)

class StudyTrackServiceTests(unittest.TestCase):
    def setUp(self) -> None:
        self.caminho = Path("data/teste_studytrack.json")
        self.repositorio = JsonRepository(self.caminho)
        self.servico = StudyTrackService(self.repositorio)

    def tearDown(self) -> None:
        self.caminho.unlink(missing_ok=True)

    def criar_cenario(self) -> tuple[dict, dict, dict]:
        aluno = self.servico.cadastrar_aluno(
            "Ana",
            "ana@example.com",
            "senha123",
            "2026001",
            "2INFO",
            "Informática"
        )

        plano = self.servico.criar_plano(
            aluno["id_aluno"],
            "Plano de Estudos",
            "Estudar POO"
        )

        disciplina = self.servico.criar_disciplina(
            "Programação Orientada a Objetos"
        )

        return aluno, plano, disciplina

    def test_cadastro_aluno(self) -> None:
        aluno, _, _ = self.criar_cenario()

        self.assertEqual("Ana", aluno["nome_usuario"])

    def test_email_duplicado(self) -> None:
        self.criar_cenario()

        with self.assertRaises(DuplicateError):
            self.servico.cadastrar_aluno(
                "Outra Pessoa",
                "ANA@example.com",
                "senha123",
                "2026002",
                "2INFO",
                "Informática"
            )

    def test_criacao_atividade(self) -> None:
        _, plano, disciplina = self.criar_cenario()

        atividade = self.servico.criar_atividade(
            plano["id_plano"],
            disciplina["id_disciplina"],
            "Revisar Classes"
        )

        self.assertEqual(
            "Revisar Classes",
            atividade["titulo"]
        )

    def test_prioridade_invalida(self) -> None:
        _, plano, disciplina = self.criar_cenario()

        with self.assertRaises(ValidationError):
            self.servico.criar_atividade(
                plano["id_plano"],
                disciplina["id_disciplina"],
                "Exercícios",
                prioridade="urgente"
            )
    def test_material_em_atividade(self) -> None:
        _, plano, disciplina = self.criar_cenario()

        atividade = self.servico.criar_atividade(
            plano["id_plano"],
            disciplina["id_disciplina"],
            "Estudar Herança"
        )
        material = self.servico.cadastrar_material(
            "POO em Python",
            "livro"
        )
        self.servico.associar_material(
            atividade["id_atividade"],
            material["id_material"]
        )
        materiais = self.servico.buscar_catalogo("python")
        self.assertTrue(materiais)
    def test_atividade_de_outro_aluno(self) -> None:
        ana, plano, disciplina = self.criar_cenario()

        atividade = self.servico.criar_atividade_aluno(
            ana["id_aluno"],
            plano["id_plano"],
            disciplina["id_disciplina"],
            "Tarefa Ana"
        )
        bruno = self.servico.cadastrar_aluno(
            "Bruno",
            "bruno@example.com",
            "senha123",
            "2026002",
            "2INFO",
            "Informática"
        )
        with self.assertRaises(NotFoundError):
            self.servico.atualizar_atividade_aluno(
                bruno["id_aluno"],
                atividade["id_atividade"],
                status="concluida"
            )
    def test_autenticacao_demo(self) -> None:
        self.servico.garantir_dados_demo()

        aluno = self.servico.autenticar_aluno(
            "ana.demo@studytrack.local",
            "Estudos123"
        )
        self.assertIsNotNone(aluno)
if __name__ == "__main__":
    unittest.main()