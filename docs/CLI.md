# Interface CLI

A CLI implementa os comandos mínimos previstos na SPEC. Todos os comandos são seguros para o ambiente atual: não iniciam containers, não fazem chamadas de rede e não executam código de genoma.

```bash
PYTHONPATH=src python3 -m evo_kernel.cli validate
PYTHONPATH=src python3 -m evo_kernel.cli run --generations 3
PYTHONPATH=src python3 -m evo_kernel.cli inspect
PYTHONPATH=src python3 -m evo_kernel.cli lineage
PYTHONPATH=src python3 -m evo_kernel.cli replay
PYTHONPATH=src python3 -m evo_kernel.cli stop
PYTHONPATH=src python3 -m evo_kernel.cli report
PYTHONPATH=src python3 -m evo_kernel.cli readiness
PYTHONPATH=src python3 -m evo_kernel.cli attack-matrix
```

`validate` verifica o manifesto de demonstração e reporta a disponibilidade do sandbox. `run` e `report` executam somente o dry-run B3 de três gerações. `inspect` exibe o estado global e o bloqueio de execução. `lineage` exibe o contrato de proveniência. `replay` valida um cassette local registrado. `stop` confirma que não há execução ativa e mantém o bloqueio.

`readiness` calcula os gates de política, runtime e ataques sem executar Docker, probes ou código de candidato. `attack-matrix` lista os 13 ataques, informa `NOT_RUN`/`UNVERIFIED` e mantém o gate bloqueado. A existência dos comandos não constitui autorização.

O entry point de pacote também está definido como `evo-kernel` quando o projeto é instalado. A saída é JSON para facilitar auditoria e automação, mas não deve ser interpretada como evidência científica: o estado continua `INSUFFICIENT_EVIDENCE`.
