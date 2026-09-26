# Evaluator runtime Docker

`DockerEvaluator` conecta tarefas ao `DockerExecutor` aprovado sem escrever testes ocultos no workdir da solução. A solução é enviada ao container como código de execução, cada caso recebe apenas seu stdin e o expected output permanece no processo kernel para comparação posterior.

O resultado exposto contém somente validade, sucesso, hash do evaluator e estados por caso. `hidden_tests_accessible_to_solution` é sempre falso e a tarefa é rejeitada quando incompleta. O evaluator não passa o expected output, o identificador do holdout ou o conteúdo dos testes privados para o processo avaliado.

A implementação exige o `DockerExecutor`; não há fallback para `SubprocessSandbox`. Sem runtime Docker aprovado, a avaliação lança `DockerExecutorError` com `FAIL_CLOSED`. Os testes com runner injetado verificam o contrato de transporte e a ausência de exposição do expected output, mas não substituem testes de escape contra Docker real.
