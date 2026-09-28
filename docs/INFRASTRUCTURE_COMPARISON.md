# Comparação técnica de boundaries de isolamento

**Data:** 2026-09-28  
**Finalidade:** apoiar decisão humana, sem ranking e sem seleção automática.  
**Estado do projeto:** `FAIL_CLOSED`; `genome_execution=BLOCKED`; `attack_gate=CLOSED`.

Esta comparação descreve propriedades esperadas e dependências de evidência. Nenhuma linha afirma que a alternativa está disponível ou aprovada neste sandbox. A configuração concreta, a versão e os resultados comportamentais ainda precisam ser produzidos no ambiente escolhido.

## 1. Comparação por dimensão

| Alternativa | Security boundary | Evaluator boundary | Filesystem/processo | Rede/credenciais/capabilities | Recursos e mounts | Observabilidade independente |
|---|---|---|---|---|---|---|
| **Docker rootless** | Daemon e containers operam sem privilégio root do usuário; continua dependente do kernel, namespaces e configuração Docker | Não é fornecida automaticamente; evaluator/holdout ainda precisam estar fora de mounts, processos e namespaces do candidato | Namespaces, rootfs read-only e mounts podem ser configurados; PID isolation depende do perfil | Network namespace/egress deny e cap-drop são configuráveis; credenciais precisam permanecer fora do container | cgroups, pids, timeout e mounts dependem do runtime/host; validar efetivamente | Boa integração com CLI e inspeção de `/proc`, cgroups e mountinfo; o daemon rootless não prova os comportamentos sozinho |
| **Docker + `userns-remap`** | UID/GID do container pode ser remapeado no host; o daemon continua rootful e essa distinção importa | Não resolve separação do evaluator; exige evaluator/holdout externos | Mantém modelo Docker e adiciona user namespace; volumes e ownership precisam ser testados | Rede, credenciais, caps e seccomp continuam dependentes do profile; remap não substitui no-new-privileges | Storage, volumes, mounts, cgroups e permissões podem exigir migração/configuração; validar no host | UID map, tentativa de escrita/escape e observação host são verificáveis; config de remap sozinha não basta |
| **gVisor** | Introduz uma camada de kernel em user space (`runsc`) que reduz a exposição direta de syscalls ao kernel host; não é VM completa | Não separa evaluator por si só; I/O boundary e holdout externo continuam necessários | Filesystem, processos e syscalls passam por camada do runtime; compatibilidade depende do workload | Rede e credenciais dependem do runner e configuração; capabilities/seccomp não devem ser presumidos equivalentes ao Docker | Limites e mounts dependem da integração; overhead e incompatibilidades precisam de medição | Pode observar processo/container, mas parte da evidência deve incluir runtime e host; exige auditoria específica do `runsc` |
| **Kata Containers** | Executa workload em VM/guest kernel leve, adicionando boundary entre guest e host | Não garante evaluator/holdout separado; essa boundary deve ser construída no runner | Guest kernel fornece separação adicional de processos/filesystem; volumes e dispositivos são superfície crítica | Rede, credenciais e capabilities dependem da configuração do guest/runtime; guest boundary não elimina leakage lógico | Maior overhead de memória/latência e dependências de virtualização; mounts/volumes precisam de auditoria | Observação precisa cobrir host, VMM, guest e I/O; mais componentes significam mais evidência e maior complexidade de auditoria |
| **Firecracker/VM dedicada** | VM/VMM separa kernel guest e host; pode fornecer boundary forte se configuração e canal forem mínimos | Não cria evaluator automaticamente; requer runner, I/O boundary e holdout fora da VM/candidato | Filesystem, processos e PID ficam no guest; imagem, boot e dispositivos precisam ser fixados | Rede e credenciais podem ser isoladas por VM; capabilities guest não são prova sobre host | Isolamento e limites podem ser fortes, mas runner, snapshots, dispositivos e lifecycle são complexos | Exige observação no host/VMM/guest e logs do canal I/O; maior esforço para fingerprint e reprodução |

## 2. Avaliação de compatibilidade com o modelo do projeto

| Alternativa | Candidate → I/O boundary → kernel evaluator | Reprodutibilidade | Complexidade/dependências | Custo/latência qualitativos | Dificuldade de auditar |
|---|---|---|---|---|---|
| Docker rootless | Compatível com o executor Docker existente; evaluator ainda precisa ser processo/domínio confiável separado | Imagem por digest e profile hash ajudam; daemon/host ainda fazem parte do fingerprint | Menor mudança arquitetural entre as opções, mas depende de rootless, cgroups e permissões do host | Geralmente menor overhead relativo; medir wall time, CPU, memória e falhas | Média: muitos controles Docker são familiares, mas behavioral evidence continua necessária |
| Docker + `userns-remap` | Compatível com o transporte atual, sujeito a ajustes de storage/ownership | Reproduzível se daemon config, remap e imagem forem fixados | Alteração global do daemon e migração de storage aumentam dependências | Overhead operacional geralmente menor que VM, mas impacto em volumes/permissões precisa de medição | Média: exige provar mapping real e ausência de efeitos colaterais |
| gVisor | Pode preservar o modelo container + I/O, desde que evaluator fique fora | Fixar versão/runtime/configuração é essencial; compatibilidade do workload precisa de cassette | Adiciona runtime e possível adaptação de syscalls/IO | Overhead de CPU/latência pode ser relevante e deve ser medido | Média-alta: evidência deve cobrir sentry, host, mounts, rede e comportamento |
| Kata Containers | Possível, mas o canal de I/O e lifecycle guest precisam ser integrados ao kernel evaluator | Imagem guest, runtime, VMM e configuração devem ser fixados | Hypervisor/guest/volumes/virtualização aumentam dependências | Maior memória/latência que container simples; medir boot e execução | Alta: mais camadas e superfícies para fingerprint e observação |
| Firecracker/VM dedicada | Requer novo runner e I/O boundary; não é substituição direta do executor Docker | Alta somente com kernel, rootfs, VMM, config e lifecycle fixados | Maior mudança arquitetural e operacional | Boot, pooling, memória e observabilidade podem dominar custo/latência | Alta: evidência deve cruzar host, VMM, guest, canal e evaluator |

## 3. Propriedades que nenhuma alternativa fornece automaticamente

Todas as alternativas continuam exigindo implementação e evidência separadas para:

- holdout e hidden tests fora do domínio do candidato;
- evaluator kernel-only fora de filesystem/processo/namespace do candidato;
- ausência de credenciais e tokens;
- integridade de métricas, logs, manifesto e proveniência;
- orçamento e gateway fora do alcance do candidato;
- observação independente das tentativas dos 13 ataques;
- fingerprint do runtime, kernel, imagem, evaluator, probe e artefatos;
- recuperação/replay e auditoria após reinício.

Uma security boundary adequada para impedir escape não demonstra automaticamente evaluator boundary, independência do holdout ou validade experimental.

## 4. Evidências necessárias antes da aprovação

Para qualquer alternativa selecionada, produzir:

1. **Configuration evidence:** versão do mecanismo, host/runtime identifier, imagem/rootfs e digest, profile/config hash, flags, namespaces, mounts, capabilities, seccomp/boundary equivalente, cgroups e rede.
2. **Behavioral evidence:** tentativas concretas dos 13 ataques, observador confiável, artefatos coletados, resultado externo ao stdout/stderr do candidato e classificação objetiva.
3. **Evaluator evidence:** processos, filesystem, namespace, I/O e holdout separados; tentativa de leitura/alteração e verificação independente de integridade.
4. **Reproducibility evidence:** fingerprint completo, versão do kernel/protocolo/evaluator/probe, timestamp, execution ID e hashes dos artefatos.
5. **Risk record:** limitações, incompatibilidades, custos/latência medidos e risco residual aceito pela decisão humana.

Se qualquer propriedade necessária não puder ser demonstrada no runtime concreto, o estado permanece `UNVERIFIED` e a execução continua bloqueada.

## 5. O que não foi feito

- Nenhuma alternativa foi escolhida.
- Nenhum ranking ou score foi produzido.
- O host e o daemon não foram alterados.
- Acesso ao socket não foi concedido.
- Nenhum container, candidato ou ataque foi executado.
- `SPEC.md` não foi alterada.
