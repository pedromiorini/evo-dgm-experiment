# Resposta à auditoria independente

## Veredito

A auditoria foi considerada tecnicamente válida nos principais achados. O projeto permanece `IN_PROGRESS`, `EXPLORATORY` e `FAIL_CLOSED`. Nenhuma execução de genoma foi liberada.

## Correções aplicadas

| Achado | Correção | Evidência |
|---|---|---|
| Sandbox potencialmente fail-open | `available=True` deixou de ser derivado apenas de `docker --version`/`docker info`; o status só pode ser aprovado quando todas as propriedades efetivas forem verificadas | `sandbox.py`, testes de regressão |
| NNP, rede, seccomp e limites não comprovados | O pré-voo atual retorna `docker_present_runtime_profile_unverified`; flags de runtime ainda não são tratadas como evidência | `IsolationStatus.all_required_properties_verified` |
| Manifesto mutável | Conteúdo agora é recursivamente congelado com mappings, tuplas e frozensets imutáveis; alteração direta produz `TypeError` | `manifest.py`, testes de imutabilidade |
| Manifesto confirmatório incompleto | Campos confirmatórios adicionais são exigidos quando `mode=CONFIRMATORY`; campos exploratórios continuam condicionais | `EXPLORATORY_REQUIRED_FIELDS` e `CONFIRMATORY_REQUIRED_FIELDS` |
| Allowlist ampla demais | `MutationProposal` aceita somente `modify_genome`; fixtures, tasks, evaluator assets e DEV artifacts não atravessam essa fronteira | `permissions.py`, testes de paths e ações |

## Pendências preservadas explicitamente

A auditoria também identificou itens que não devem ser mascarados pelas correções lógicas: executor Docker real, verificação efetiva de rootless/user namespace, `no-new-privileges`, seccomp, capabilities, rede, filesystem, limites, ausência de sockets e credenciais, ataques reais ao host/processo/holdout/evaluator, persistência de logs, recuperação após restart e âncora externa.

Esses itens continuam bloqueando a execução real e qualquer conclusão de F2. A hash chain atual permanece classificada como `TAMPER_EVIDENT_LOCAL_ONLY` até existir persistência, recuperação, verificação após restart e, para confirmatório, âncora independente.

## Validação desta correção

A suíte histórica passou em **31 testes**. Na rechecagem de 2026-09-28, Docker `29.1.3` está instalado e o serviço ativo, mas a sessão experimental não acessa o socket e o daemon não mostrou rootless/userns. O preflight atual permanece `FAIL_CLOSED`; nenhum container, genoma ou chamada externa foi executado.
