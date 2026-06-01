- [ ] No experimento de probing precisa reomover a primeira camada antes de usar o classificador. 
  - Ver como isso influencia os filtros de arestas
- [ ] Ver dataset do twiter, se tem algo util
- [ ] Rodar com modelos diferentes do Berd --> GPT2 e ModernBERT (Entender melhor esse modernBERT)
- [ ] Ajustar geração de imagens da lib para grande volume de dados

- [ ] Começar a tirar metricas considerando a caracteristica multipartida da rede. Entender o que são as metricas para a rede multipartida --> Atenção na normalização das métricas.
- [ ] Bolar alguma forma de desvinvular dados do codigo, sincronizar com alguma coisa e apagar imediatamente. 
    - [ ] Usar ssh somente para executar a lib, fazer todo o resto local.

- [ ] Se for seguir essa abordagem tem que ver melhor isso aqui: "A naive classifier at a single layer cannot either, be-
cause information about a particular span may be spread out across several layers," - BERT Rediscovers the Classical NLP Pipeline
  - [ ] Possivel usar uma abordagem acumulativa, onde layers são adicionadas, como no paper

- [ ] comparação entre o BERT base e o completo, o comportamento se repete quando olhamos relativo ao tamanho do modelo? Isso é, se normalizar, vemos os mesmos comportamentos nos mesmos pontos?


- [ ] Comparação entre Tarefas de Naturezas Diferentes: No seu código, você definiu os datasets bigram_shift, odd_man_out e sentence_length. Essas tarefas medem propriedades diferentes (sintaxe, semântica e informações superficiais). Avalie se tarefas semânticas (como a anomalia do odd_man_out) geram grafos mais complexos e densos do que tarefas puramente de superfície (como sentence_length).
- [ ] Verificar se grid gerado esta condizente com o grafo
- [ ] Entender a saida da lib e ter alguma forma de verifica-la entre os diferentes modelos

- [ ] Implementar novas metricas (com atenção ao escopo global e por camada)

- [ ] Se continuar com essa ideia de probing, o sentense_leght não bateu com o paper original. 
- [ ] Verificar a doc do UMAP
  - [ ] Revisar implementação da redução de dimensionalidade
  - [ ] Fazer experimento variando a seed do UMAP

- [ ] Olhar extremos (10 e 50) para a analise de camadas
- [ ] Ve o número de neuronios ativos em cada camada antes da redução de dimensionalidade

- [ABSTRATO] Ter algum norte para definir os valores de gridsize

- [ ] Conferir referencias do Bertology para a segregação das camadas
- [ ] Ver questão da camada para outros modelos e aplicações
- [ ] Estudar melhor a lib e entrar em contato com o Luiz
- [ ] Formular melhor a metrica com base no peso das arestas (Ter solisez estatistica nas métricas)
- [ ] Métrica de caminhos medios não faz sentido, é altamente dependente das camadas
- [ ] Assortatividade sempre será negativa devido a discrepancia entre a primeira e segunda camada, talvez da penutima e ultima também

# ======================================================== DONE ========================================================

- [x] Adicionar tamanho da janela de contexto de acordo com tamanho do modelo usado na lib - remover o 512 que ta lá
- [x] Adicionar equações maiores para o experimento de diferentes dominios
- [x] Melhorar experimento das noticias
  - [x] Adicionar um dominio completamente diferente (papers/receitas) - Rede pode não ser influenciada pelo assunto, fazer teste com estruturas diferentes (prontuario/receita)...
  - [x] Ver como as curvas se comportam --> Calcular a correlação no experimento das noticias
  - [x] Normalizar dados para fazer graficos?
- [x] moralizar notebooks para reunião com o Celso
- [x] Estudar a fundo para entender as inversões. 
  - [x] Porque imagem do grid não mostrar ele completo? Há erro no tamanho do grid??
    - Da forma que estava implementado eliminava qualquer linha ou coluna com somente zeros --> foi adicionado um parametro para contornar isso
  - [x] Apresentar grid completo, mesmo com colunas e linhas com somente zero
- [x] Tentar experimentos com grupos de natureza distintas (revisitar experimentos com os papers)
- [x] Plotar distribuição dos pesos das arestas antes e depois do filtro --> Distribuição continua Livre de Escala --> continua sendo uma rede complexa
- [x] No SentEval, as frases são as mesmas para todos as tasks? Isso pode afetar o bert e o NRAG produzido.
  - Paper fala de "The sentences for all our tasks are extracted from the Toronto Book Corpus (Zhu et al., 2015), more specifically
   from the random pre-processed portion"
  - Não deixa claro se frases se repetem entre os datasets
  - Pelo experimento que fiz, datasets são potencialmente diferetentes entre as tasks! porque resultado é tão semelhante? 
- [x] Investigar camada discrepante (numero de nós) entre diferentes modelos e domínios de entradas
  - [x] Testar diferentes BERTs para verificar o comportamento
- [x] Usar as caracteristicas topologicas por camada para fazer o classificador (investigar por que elas não estão variando muito - mexer no limiar da lib) --> Não é possível pois as metricas são por camada/grafo e não são 1 para 1 com as entradas.
    -[x] Quais interferem mais no resultado final (SHAP)? --> SHAP só faz sentido se usar features "conhecidas",  por hora estamos usando somente as ativações das camadas ocultas
    -[x] Por camada, qual metrica descide melhor? --> Não é possível usar metricas no classificador
- [x] Verificar trhesould da lib, muitos dados podem gerar ativações ocasionais
    - threshold é um parametro do Graph2D.build_graph mas não é usado. No GraphND é usado.
    - Pesos das arestas também é contabilizado de forma diferente a depender da Graph2D ou GraphND
    - POR HORA FIZ UM FILTRO MANUAL PARA LIDAR COM ISSO
- [X] Pesquisar melhor o que fiz até aqui, faz sentido fazer a corelação envolvendo a precisão do classificador?
- [X] investigar porque o json gerado tem menos linhas --> Arquivo de entreda estava sendo lido de forma errada
- [x] Usar pelo menos um dataset de cada tipo disponível
- [x] Balancear o corte dos datasets
- [x] Retomar o probing feito na dissertação do Mateus
  - Queria validar a redução de dimensionalidade. Ver o quanto de informações eram perdidas comparando as regiões de ativação dos NRAGs com os embeddings dos docs
  - Usou Regressão Logistica com cross-validation
  - Comparou o impacto de diferentes dimensões (aparentemente quanto maior a dimensão, mais informações são perdidas)
  - Valida que os NRAGs são uma boa representação do comportamento interno do modelo.
  - Não fez por camadas nem teve como objetivo algo relacionado a explicabilidade

- [x] Verificar dataset usado, porque git foi deprecado? 
    - Pode-se usar o JiANT ou o MTEB (https://share.google/aimode/9H22iQTTpkprzZpoI)
    - Professor falou que não é problema usar o SentEval (Não é o momento de ser pop star)
    
- [x] Estudar e entender melhor os conceitos por tras do centro de massa
- [x] Debugar a variação ocorrida no experimento 1 --> O que é não deterministico no processo?
  - Problema na função `UMAP.get_reduction` sem o random_state --> Aparentemente foi esquecimento no refactor e meus testes estavam sempre usando o `n_components` = 2

  - A `UMAP.get_hidden_states_reduction` e usada para reduz todos os hidden states por camada e retorna um dict
    - Usado somente quando `n_components` != 2
  - A `UMAP.get_reduction` e usada depois da `UMAP.get_hidden_states_reduction` para reduz um único conjunto (array) para coordenadas (tipicamente 2D) e retorna coords
    - Usado somente quando `n_components` == 2
  - quando `n_components == 2` usa o Graph2D passando o gridsize, comente nesse caso é possível montar a representação 2D.  
    ![alt text](image.png)
    - Essa afirmação da imagem esta estranha também, segundo o paper: "Each cell represents a region of
      the original higher dimensionality, i.e., an activation value in the original layer is mapped
      to a region of the reduced space."

- [x] Entender como a biblioteca esta configurando os modelos e se externaliza as configs
  - Atualmente só é possível escolher o modelo e ele será carregado pela `AutoModel.from_pretrained`. No entanto, segundo a documentação é possível passar alguns parametros para esse método:
    - https://huggingface.co/transformers/v3.0.2/model_doc/auto.html#transformers.AutoModel.from_pretrained
    - Interessante ter isso para quanto quiser modificar ou ter configs especiais para os modelos usados --> Fazer alterações no modelo e ver o impacto
    - É util para fazer otimizações (diminuir a precisão dos pesos por exemplo)
