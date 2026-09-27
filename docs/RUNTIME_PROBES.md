# Probes concretos do runtime

A matriz possui 13 probes definidos pelo kernel para os ataques operacionais prioritários: escape de filesystem, descoberta de `/proc`, escape de rede, vazamento de ambiente, descoberta do processo pai, Docker socket, mounts protegidos, descoberta de testes ocultos, descoberta do evaluator, exaustão de recursos, capabilities, privilégios e path traversal.

Cada `AttackProbe` declara `expected_safe_status`, `classification_rule` e `evidence_type`. O runner aceita somente marcador único e exato (`BLOCKED`, `DETECTED` ou `FAILED_CLOSED`), com stderr vazio; saída ambígua permanece `UNVERIFIED`. O probe de exaustão declara `FAILED_CLOSED` como resultado seguro quando o timeout é observado.

Os metadados agora tornam explícita a limitação dos probes preliminares: vários ainda são `existence-check` ou `mountinfo-existence-check`, não prova de leitura efetiva. Eles não podem ser usados como evidência final de que uma fronteira foi atravessada ou protegida. A próxima etapa deve substituir esses checks por sentinels secretos criados no domínio protegido, tentativas concretas de leitura e observação independente do kernel.

Os probes são apenas definições de teste e não são executados durante a suíte local. A execução contra Docker real continua bloqueada por `rootless_or_userns=false`; nenhuma classificação operacional dos 13 ataques foi promovida ao gate.
