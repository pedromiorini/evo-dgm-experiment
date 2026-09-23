# Status da F2 — Kernel e segurança

## Estado

A F2 está parcialmente implementada em modo exploratório, sem execução de genomas. O ambiente atual não possui Docker; por isso a política permanece `FAIL_CLOSED` e nenhum backend de sandbox pode aceitar código mutável.

## Controles implementados

| Controle | Estado | Evidência |
|---|---|---|
| Hash chain de logs | Implementado | `src/evo_kernel/integrity.py` e testes de adulteração |
| Contador de orçamento | Implementado | `src/evo_kernel/budget.py` e teste de overrun |
| Histórico entre gerações como dado | Implementado | `src/evo_kernel/history.py` e testes de hash/injeção |
| Pré-voo de isolamento | Implementado | `src/evo_kernel/sandbox.py`; retorna `docker_not_installed` |
| Manifesto congelado | Implementado | `src/evo_kernel/manifest.py` |
| Allowlist de mutações | Implementado | `src/evo_kernel/permissions.py` |
| Estados de validade | Implementado | `src/evo_kernel/validity.py` |
| Proveniência de lineage | Implementado | `src/evo_kernel/provenance.py` |

## O que ainda bloqueia a conclusão da F2

Ainda é necessário validar um runtime real com Docker rootless, `no-new-privileges`, seccomp, capabilities mínimas, rede negada, filesystem descartável e limites de CPU/RAM/processos/tempo. Também falta implementar o evaluator isolado, o gateway estruturado e os ataques de sandbox que só podem ser executados em ambiente apropriado.

A presença desses módulos não constitui prova de segurança. A ausência de falhas observadas significa somente que os testes executados no ambiente atual não demonstraram a vulnerabilidade correspondente.
