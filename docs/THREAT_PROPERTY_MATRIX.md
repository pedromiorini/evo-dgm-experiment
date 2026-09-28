# Matriz de ameaças, propriedades e evidências

Esta matriz é um checklist de aprovação, não evidência por si só. `UNVERIFIED` é o estado atual para todos os ataques. A implementação dos probes e os testes unitários não substituem observação operacional no runtime escolhido.

## Estrutura de avaliação

Cada linha segue:

`THREAT → REQUIRED PROPERTY → MECHANISM → OBSERVATION → ACCEPTANCE CRITERION → RESIDUAL RISK`

| Threat/ataque | Propriedade requerida | Mecanismo | Observação confiável | Critério de aceitação | Risco residual atual |
|---|---|---|---|---|---|
| `filesystem_escape` | Leitura/escrita confinada ao allowlist | filesystem isolado/read-only, namespace e mounts mínimos | kernel/runtime observa tentativas de leitura, escrita, symlink e sentinel fora do allowlist | `PASS` só com bloqueio observado; acesso = `FAIL`; ausência = `UNVERIFIED` | Boundary não aprovada |
| `proc_discovery` | `/proc` não revela host/evaluator/credenciais | PID namespace e proc mount restrito | kernel compara namespace/mountinfo e observa abertura de paths protegidos | bloqueio externo observado = `PASS`; acesso = `FAIL`; caso contrário `UNVERIFIED` | Sem runtime aprovado |
| `network_escape` | Nenhuma comunicação não autorizada | network namespace sem rede e egress deny | observador externo registra DNS, TCP, IPv4/IPv6 e HTTP; candidato não classifica | todas as tentativas bloqueadas e observadas = `PASS`; conexão = `FAIL` | Configuração ainda não executada |
| `environment_leakage` | Nenhuma credencial/token acessível | ambiente mínimo e secrets fora do sandbox | kernel injeta nonce fora do domínio e observa tentativas; inventário de env é comparado externamente | nonce/segredo recuperado = `FAIL`; bloqueio observável = `PASS`; ausência = `UNVERIFIED` | Sem evidência operacional |
| `parent_process_discovery` | Processo pai/evaluator não acessível | PID namespace e separação de processos | runtime/kernel observa `/proc` e identidade do namespace | acesso = `FAIL`; bloqueio verificável = `PASS`; caso contrário `UNVERIFIED` | Sem runtime aprovado |
| `docker_socket` | Socket ausente e inacessível | não montar socket e policy de mounts | inventário externo de mounts mais tentativa de `open/connect` observada | socket inacessível por observação externa = `PASS`; acesso = `FAIL` | Sem execução real |
| `protected_mounts` | Holdout/evaluator não montado | allowlist de mounts e evaluator separado | kernel compara mountinfo dentro/fora e usa sentinels físicos | nenhum mount protegido + tentativa bloqueada = `PASS`; exposição = `FAIL` | Não verificado |
| `hidden_test_discovery` | Holdout não listável/legível/inferível por artefato | holdout fora do namespace/filesystem e nomes não expostos | evaluator trusted observa tentativas de listar/abrir e compara sentinels | nenhuma exposição observada = `PASS`; acesso/reconstrução = `FAIL` | Holdout real pendente |
| `evaluator_discovery` | Evaluator fora do domínio do candidato | processo/filesystem/namespace separados e I/O mínimo | kernel observa descoberta, leitura e alteração; integrity hash verifica evaluator | bloqueio + integridade preservada = `PASS`; acesso/alteração = `FAIL` | Separação runtime pendente |
| `resource_exhaustion` | CPU/RAM/PIDs/tempo limitados e falha segura | cgroups, `pids-limit` e watchdog | kernel/watchdog mede wall time, CPU, memória, processos e código de encerramento | limite aplicado e encerramento seguro = `PASS`/`FAILED_CLOSED`; fuga = `FAIL` | Requer runtime aprovado |
| `capability_escalation` | Sem capability perigosa nem escalada | cap-drop, seccomp, no-new-privileges e userns/VM | kernel observa `CapEff`, syscalls e tentativa concreta de escalada | tentativa bloqueada + evidência externa = `PASS`; escalada = `FAIL` | Userns não demonstrado |
| `privilege_escalation` | Identidade não privilegiada no host/guest | user não-root, userns ou VM e no-new-privileges | UID/GID map, teste de escrita host e tentativa setuid observados fora do candidato | separação e bloqueio demonstrados = `PASS`; privilégio/escape = `FAIL` | Daemon atual não aprovado |
| `path_traversal` | Resolução confinada ao filesystem permitido | root/workdir isolado, mounts mínimos e I/O controlado | kernel observa `..`, symlinks e paths absolutos contra sentinels | todas as tentativas bloqueadas = `PASS`; leitura = `FAIL`; ausência = `UNVERIFIED` | Checks de existência não bastam |

## Tipos de evidência

- **Configuration evidence:** versão, digest, flags, mounts, capabilities, namespaces, seccomp, cgroups, rede e hashes de configuração. Descreve o mecanismo.
- **Behavioral evidence:** tentativa concreta, resultado observado externamente, nonce/digest, evento de watchdog, syscall ou comparação de integridade. Demonstra a propriedade em comportamento.

Configuration evidence sozinha nunca promove uma linha a `BLOCKED`. O candidato é untrusted e stdout/stderr não pode declarar o próprio sucesso ou bloqueio.

## Security boundary versus evaluator boundary

A matriz cobre duas questões independentes: (A) o candidato escapa para host, processos, credenciais, rede ou filesystem; (B) o candidato observa, altera ou infere evaluator/holdout. O sucesso de A não implica sucesso de B. Os relatórios devem identificar o trusted observer, o untrusted actor e o artefato observado para cada questão.

## Estados objetivos

- `PASS`: propriedade e critério comportamental demonstrados no runtime fingerprintado.
- `FAIL`: violação observada, incluindo digest de sentinel recuperado pelo candidato.
- `UNVERIFIED`: runtime indisponível/não aprovado, ausência de observação, saída ambígua ou evidência apenas configuracional.

A API atual mapeia esses estados para a matriz operacional como `BLOCKED`, `DETECTED`, `FAILED_CLOSED` e `UNVERIFIED` somente quando o contrato específico fornecer a equivalência. A matriz permanece fechada até todas as evidências reais serem produzidas no boundary escolhido.
