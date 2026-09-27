# Gate operacional da matriz de ataques

A matriz operacional registra cada ataque com um dos estados `BLOCKED`, `DETECTED`, `FAILED_CLOSED` ou `UNVERIFIED`. O gate exige que todos os ataques obrigatórios tenham resultado.

Para ataques de segurança:

- `BLOCKED` — aprovável;
- `FAILED_CLOSED` — aprovável;
- `DETECTED` — falha: o ataque demonstrou exposição ou vulnerabilidade;
- `UNVERIFIED` — falha: não há evidência suficiente.

Portanto, `DETECTED` e `UNVERIFIED` mantêm o sistema bloqueado. `DETECTED` não significa que o kernel impediu o ataque; significa que o resultado observado não satisfaz a propriedade de segurança.

A matriz inclui escapes de filesystem, `/proc`, rede, ambiente, processo pai, Docker socket, mounts protegidos, descoberta de holdout/evaluator, exaustão de recursos, capabilities, privilégios e path traversal. A implementação registra classificação e evidência, mas não executa ataques por conta própria. A execução contra Docker real permanece dependente de um runtime disponível e aprovado.
