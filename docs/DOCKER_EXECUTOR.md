# Executor Docker fail-closed

A base possui um executor Docker separado do pré-voo conceitual. Ele valida o perfil declarativo, confirma que o binário Docker responde a `docker info`, executa um probe dentro do perfil e só guarda autorização quando recebe evidência booleana para rootless/user namespace, `no-new-privileges`, rede desabilitada, seccomp, limites de recursos, filesystem descartável, capabilities, UID não-root, ausência de Docker socket e ausência de mounts protegidos.

O probe não copia as flags pedidas para a resposta. Ele observa propriedades efetivas em `/proc`, cgroups, rotas de rede, tentativa de escrita no root filesystem, UID, capabilities, mounts e presença de socket. Evidência ausente, falsa, malformada ou inconsistente bloqueia o executor.

O executor não possui fallback para subprocesso. Se Docker estiver ausente, o probe falhar ou qualquer propriedade for falsa, ele lança `DockerExecutorError` com `FAIL_CLOSED`. O perfil inclui `--interactive` para preservar o transporte stdin/stdout necessário ao evaluator, sem alocar TTY.

Os testes usam runner injetado para validar a política sem fingir que há Docker disponível. A verificação local confirma que este ambiente não possui Docker e continua bloqueado. Os testes mockados não são evidência de isolamento real; o próximo gate operacional deve executar o mesmo fluxo contra Docker real e classificar ataques de escape como BLOCKED, DETECTED, FAILED_CLOSED ou UNVERIFIED.
