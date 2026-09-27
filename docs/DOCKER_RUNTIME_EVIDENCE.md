# Evidência real do runtime Docker

Em 2026-09-27, após autorização explícita, o usuário `ubuntu` foi adicionado ao grupo `docker` para permitir acesso ao daemon sem `sudo`.

O daemon Docker 29.1.3 respondeu a `docker info` em sessão com o grupo aplicado. O probe real do perfil `python:3.12-slim` produziu:

| Propriedade | Resultado |
|---|---|
| `network_disabled` | `true` |
| `no_new_privileges` | `true` |
| `seccomp_present` | `true` |
| `resource_limits_verified` | `true` |
| `disposable_filesystem_verified` | `true` |
| `required_capabilities_verified` | `true` |
| `uid_non_root` | `true` |
| `docker_socket_absent` | `true` |
| `protected_mounts_absent` | `true` |
| `rootless_or_userns` | `false` |

O executor permaneceu `FAIL_CLOSED` porque o daemon está rootful e não possui user namespace remapeado. `--userns=private` foi testado e o Docker rejeitou a opção como modo inválido. Não foi alterada a configuração do daemon para habilitar userns-remap.

Durante a validação foi corrigido um falso positivo: o probe inicialmente confundia o caminho de origem `/var/lib/docker` nos mounts internos de `/etc/hosts`, `/etc/hostname` e `/etc/resolv.conf` com mount protegido. A verificação agora examina o mountpoint efetivo antes do separador ` - ` do `/proc/self/mountinfo`, e uma regressão cobre esse caso.

**Estado:** Docker real parcialmente verificado; autorização de execução continua bloqueada até resolver e revalidar `rootless_or_userns`.
