# Executor Docker fail-closed

A base agora contém um executor Docker separado do pré-voo conceitual. Ele valida o perfil declarativo, confirma que o binário Docker responde a `docker info`, executa um probe dentro do perfil e só guarda autorização quando recebe evidência booleana para rootless/user namespace, `no-new-privileges`, rede desabilitada, seccomp, limites de recursos, filesystem descartável, capabilities, UID não-root, ausência de Docker socket e ausência de mounts protegidos.

O executor não possui fallback para subprocesso. Se Docker estiver ausente, o probe falhar, o JSON de evidência estiver incompleto ou qualquer propriedade for falsa, ele lança `DockerExecutorError` com `FAIL_CLOSED`. O perfil inclui `--interactive` para preservar o transporte stdin/stdout necessário ao evaluator, sem alocar TTY.

Os testes usam runner injetado para validar a política sem fingir que há Docker disponível. A verificação local confirma que este ambiente não possui Docker e continua bloqueado. Os testes mockados não são evidência de isolamento real; a próxima etapa operacional deve executar o mesmo fluxo contra Docker real e testar escapes e propriedades efetivas.
