# Contribuição

## Estado do projeto

A F1 está resolvida em `MODE=EXPLORATORY`. O estado atual é `IN_PROGRESS`: F2 parcial, com F3 preparada e F4 dry-run concluída. Este repositório é um `DEVELOPMENT / PREPARATION ENVIRONMENT`. A execução de genoma permanece bloqueada (`genome_execution=BLOCKED`) sob a política `FAIL_CLOSED`; `attack_gate` permanece `CLOSED`. Docker instalado não autoriza runtime experimental. As decisões de isolamento continuam registradas em `protocol/DECISOES_HUMANAS.md`.

## Antes de abrir um pull request

- Verifique se a alteração não implementa ou habilita o kernel experimental prematuramente.
- Atualize a especificação, o threat model ou o protocolo quando a mudança afetar segurança, validade, causalidade, interpretabilidade, custo ou governança.
- Registre qualquer nova dependência em `pending_approval/` antes de adicioná-la.
- Não inclua credenciais, tokens, dados de holdout, logs oficiais ou artefatos privados.
- Preserve o vocabulário operacional e as limitações epistemológicas do projeto.

## Validação

A validação local esperada é a suíte unitária, a mesma do CI (pytest via GitHub Actions, `.github/workflows/ci.yml`):

```bash
PYTHONPATH=src python3 -m pytest
```

O job de CI remove o CLI Docker do PATH antes do pytest e não executa genoma (`FAIL_CLOSED`).

## Revisão

Mudanças em permissões, sandbox, evaluator, gateway, orçamento, manifesto, métricas, seleção, holdout, threat model ou protocolo exigem revisão humana explícita e não devem ser mescladas silenciosamente.
