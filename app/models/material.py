class Material:
    def __init__(self, id_material: int, nome_material: str, tipo: str, descricao_material: str, link: str, categoria: str, autor: str):
        self.id_material = id_material
        self.nome_material = nome_material
        self.tipo = tipo
        self.descricao_material = descricao_material
        self.link = link
        self.categoria = categoria
        self.autor = autor
