FROM python:3.11-slim

# Instala dependências do sistema
RUN apt-get update && apt-get install -y --no-install-recommends \
  build-essential \
  graphviz \
  graphviz-dev \
  libgraphviz-dev \
  pkg-config \
  gcc \
  g++ \
  git \
  && rm -rf /var/lib/apt/lists/*

# Define variáveis de ambiente para ajudar o pygraphviz a encontrar as bibliotecas
ENV GRAPHVIZ_ROOT=/usr
ENV GRAPHVIZ_INCLUDE=/usr/include/graphviz
ENV GRAPHVIZ_LIB=/usr/lib/x86_64-linux-gnu

# Copia o arquivo requirements.txt
COPY docker_requirements.txt .

# Instala as dependências do Python
RUN pip install --upgrade pip
RUN pip install --no-cache-dir -r docker_requirements.txt

# Instala Jupyter Notebook
RUN pip install --no-cache-dir notebook

# Cria diretório de trabalho
WORKDIR /workspace

# Exponha a porta padrão do Jupyter
EXPOSE 8888

# Comando para iniciar o Jupyter Notebook
CMD ["jupyter", "notebook", "--ip=0.0.0.0", "--port=8888", "--no-browser", "--allow-root", "--NotebookApp.token=''"]