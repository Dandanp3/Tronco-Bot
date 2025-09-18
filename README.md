# Tronco-Bot

**Tronco Bot** é um bot simples desenvolvido para servir como uma ferramenta de teste em dois servidores específicos. Foi projetado como um projeto pessoal de aprendizado, utilizando comandos básicos para testar e gerenciar usuários no Discord. O bot executa funções de solicitação de teste, correção e atribuição de cargos, com a verificação de status do usuário no servidor.

## Funcionalidades

* **Solicitação de Teste**:

  * Os membros dos servidores podem solicitar um teste privado com o comando `!solicitar`.
  * O bot envia o teste no formato de embed, com as alternativas para o usuário marcar.

* **Correção de Teste**:

  * Membros com permissão de staff podem usar o comando `!corrigir` para corrigir o teste e, dependendo do resultado, o bot atribui ou altera cargos no Discord do usuário.

* **Controle de Punições**:

  * Usuários com punições de "strike" não podem solicitar o teste. O bot verifica esse status antes de permitir a solicitação.

* **Armazenamento Simples**:

  * As informações são armazenadas localmente em arquivos JSON, com um arquivo separado para cada servidor. Isso permite um gerenciamento simples de dados, adequado para a escala limitada do bot.

## Estrutura de Dados

* O bot utiliza **arquivos JSON** para armazenar as informações dos usuários e o status dos testes.
* Cada servidor tem seu próprio arquivo de dados, tornando o armazenamento eficiente e isolado entre servidores.
* Como este é um bot pequeno e simples, a estrutura de dados não é altamente otimizada, mas funciona bem para a proposta inicial de uso em dois servidores.

