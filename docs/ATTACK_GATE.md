# Gate operacional da matriz de ataques

A matriz operacional registra cada ataque com um dos estados `BLOCKED`, `DETECTED`, `FAILED_CLOSED` ou `UNVERIFIED`. O gate exige que todos os ataques obrigatórios tenham resultado e rejeita qualquer matriz que contenha ataque ausente ou `UNVERIFIED`.

Somente `BLOCKED`, `DETECTED` e `FAILED_CLOSED` são estados aprováveis. Um ataque `UNVERIFIED` não é convertido automaticamente em sucesso por ausência de evidência; ele mantém o sistema bloqueado até que o runtime seja testado ou a limitação seja formalmente resolvida.

A matriz inclui escapes de filesystem, `/proc`, rede, ambiente, processo pai, Docker socket, mounts protegidos, descoberta de holdout/evaluator, exaustão de recursos, capabilities, privilégios e path traversal. A implementação registra classificação e evidência, mas não executa ataques por conta própria. A execução contra Docker real permanece dependente de um runtime disponível e aprovado.
