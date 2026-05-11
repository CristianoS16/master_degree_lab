## Código

```python
class ActivationAreas:

    def __init__(self, model:str, dataset, reduction_method, device:str="cpu"):
        self.model = model
        self.tokenizer = AutoTokenizer.from_pretrained(model)

    def _tokenize(self, batch):
        """
        Tokenizes a batch of text.

        Args:
            batch (Dataset): Dataset with column "text" to be tokenized.

        Returns:
            Token: Tokenization of the Dataset, with padding enabled and a maximum length of 512.
        """
        if self.tokenizer.pad_token is None:  # Adding eos as pad token for decoders
            self.tokenizer.pad_token = self.tokenizer.eos_token
        
        return self.tokenizer(batch["text"], padding=True, truncation=True, max_length=512)    
```

### Problemas


1. truncation=True:

    Se você tem um documento de 2000 tokens e o tokenizador aplica um "corte seco" no token 512, o seu grafo de ativações estará representando apenas a introdução do texto.

    a. Perda de Semântica: Imagine analisar um artigo científico ou um contrato jurídico: os primeiros 512 tokens geralmente cobrem apenas o título, o abstract e o início da introdução. A metodologia, os argumentos, os resultados e a conclusão (que gerariam padrões de ativação completamente diferentes nas camadas ocultas) são sumariamente ignorados.

    b. Viés nas Métricas: Para análises de diferenças estruturais em grafos, isso insere um viés enorme. Textos longos são "amputados", e a métrica extraída refletirá as características apenas do início dos documentos, perdendo a representação global.

2. Valor de 512 esta fixo no max_length:

    O número 512 é uma herança histórica da era de modelos como o BERT, RoBERTa e DistilBERT, que tinham esse limite físico na sua matriz de posição (Positional Embeddings).

    No entanto, quando falamos de "Large Language Models" (LLMs) modernos como Llama 3, Mistral, ou modelos da família GPT, as janelas de contexto são gigantescas: 8k, 32k, 128k, ou até milhões de tokens.


### Erro ao usar a return_overflowing_tokens=True diretamente:

```
---------------------------------------------------------------------------

ArrowInvalid                              Traceback (most recent call last)

Cell In[10], line 12

      8 umap = UMAP(n_components=2, random_state=42, gridsize=15)

      9 llm_mri = ActivationAreas(

     10     model=model_ckpt, device="cpu", dataset=dataset, reduction_method=umap

     11 )

---> 12 llm_mri.process_activation_areas()

     13 for label in class_names:

     14     current_graph = llm_mri.get_graph(label)



File /llm-mri/llm_mri/ActivationAreas.py:143, in ActivationAreas.process_activation_areas(self, save_raw_path, save_reduced_path, save_jsonl_path)

    133 """

    134 Processes the activation areas.

    135 

   (...)    139     save_jsonl_path (str, optional): Path to save raw features in the extract_features JSONL format.

    140 """

    142 # Obtaining the tokenized dataset

--> 143 self.dataset = self._initialize_dataset()

    145 # Extracting hidden states from the model

    146 self.hidden_states_dataset = self.dataset.map(

    147     self._extract_all_hidden_states, batched=True

    148 )



File /llm-mri/llm_mri/ActivationAreas.py:87, in ActivationAreas._initialize_dataset(self)

...

File /usr/local/lib/python3.11/site-packages/pyarrow/table.pxi:4256, in pyarrow.lib.Table.validate()



File /usr/local/lib/python3.11/site-packages/pyarrow/error.pxi:92, in pyarrow.lib.check_status()



ArrowInvalid: Column 2 named input_ids expected length 21223 but got length 28108

Output is truncated. View as a scrollable element or open in a text editor. Adjust cell output settings...
```

Desalinhamento no número de linhas (registros) da sua base de dados provocado pelo Apache Arrow (o motor por trás do Hugging Face Datasets).

O verdadeiro comportamento de return_overflowing_tokens=True:
Quando você ativa esse parâmetro, o tokenizador não apenas "sinaliza" que houve um corte. Ele pega os tokens excedentes e cria novas sequências (novas linhas) com eles.

Por exemplo, se o seu max_length é 512, e um único texto do seu batch possui 1200 tokens, o tokenizador não retorna uma lista de 512. Ele quebra esse texto e retorna três listas:

Lista 1: Tokens 1 a 512

Lista 2: Tokens 513 a 1024

Lista 3: Tokens 1025 a 1200

Ou seja, uma entrada no batch original se transformou em três saídas no input_ids.

Sem o return_overflowing_tokens=True, o tokenizador aplica um truncamento estrito: ele simplesmente corta e joga fora tudo o que passar de 512. Assim, 21.223 textos entram e exatamente 21.223 input_ids saem, mantendo a tabela do Arrow perfeitamente alinhada.

Descarte: O token 513 em diante é sumariamente deletado. Essa informação extra não é guardada em lugar nenhum, não vira uma nova linha e não é passada para o modelo. Ela simplesmente deixa de existir para aquele processamento.

### Overflow nos datasets usados:

* Para o experimento de _news_:
```
[WARNING] Tokenization overflow detected: 1654 sample(s) exceeded max_length out of 18331. This generated 6550 extra chunk(s) (total chunks: 24881). These long sequences were truncated for the final model input.
```

* Para o experimento de _structure_:
```
[WARNING] Tokenization overflow detected: 1723 sample(s) exceeded max_length out of 21223. This generated 6885 extra chunk(s) (total chunks: 28108). These long sequences were truncated for the final model input.
```

* Para o experimento de _medical_answers_iam_:
```
[WARNING] Tokenization overflow detected: 1 sample(s) exceeded max_length out of 268. This generated 1 extra chunk(s) (total chunks: 269). These long sequences were truncated for the final model input.
```

* Para o experimento de _medical_answers_dpoc_:   
Não ocorre

### Dúvidas:

* Queremos de alguma forma dá suporte a textos grandes?

Como a biblioteca deveria lidar com textos muito grandes?
Em vez de usar truncation=True e jogar a informação fora, uma ferramenta focada em extração de hidden states de documentos inteiros deveria usar estratégias de Chunking ou Sliding Window .

Curiosamente, é justamente aí que aquele return_overflowing_tokens=True (que gerou o seu problema inicial) brilha! O fluxo ideal seria:

Quebrar o texto: O tokenizador usaria o overflow para quebrar automaticamente o texto gigantesco em vários blocos do tamanho suportado (ex: três blocos de 512 tokens).

Extração Sequencial: A biblioteca passaria todos esses blocos pelo LLM, gerando as ativações (hidden states) para a "Parte 1", "Parte 2" e "Parte 3".

Agregação: Por fim, ela combinaria as ativações de todas as partes (calculando a média ou unindo os sub-grafos) para formar um grafo único que realmente represente o documento inteiro.

* Qual porcentagem de entrata truncada deveria torna proibitivo o uso da biblioteca?