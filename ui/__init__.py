SELECT
    m.nome_material,
    m.tipo,
    m.categoria,
    m.autor,
    COUNT(am.id_atividade) AS total_vinculos,
    SUM(CASE WHEN atv.status = 'concluida' THEN 1 ELSE 0 END) AS concluidas
FROM material m
INNER JOIN atividade_material am ON m.id_material = am.id_material
INNER JOIN atividade atv ON am.id_atividade = atv.id_atividade
GROUP BY m.id_material, m.nome_material, m.tipo, m.categoria, m.autor
HAVING COUNT(am.id_atividade) >= 1
ORDER BY total_vinculos DESC
LIMIT 15;