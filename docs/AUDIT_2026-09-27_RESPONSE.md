# Resposta à auditoria de 2026-09-27

## Correções concluídas

| Requisito | Implementação | Teste | Resultado | Limitação |
|---|---|---|---|---|
| `DETECTED` não abre o gate | `AttackMatrix.assert_gate_open()` aprova apenas `BLOCKED` e `FAILED_CLOSED` | regressão `test_detected_attack_cannot_open_gate` | `IMPLEMENTED`, `UNIT_TESTED` | nenhum ataque real foi promovido |
| Imagem reprodutível | referência `python@sha256:f77ac9e44ae96ef2c90b8053ea08c31f8be030f824196b0ae4db6d462c84e51f` | perfil rejeita tag mutável e exige `--pull=never` | `IMPLEMENTED`, `UNIT_TESTED` | digest depende da imagem registrada neste ambiente |
| Pull implícito | `--pull=never` no `DockerSandboxProfile.command_args()` | teste do perfil e preflight real | `IMPLEMENTED`, `UNIT_TESTED` | preparação/atualização de imagem é etapa separada |
| Falso positivo de mounts | detector examina mountpoint efetivo, não caminho de origem | regressão com `/var/lib/docker` como source de `/etc/hosts` | `IMPLEMENTED`, `UNIT_TESTED`, `RUNTIME_VERIFIED` | sem mounts protegidos observados no container atual |

## Verificação operacional

O Docker daemon 29.1.3 respondeu sem `sudo` em sessão com grupo `docker`. O probe real aprovou 9/10 propriedades. `rootless_or_userns=false` permanece bloqueador; o executor retorna `FAIL_CLOSED` e o preflight mantém `genome_execution=BLOCKED`.

## Itens ainda não verificados

- os 13 ataques ainda não foram executados como matriz contra o runtime;
- alguns probes ainda são preliminares e precisam de sentinels protegidos e testes de leitura/exfiltração;
- `RuntimeEvidence` ainda precisa ser vinculada a fingerprint completo de versão Docker, digest, perfil, probe e timestamp;
- `DockerEvaluator` ainda é um evaluator de I/O público, não uma demonstração completa com hidden tests reais;
- user namespace remapping/rootless ainda não está configurado;
- logs locais continuam `TAMPER_EVIDENT_LOCAL_ONLY`.

A suíte local final desta etapa: **68 testes aprovados**. Isso não é evidência científica nem autorização para execução de genomas.

## Correção posterior da classificação do runner

A auditoria apontou que substring arbitrária como `previous attempt was BLOCKED` poderia ser interpretada como evidência. O `RuntimeAttackRunner` agora exige uma única linha exata em stdout (`BLOCKED`, `DETECTED` ou `FAILED_CLOSED`) e stderr vazio; qualquer texto adicional permanece `UNVERIFIED`. A regressão correspondente está em `test_runner_does_not_trust_arbitrary_text_containing_marker`.

Isso corrige a confusão acidental por substring, mas não declara que o candidato pode provar a própria segurança. A limitação permanece registrada: a próxima milestone deve usar ações concretas, sentinels protegidos e observação independente do kernel/runtime para produzir resultados dos 13 ataques.
