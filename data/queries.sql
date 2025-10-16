-- Total a pagar HOJE (abertas)
SELECT IFNULL(SUM(valor), 0) AS total_hoje
FROM contas_pagar
WHERE situacao LIKE 'ABER%' AND date(data_vencimento) = date('now');

-- Total a receber HOJE (abertas)
SELECT IFNULL(SUM(valor), 0) AS total_hoje
FROM contas_receber
WHERE situacao LIKE 'ABER%' AND date(data_vencimento) = date('now');

-- Quem está me devendo (abertas e vencidas)
SELECT contato_nome, SUM(valor) AS total_devedor
FROM contas_receber
WHERE situacao LIKE 'ABER%' AND date(data_vencimento) < date('now')
GROUP BY contato_nome
ORDER BY total_devedor DESC;

-- Resumo por período (últimos 7 dias)
SELECT 'pagar' AS tipo, IFNULL(SUM(valor),0) AS total
FROM contas_pagar
WHERE date(data_vencimento) BETWEEN date('now','-6 day') AND date('now')
UNION ALL
SELECT 'receber', IFNULL(SUM(valor),0)
FROM contas_receber
WHERE date(data_vencimento) BETWEEN date('now','-6 day') AND date('now');
