#!/bin/bash
# Script para configurar o ambiente local sem Docker
# Inclui instalação do pacote llm-mri do repositório local

set -e  # Para em caso de erro

# Caminho para o repositório LLM-MRI
LLM_MRI_PATH="/home/f-msc2026/ra256352/Documents/pos/code/LLM-MRI"

echo "🔧 Configurando ambiente virtual Python..."
python3 -m venv venv

echo "📦 Ativando ambiente virtual..."
source venv/bin/activate

echo "⬆️  Atualizando pip..."
pip install --upgrade pip setuptools wheel

echo ""
echo "📚 Instalando dependências Python (isso pode levar alguns minutos)..."
echo "    ⚠️  Usando versões do docker_requirements.txt (testadas e funcionais)"
echo "    ⚠️  Usando --no-cache-dir para economizar espaço em disco"
echo ""

# Instala pacotes científicos básicos com versões exatas do docker
echo "    → [1/7] Instalando NumPy 1.26.4..."
pip install --no-cache-dir "numpy==1.26.4"

echo "    → [2/7] Instalando SciPy 1.16.3..."
pip install --no-cache-dir "scipy==1.16.3"

echo "    → [3/7] Instalando Pandas 2.3.3..."
pip install --no-cache-dir "pandas==2.3.3"

echo "    → [4/7] Instalando PyTorch 2.9.1 (CPU-only)..."
# Instala versão específica do Docker (CPU-only para economizar espaço)
pip install --no-cache-dir "torch==2.9.1" --index-url https://download.pytorch.org/whl/cpu

echo "    → [5/7] Instalando PyGraphviz..."
if pkg-config --exists libcgraph; then
    echo "        Usando pkg-config para encontrar bibliotecas graphviz..."
    pip install --no-cache-dir pygraphviz \
        --config-settings="--global-option=build_ext" \
        --config-settings="--global-option=-I$(pkg-config --variable=includedir libcgraph)" \
        --config-settings="--global-option=-L$(pkg-config --variable=libdir libcgraph)" 2>/dev/null || \
    pip install --no-cache-dir pygraphviz
else
    echo "        Instalando pygraphviz com configuração padrão..."
    pip install --no-cache-dir pygraphviz
fi

echo "    → [6/7] Instalando scikit-learn 1.4.2 (compilando do código fonte)..."
# Instala Cython primeiro (necessário para compilar scikit-learn)
echo "        Instalando Cython (build dependency)..."
pip install --no-cache-dir "Cython>=0.29.33"
# Usa --no-build-isolation para usar o numpy já instalado ao invés de baixar 2.0.0rc1
echo "        Compilando scikit-learn 1.4.2..."
pip install --no-cache-dir --no-build-isolation "scikit-learn==1.4.2"

echo "    → [7/7] Instalando demais dependências..."
pip install --no-cache-dir --prefer-binary -r requirements.txt

echo ""
echo "📦 Instalando LLM-MRI do repositório local..."
if [ -d "$LLM_MRI_PATH" ]; then
    echo "    Repositório encontrado em: $LLM_MRI_PATH"
    pip install --no-cache-dir -e "$LLM_MRI_PATH"
    echo "    ✓ LLM-MRI instalado em modo desenvolvimento (editable)"
else
    echo "    ⚠️  AVISO: Repositório LLM-MRI não encontrado em $LLM_MRI_PATH"
    echo "    Continuando sem instalar llm-mri..."
fi

echo ""
echo "✅ Instalação concluída!"
echo ""
echo "🔍 Verificando instalação..."
python3 -c "import torch; print('✓ PyTorch:', torch.__version__)"
python3 -c "import transformers; print('✓ Transformers:', transformers.__version__)"
python3 -c "import pygraphviz; print('✓ PyGraphviz: OK')"
python3 -c "import jupyter; print('✓ Jupyter: OK')" 2>/dev/null || echo "⚠️  Jupyter não instalado"

# Verifica llm-mri
python3 -c "import llm_mri; print('✓ LLM-MRI:', llm_mri.__name__)" 2>/dev/null || echo "⚠️  LLM-MRI não disponível"

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "Para usar o ambiente no VSCode:"
echo "  1. Ative o ambiente virtual:"
echo "     source venv/bin/activate"
echo ""
echo "  2. Abra qualquer notebook (.ipynb) no VSCode"
echo ""
echo "  3. Selecione o kernel Python do ambiente virtual (venv)"
echo "     - Pressione Ctrl+Shift+P"
echo "     - Digite 'Select Interpreter'"
echo "     - Escolha o interpretador do caminho ./venv/bin/python"
echo ""
echo "Para desativar o ambiente virtual:"
echo "  deactivate"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
