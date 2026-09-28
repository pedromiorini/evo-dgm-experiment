# Inventário factual do ambiente — 2026-09-28

**Escopo:** somente leitura. Nenhum pacote foi instalado, nenhum serviço iniciado, nenhum daemon alterado, nenhum acesso ao socket concedido e nenhum container/candidato/ataque foi executado.

## A. Inventário factual

| Área | Observação | Fonte/limite |
|---|---|---|
| Kernel | Linux `6.18.38+`, x86_64, Ubuntu `24.04.4 LTS` | `uname`, `/etc/os-release` |
| Virtualização | `systemd-detect-virt=docker`; CPU reporta hypervisor KVM | O processo está dentro de um container; isso não prova KVM acessível ao sandbox |
| CPU | 6 CPUs, 3 cores físicos reportados, Intel Xeon 2.10 GHz | `lscpu`; recursos são compartilhados conforme ambiente |
| KVM | `/dev/kvm` ausente; nested virtualization desconhecida | inspeção de path/sysfs; nenhuma VM foi iniciada |
| cgroups | cgroup v2 (`cgroup2fs`); controllers visíveis: `cpuset cpu io memory hugetlb pids` | controllers e `cgroup.subtree_control` legíveis; valores de `cpu.max`, `memory.max`, `pids.max` não estavam disponíveis neste cgroup |
| User namespaces | `user.max_user_namespaces=15742`; `user.max_net_namespaces=15742`; `kernel.unprivileged_userns_clone` não disponível neste namespace | valor máximo não demonstra que criação efetiva é permitida |
| Rootless helpers | `newuidmap` e `newgidmap` não encontrados | `command -v`; pré-requisito ausente para o fluxo convencional |
| Subordinate IDs | `/etc/subuid` e `/etc/subgid` existem e possuem entradas para `ubuntu`/`user` | conteúdo dos intervalos foi redigido; existência não prova daemon rootless funcional |
| AppArmor | binário `aa-status` existe, mas status efetivo não foi confirmado | observação sem privilégio suficiente/sem saída conclusiva |
| SELinux | `/sys/fs/selinux/enforce` indisponível | não demonstrado neste ambiente |
| Seccomp do processo atual | `Seccomp: 0`, `Seccomp_filters: 0` | característica do sandbox atual, não aprovação do runtime de candidatos |
| Filesystem | `/` e `/tmp` em `/dev/root`, 48G total, 39G livres no momento | `findmnt`/`df`; não é evidência de rootfs descartável de candidato |
| Docker client | Docker `29.1.3` instalado | `docker version` retornou apenas client |
| Docker daemon | serviço ativo conforme rechecagem anterior; processo atual recebe `permission denied` no socket; inspeção privilegiada anterior observou rootful, `overlayfs`, sem `rootless`/`userns` | nenhum container foi executado nesta etapa |
| gVisor | `runsc` não encontrado | `command -v` |
| Kata | `kata-runtime`, `kata-collect-data` e `kata-check` não encontrados | `command -v`; nenhum workload iniciado |
| Firecracker | `firecracker` não encontrado; KVM também ausente | `command -v`, `/dev/kvm` |
| Memória | 23 GiB total, 21 GiB disponíveis no momento, swap 2 GiB | `free -h`; dinâmica |
| Disco | 48 GiB no filesystem observado, 39 GiB livres | `df -h`; dinâmica |

## B. Viabilidade técnica preliminar

Esta classificação é de disponibilidade/pré-requisito, não de aprovação de segurança.

| Alternativa | Classificação atual | Motivo |
|---|---|---|
| Docker rootless | **Desconhecido / pré-requisitos ausentes** | Docker client existe; `newuidmap/newgidmap` não existem; suporte efetivo de user namespace e daemon rootless não foi demonstrado; o sandbox já está dentro de Docker |
| Docker + `userns-remap` | **Desconhecido** | `/etc/subuid`/`subgid` existem, mas daemon é rootful atual, não há configuração lida de remap e nenhuma alteração pode ser feita sem decisão |
| gVisor | **Não disponível no estado atual** | `runsc` ausente; não foi instalado |
| Kata Containers | **Não disponível no estado atual** | runtimes e ferramentas ausentes; KVM não exposto |
| Firecracker/VM dedicada | **Não disponível no estado atual** | binário ausente e `/dev/kvm` ausente; nested virtualization desconhecida |

## C. Pré-requisitos ausentes ou desconhecidos

- Acesso controlado ao runtime, sem necessariamente conceder o socket Docker ao processo experimental.
- Helpers `newuidmap`/`newgidmap` para o fluxo rootless convencional.
- Demonstração efetiva de criação de user namespace não privilegiado.
- Configuração e funcionamento de `userns-remap`, se essa opção for escolhida.
- `/dev/kvm` e nested virtualization para Kata/Firecracker/VM.
- Runtime `runsc`, Kata ou Firecracker, que não foram instalados.
- Valores de limites cgroup aplicáveis a um workload de candidato.
- Perfil AppArmor/SELinux efetivo e sua contribuição para a boundary.
- Observação comportamental dos 13 ataques.
- Separação operacional de evaluator e holdout.

## D. Questões que exigem decisão humana

1. Escolher uma boundary entre as alternativas documentadas.
2. Definir ambiente-alvo fora ou dentro deste sandbox Docker aninhado.
3. Autorizar ou não qualquer alteração de host/daemon e definir revisão responsável.
4. Decidir se rootless/userns permanece requisito explícito ou se uma propriedade equivalente será formalmente especificada.
5. Aceitar custos de complexidade, latência, memória e reprodutibilidade.
6. Aprovar critérios de evidência comportamental e a auditoria dos 13 ataques.

## Estado preservado

```text
FAIL_CLOSED
genome_execution=BLOCKED
attack_gate=CLOSED
```

Disponibilidade preliminar não é aprovação. A alternativa escolhida somente poderá avançar após configuração auditada, fingerprint, evidence de configuração e evidence comportamental no runtime concreto.
