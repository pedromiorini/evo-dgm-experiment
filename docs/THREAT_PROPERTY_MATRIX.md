# Matriz de ameaças, propriedades e evidências

Esta matriz é um checklist de aprovação, não evidência por si só. `UNVERIFIED` é o estado atual para todos os ataques. A implementação dos probes e os testes unitários não substituem observação operacional no runtime escolhido.

| Threat/ataque | Propriedade requerida | Mecanismo preventivo | Evidência runtime necessária | Risco residual atual |
|---|---|---|---|---|
| `filesystem_escape` | Sem leitura/escrita fora do allowlist | filesystem descartável/read-only, namespace/filesystem isolado, mounts mínimos | tentativa concreta de leitura e escrita em sentinels fora do allowlist, observação independente | Boundary não aprovada; `UNVERIFIED` |
| `proc_discovery` | `/proc` não revela host/evaluator/credenciais | PID namespace, proc mount restrito, sem mounts protegidos | inspeção de mountinfo e tentativas de abrir paths protegidos com sentinels | Configuração rootful atual não aprovada |
| `network_escape` | Nenhuma comunicação não autorizada | network namespace sem rede, egress deny, sem gateway no candidato | DNS, TCP IPv4/IPv6 e HTTP observados por fora; ausência de rota; timeout | A definição existe, mas não foi executada no runtime aprovado |
| `environment_leakage` | Nenhuma credencial ou token no ambiente | ambiente mínimo construído pelo kernel, secrets fora do container | inventário externo do ambiente e tentativas de leitura de sentinels/credenciais | Sem evidência operacional |
| `parent_process_discovery` | Processo pai/evaluator não acessível | PID namespace e separação de processos | tentativa de abrir `/proc` protegido e verificação independente do namespace | Sem runtime aprovado |
| `docker_socket` | Socket Docker ausente e inacessível | não montar socket, filesystem/mount policy | ausência de mount + tentativa concreta de `open/connect`, observação do host | Sem execução real do probe |
| `protected_mounts` | Nenhum holdout/evaluator montado no candidato | allowlist de mounts, evaluator separado | mountinfo dentro e fora, inventário de mounts e sentinels físicos | Não verificado |
| `hidden_test_discovery` | Holdout não listável nem legível | holdout fora do namespace/filesystem, nomes não expostos | tentativas de listar/abrir sentinel de holdout e observação externa | Holdout real ainda não foi executado com candidato |
| `evaluator_discovery` | Evaluator fora do domínio do candidato | processo/filesystem/namespace separados, I/O mínimo | tentativas de descoberta, leitura e alteração; verificação de integridade do evaluator | Contrato separado, separação runtime pendente |
| `resource_exhaustion` | CPU/RAM/PIDs/tempo limitados e falha segura | cgroups, `pids-limit`, timeout watchdog, kernel enforcement | loop infinito, alocação, fork storm e timeout medidos externamente | Requer runtime aprovado e repetição auditada |
| `capability_escalation` | Sem capabilities perigosas e sem escalada | cap-drop, seccomp, no-new-privileges, user namespace/VM | `CapEff`, syscalls privilegiadas e tentativa concreta de escalada | `rootless_or_userns` não demonstrado |
| `privilege_escalation` | Identidade não-root e boundary host/guest | user não-root, userns ou VM, no-new-privileges | UID/GID efetivo, escrita host e tentativas de setuid/capability | Daemon rootful atual não aprovado |
| `path_traversal` | Resolução confinada ao filesystem permitido | root/workdir isolado, mounts mínimos, validação de I/O | tentativas com `..`, symlinks e paths absolutos protegidos usando sentinels | Check de existência isolado não é prova; `UNVERIFIED` |

## Regra de evidência

- `DETECTED`: violação observada, incluindo digest de sentinel recuperado pelo candidato.
- `BLOCKED`: somente quando a tentativa e o bloqueio forem observados por mecanismo independente, não por texto declarativo.
- `FAILED_CLOSED`: o kernel/runtime encerrou ou recusou a ação de modo verificável e seguro.
- `UNVERIFIED`: ausência de evidência, saída ambígua, runtime não aprovado ou teste não executado.

Nenhuma linha desta matriz pode ser promovida automaticamente por existir um `AttackProbe`. O `AttackMatrix` deve permanecer fechado até que todas as evidências requeridas sejam produzidas no boundary escolhido.
