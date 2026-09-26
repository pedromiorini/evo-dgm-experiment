# Probes concretos do runtime

A matriz possui 13 probes definidos pelo kernel para os ataques operacionais prioritários: escape de filesystem, descoberta de `/proc`, escape de rede, vazamento de ambiente, descoberta do processo pai, Docker socket, mounts protegidos, descoberta de testes ocultos, descoberta do evaluator, exaustão de recursos, capabilities, privilégios e path traversal.

Cada probe emite um marcador explícito (`BLOCKED`, `DETECTED` ou `FAILED_CLOSED`) apenas quando sua observação local sustenta essa classificação. Saída ambígua permanece `UNVERIFIED`. O probe de exaustão depende do timeout do executor e é classificado como `FAILED_CLOSED` quando o limite é atingido.

Os probes são apenas definições de teste e não são executados durante a suíte local. O ambiente atual não possui Docker, portanto nenhuma classificação real foi atribuída e o gate permanece fechado. Quando Docker estiver disponível, a execução deverá registrar os resultados no `AttackMatrix`, revisar falsos positivos e manter qualquer propriedade não demonstrada como `UNVERIFIED`.
