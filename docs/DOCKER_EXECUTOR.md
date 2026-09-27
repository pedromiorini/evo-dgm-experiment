# Executor Docker fail-closed

A base possui um executor Docker separado do pré-voo conceitual. Ele valida o perfil declarativo, confirma que o binário Docker responde a `docker info`, executa um probe dentro do perfil e só guarda autorização quando recebe evidência booleana para rootless/user namespace, `no-new-privileges`, rede desabilitada, seccomp, limites de recursos, filesystem descartável, capabilities, UID não-root, ausência de Docker socket e ausência de mounts protegidos.

O probe observa propriedades efetivas em `/proc`, cgroups, rotas de rede, tentativa de escrita no root filesystem, UID, capabilities, mounts e presença de socket. Evidência ausente, falsa, malformada ou inconsistente bloqueia o executor.

Cada `RuntimeEvidence` também registra `docker_server_version`, `image_reference`, `image_digest`, `profile_hash`, `probe_version`, timestamp UTC e `runtime_fingerprint`. O fingerprint inclui versão do daemon, referência e digest da imagem, hash do perfil e versão do probe. Antes de reutilizar evidência em `run()`, o executor consulta novamente a identidade do daemon; se o fingerprint mudar, executa novo probe. Evidência antiga não é reutilizada após alteração relevante.

O executor não possui fallback para subprocesso. Se Docker estiver ausente, o probe falhar ou qualquer propriedade for falsa, ele lança `DockerExecutorError` com `FAIL_CLOSED`. O perfil inclui `--interactive` para preservar o transporte stdin/stdout necessário ao evaluator, sem alocar TTY.

O Docker real está acessível ao usuário do projeto e o probe comprovou 9 de 10 propriedades. O bloqueio residual é `rootless_or_userns=false`: o daemon está rootful sem user namespace remapeado. A opção `--userns=private` foi testada e rejeitada pelo Docker atual. Não há autorização para relaxar esse requisito nem para alterar o daemon sem revisão separada.

A imagem experimental é referenciada por digest (`python@sha256:...`) e o perfil sempre inclui `--pull=never`; tags mutáveis e pull implícito são rejeitados.

Os testes usam runner injetado para validar política, fingerprint e revalidação, mas não substituem a execução real. A evidência detalhada está em [DOCKER_RUNTIME_EVIDENCE.md](DOCKER_RUNTIME_EVIDENCE.md). A execução de genomas continua bloqueada até a propriedade residual e os ataques obrigatórios serem resolvidos e revalidados.
