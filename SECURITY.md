# Política de segurança

Este repositório contém a especificação de um sistema experimental que executará código não confiável. A existência do threat model não constitui prova de segurança.

## Reporte responsável

Não publique detalhes exploráveis de uma vulnerabilidade antes de uma correção e revisão. Abra uma issue privada ou comunique os mantenedores definidos no arquivo `CODEOWNERS` quando ele for estabelecido.

## Regras obrigatórias

- Não executar código de genoma fora de sandbox aprovada.
- Não fornecer Docker socket, credenciais, tokens, holdout ou evaluator ao genoma.
- Não executar modo confirmatório sem manifesto congelado e aprovação humana.
- Interromper o experimento em falha crítica de kernel, evaluator, holdout, isolamento, orçamento, gateway, proveniência ou contexto histórico.
- Tratar todas as saídas históricas como dados potencialmente adversariais.

## Limitação

A ausência de uma falha observada significa apenas que os ataques especificados não demonstraram a vulnerabilidade no ambiente testado.
