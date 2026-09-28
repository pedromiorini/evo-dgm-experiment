# DECISÕES_HUMANAS.md

Registro formal da F1 antes do início da F2.

## Item 13 — MODE

**Decisão: `EXPLORATORY`**

CONFIRMATORY fica fora desta rodada. Não serão feitas alegações causais ou de `PROCESS`; resultados exploratórios serão registrados de forma reproduzível.

## Item 8 — Isolamento disponível

**Status verificado em 2026-09-23: `PENDING_ISOLATION`.** O ambiente atual não possui o comando `docker` (`docker: command not found`). Portanto, nenhuma execução de genoma pode começar: a política é `FAIL_CLOSED`.

A implementação da F2 poderá preparar e testar os controles de kernel que não executam genoma, mas a execução sandbox real dependerá de um ambiente com Docker disponível e validado por `docker --version` e `docker info`.

Perfil planejado quando disponível: rootless, `no-new-privileges`, seccomp, capabilities mínimas, rede negada por padrão e filesystem descartável. gVisor, Firecracker, Kata Containers ou VM dedicada permanecem upgrades posteriores.

## Item 12 — Domínio das tarefas

**Decisão:** programação com verificação automática por entrada/saída, templates versionados e testes discriminativos.

## Orçamento exploratório

**Teto registrado:** aproximadamente US$50–100 no total, 10–20 gerações, usando o modelo mais barato compatível. O teto pode ser ajustado no modo exploratório, desde que a alteração seja registrada.

## Baselines exploratórios

Nesta rodada, executar somente B3 (`evolução completa`) para validar o pipeline. B0 poderá ser incluído como referência de sanidade. B1, B2, B4 e B5 ficam reservados para eventual modo CONFIRMATORY.

## Itens deferidos até eventual CONFIRMATORY

SESOI, alfa, poder, número máximo de runs PROCESS, nível ARTIFACT/PROCESS, estimando de custo confirmatório e política da FINAL permanecem deferidos. A regra estrutural de B2, caso venha a ser usada, será a mesma regra de finalista de B3.

## Status da F1

A F1 está resolvida para `MODE=EXPLORATORY`, com a ressalva operacional de isolamento acima. A F2 pode começar em modo de preparação e testes; toda execução de genoma permanece bloqueada até que o ambiente de sandbox seja verificado.

- **Responsável:** decisão fornecida pelo usuário
- **Data do registro:** 2026-09-23
- **Modo:** `EXPLORATORY`
- **Commit de aprovação:** a registrar no commit desta atualização

## Adendo operacional — 2026-09-28

A afirmação acima sobre `docker: command not found` descrevia a verificação de 2026-09-23 e não é mais o estado atual. Na rechecagem atual, Docker `29.1.3` está instalado e o serviço está ativo, mas a sessão `ubuntu` não tem acesso ao socket. A inspeção somente-leitura privilegiada observou daemon rootful, sem `rootless` ou `userns`. Portanto o Item 8 permanece `PENDING_ISOLATION`, nenhuma alternativa foi escolhida, nenhuma configuração global foi alterada e a execução continua `FAIL_CLOSED`.

A decisão humana pendente agora inclui escolher e auditar uma boundary entre Docker rootless, Docker com userns-remap, gVisor, Kata Containers, Firecracker/VM dedicada ou alternativa equivalente, conforme [INFRASTRUCTURE_DECISION.md](../docs/INFRASTRUCTURE_DECISION.md). O objetivo não é fazer um booleano passar, mas demonstrar as propriedades exigidas pelo protocolo.

## Decisão arquitetural — separação de ambientes — 2026-09-28

**Decisão:** o sandbox atual é classificado como `DEVELOPMENT / PREPARATION ENVIRONMENT`, não como runtime autorizado para execução de genomas.

Permitido neste ambiente: editar código, executar testes unitários, validar contratos, produzir documentação, análise estática, preparar manifestos e testar readiness gates simulados. Não permitido: transformar o container de desenvolvimento em sandbox experimental por nesting, conceder acesso ao socket Docker, alterar daemon/host/sysctls/namespaces, instalar runtimes de isolamento ou executar containers de workload, candidatos, hidden tests ou os 13 ataques.

O runtime experimental futuro deverá ser externo ou dedicado ao desenvolvimento e deverá manter kernel evaluator, holdout/hidden tests, seleção, orçamento, gateway, credenciais, logs confiáveis, manifesto/protocolo e controle de autorização fora do domínio do candidato. A escolha da boundary e o provisionamento desse runtime permanecem decisões humanas pendentes.

O estado obrigatório permanece:

```text
FAIL_CLOSED
genome_execution=BLOCKED
attack_gate=CLOSED
```
