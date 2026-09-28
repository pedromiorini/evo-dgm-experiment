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

## Milestone seguinte: sentinels

Foi adicionado `SentinelRegistry`, que mantém segredo aleatório no domínio kernel-only e classifica observações por digest do valor lido. A mera existência de path não é mais tratada como acesso. Esta é uma implementação de contrato e testes unitários; sentinels reais fora do domínio do container e execução adversarial ainda estão pendentes.

## Evidência vinculada ao runtime

`RuntimeEvidence` agora registra versão do daemon, referência e digest da imagem, hash do perfil, versão do probe, timestamp UTC e fingerprint. `DockerExecutor.run()` reconsulta a identidade do runtime antes de reutilizar evidência; mudança de daemon, imagem, perfil ou probe força novo probe e mantém `FAIL_CLOSED` em caso de falha. Testes cobrem metadados e invalidação quando a versão Docker muda.

## Contrato estruturado dos probes

Cada `AttackProbe` agora declara `expected_safe_status`, `classification_rule` e `evidence_type`. O probe de exaustão declara `FAILED_CLOSED` como resultado seguro; os checks de existência permanecem marcados como preliminares, sem serem promovidos a evidência final. A próxima etapa continua sendo sentinels físicos e observação independente.

## Workspace físico de sentinels

Foi adicionado `SentinelWorkspace`, que cria diretório temporário fora do projeto (`0700`) e arquivos sentinel protegidos (`0600`), com limpeza determinística. O sentinel não é montado nem copiado para o container avaliado. Testes verificam permissões, digest e remoção após o context manager.

Isso prepara a medição de acesso efetivo, mas ainda não constitui evidência operacional: a próxima etapa precisa executar uma ação adversarial no runtime aprovado, observar o acesso fora de stdout declarativo e registrar o resultado na matriz. O gate continua fechado.

## Probe de acesso efetivo com sentinel

Foi adicionado `run_sentinel_access_probe`. O executor monta somente o arquivo sentinel declarado, em modo read-only, no destino controlado. O leitor definido pelo kernel retorna o digest SHA-256 do conteúdo; somente o nonce exato produz `DETECTED`. Saída ausente, `BLOCKED`, stderr, linhas extras, erro ou timeout permanecem `UNVERIFIED`, pois não provam bloqueio.

A integração está coberta por testes com executor controlado e não foi usada para abrir o gate: ainda depende de Docker aprovado (`rootless_or_userns` continua pendente) e de uma execução real auditada.

## Rechecagem operacional de 2026-09-28

Neste sandbox, `docker` está instalado (`29.1.3`) e o serviço está ativo, mas `ubuntu` não pertence ao grupo `docker`; o acesso sem privilégio ao socket retorna `permission denied`. A inspeção somente-leitura com `sudo docker info` mostrou `SecurityOptions=[seccomp,cgroupns]`, sem `rootless` ou `userns`, e driver `overlayfs`. O mapa de UID do processo também é identidade direta (`0 -> 0`), não user namespace.

Consequentemente, o preflight atual retorna `FAIL_CLOSED` por indisponibilidade do socket para o processo e ainda não é possível executar o probe que confirmaria as dez propriedades. Mesmo que o acesso ao socket fosse concedido, a ausência de rootless/userns continuaria bloqueando a aprovação. Nenhuma configuração global foi alterada e nenhum container foi executado.
