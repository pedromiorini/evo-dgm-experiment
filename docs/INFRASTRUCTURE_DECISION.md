# Pacote de decisão de infraestrutura

**Data de registro:** 2026-09-28  
**Estado:** decisão pendente; nenhuma alternativa aprovada  
**Regra vigente:** `FAIL_CLOSED`, `genome_execution=BLOCKED`, `attack_gate=CLOSED`

## 1. Estado observado

- Docker `29.1.3` está instalado e o serviço está ativo.
- A sessão `ubuntu` não tem acesso ao socket Docker.
- A inspeção somente-leitura privilegiada observou `SecurityOptions=[seccomp,cgroupns]`, sem `rootless` ou `userns`.
- O driver observado é `overlayfs`; o mapa de UID do processo não demonstra user namespace.
- Nenhum container ou genoma foi executado nesta rechecagem.
- Nenhum parâmetro global do host foi alterado.
- O preflight do processo experimental retorna `FAIL_CLOSED`.

Docker instalado não equivale a Docker acessível, e Docker acessível não equivale a boundary aprovada.

## 2. Alternativas para decisão humana

A tabela não é um ranking. Ela registra hipóteses de boundary que precisam ser configuradas e demonstradas no ambiente de execução escolhido.

| Alternativa | Ameaças que pode mitigar | Propriedades potenciais | Limitações/riscos a verificar | Impacto operacional e custo | Evidência mínima para aprovação |
|---|---|---|---|---|---|
| Docker rootless | Reduz impacto de daemon/containers rootful e escalada para host | Não-root efetivo, isolamento de namespaces, limites, rede negada, caps drop | Não elimina bugs de kernel, fuga de namespace, mounts indevidos ou vazamento lógico; compatibilidade de volumes/cgroups | Pode exigir instalação e daemon por usuário; mudanças em throughput, cgroups e operação | `docker info` rootless, UID/userns dentro do container, probe completo, 13 ataques, fingerprint e revisão de mounts |
| Docker rootful + `userns-remap` | Reduz mapeamento de UID do container para host | User namespace remapeado, perfil Docker atual, limites e rede | Daemon continua rootful; configuração de storage/volumes e cobertura real do remap precisam ser demonstradas | Alteração global do daemon e possível migração/permissão de imagens; custo operacional relevante | Configuração revisada, mapa UID não identidade, teste de escrita/escape, probe completo e ataques reais |
| gVisor | Reduz superfície de syscall/kernel para workloads compatíveis | Sentry/user-space kernel, integração Docker/Kubernetes, rede e filesystem configuráveis | Compatibilidade, performance, cobertura de syscalls e configuração do host; não é prova absoluta | Instalação de runtime e overhead de CPU/latência; disponibilidade não verificada neste sandbox | Runtime `runsc` fixado, configuração auditada, probe de propriedades, ataques reais e benchmark de custo |
| Kata Containers | Adiciona boundary de VM leve por workload | Kernel/VM guest, namespaces, limites e rede sob configuração do runtime | Complexidade de hypervisor, dispositivos/volumes, configuração e superfície do host | Maior latência/memória e dependências de virtualização; disponibilidade não verificada | Runtime Kata fixado, isolamento guest comprovado, mounts/caps/rede auditados, ataques e custo medidos |
| Firecracker/VM dedicada | Boundary de VM mais forte e separação de kernel guest | Filesystem, processo, rede e credenciais separados por VM | Requer arquitetura de runner, imagem/boot, canal I/O e observabilidade próprios; não é drop-in Docker | Maior complexidade de provisionamento e latência de boot; custo depende de pooling | VMM/configuração/imagem fixadas, boundary guest/host demonstrada, canal I/O auditado, 13 ataques e custo |
| Outro mecanismo equivalente | Depende do mecanismo escolhido | Somente as propriedades realmente demonstradas | Não pode ser aprovado por analogia, nome do produto ou prompt | Deve ser avaliado no ambiente-alvo | Threat-to-evidence matrix completa, testes reais reproduzíveis e aprovação humana |

### Propriedades comuns exigidas

A alternativa escolhida deve demonstrar, no runtime real e com fingerprint: filesystem descartável/read-only, não-root ou user namespace equivalente, `no-new-privileges`, seccomp ou boundary equivalente, capabilities efetivamente reduzidas, rede negada, limites de CPU/RAM/processos/tempo, ausência de Docker socket e mounts protegidos, além de evaluator/holdout fora do domínio do candidato.

`rootless_or_userns` não é um objetivo cego: se a alternativa não fornecer exatamente esse booleano, será necessário alterar formalmente o protocolo e demonstrar uma propriedade equivalente. Essa alteração exige decisão humana; este documento não a faz.

## 3. Decisões pendentes

1. Boundary de execução aprovada: uma alternativa da tabela ou outra justificável.
2. Ambiente-alvo em que a alternativa será configurada e auditada.
3. Aceitação, se houver, de custos de latência, memória, compatibilidade e manutenção.
4. Se o requisito explícito de rootless/userns permanecerá obrigatório ou será substituído por uma propriedade equivalente formalmente definida.
5. Critério de aprovação e responsável pela revisão da evidência dos 13 ataques.

Até essas decisões, nenhum acesso ao socket, configuração do daemon, execução de container de candidato ou mudança do attack gate deve ocorrer.

## 4. Saída esperada após a decisão

A alternativa selecionada deve gerar uma nova evidência versionada contendo configuração, imagem/runtime fixados, fingerprint, resultados dos probes, resultados dos 13 ataques com observação independente, limitações e risco residual. Somente depois disso o `RuntimeReadiness` poderá considerar o runtime verificado; ainda será necessário demonstrar evaluator e holdout separados.
