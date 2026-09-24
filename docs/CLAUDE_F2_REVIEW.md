# Revisão do pacote `dgm_kernel_f2.zip`

## Identificação

- Arquivo revisado: `/home/ubuntu/upload/dgm_kernel_f2.zip`
- SHA-256: `8010eb3cb5e082c780c6fe81a2966b0132f2990ec4d6d678e81d95d2a2363aad`
- Conteúdo: 36 entradas, incluindo 10 módulos de kernel, 17 arquivos de teste, `ATTACK_MATRIX.md`, `THREAT_MODEL.md` e `DECISOES_HUMANAS.md`.

## Reprodução

O arquivo foi extraído para um diretório temporário separado do repositório do projeto e a suíte foi executada sem instalação de novas dependências:

```text
77 passed in 4.39s
```

Os testes de CPU, memória, processos, timeout e rede fazem parte dessa suíte. O teste `test_known_limitation_filesystem_not_chrooted` confirma explicitamente que o backend `SubprocessSandbox` não fornece isolamento de filesystem. A factory também rejeita backends de produção indisponíveis com `FailClosedError`.

## Compatibilidade com o projeto atual

O pacote não é um commit incremental da árvore publicada. Ele usa `kernel/`, `cli.py` na raiz, `requirements.txt`, APIs como `BudgetLedger`, `KernelLog`, `Archive` e `SubprocessSandbox`, enquanto o projeto atual usa `src/evo_kernel/`, `pyproject.toml`, `Budget`, `HashChain`, `ExploratoryRun` e a CLI `evo-kernel`. Portanto, os 77 testes não são testes adicionais da base atual e não devem ser somados aos 31 testes atuais como se fossem uma única suíte.

## Pontos positivos confirmados

A implementação alternativa documenta honestamente o limite de filesystem do subprocesso, mantém backend de produção fail-closed, usa limites reais de CPU/memória/processos/tempo, testa rede via namespace, mantém evaluator por stdin/stdout e fornece uma matriz explícita dos 27 ataques obrigatórios.

## Pontos a resolver antes de eventual integração

Primeiro, `make_isolated_workdir` deve validar caminhos relativos e rejeitar `..`, caminhos absolutos e escapes antes de escrever arquivos. Hoje a função concatena o caminho fornecido ao diretório temporário; embora os chamadores atuais pareçam kernel-controlled, a validação deve existir na boundary.

Segundo, `SubprocessSandbox.run` aceita `extra_env` e faz merge desse conteúdo depois da allowlist mínima. A API deve restringir ou remover esse parâmetro, para evitar que um chamador repasse credenciais, tokens ou variáveis protegidas ao processo avaliado.

Terceiro, a validação do gateway exige campos `provider` e `model`, mas o trecho revisado não demonstra uma allowlist de valores efetivamente permitidos. Antes de uso real, provider/model/version devem ser fixados por política do kernel, como já ocorre no gateway da árvore atual.

Quarto, o pacote alternativo contém logs persistentes locais, mas continua corretamente classificado como `TAMPER_EVIDENT_LOCAL_ONLY`; não há âncora externa. Isso não deve ser promovido a evidência confirmatória.

## Decisão

O pacote foi **verificado, não integrado**. O estado do projeto atual permanece `IN_PROGRESS`, `EXPLORATORY` e `FAIL_CLOSED`. A integração deve ser feita por seleção de componentes e adaptação testada, não por cópia integral da árvore alternativa.
