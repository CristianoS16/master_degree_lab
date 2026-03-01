#!/bin/bash
# Script para limpar o ambiente virtual e cache do pip

echo "🧹 Limpando ambiente virtual e cache..."
echo ""

# Remove o ambiente virtual se existir
if [ -d "venv" ]; then
    echo "  → Removendo venv/"
    rm -rf venv/
    echo "    ✓ Removido"
else
    echo "  ℹ️  venv/ não encontrado"
fi

# Limpa o cache do pip
echo "  → Limpando cache do pip"
pip cache purge 2>/dev/null || echo "    (pip cache não disponível)"
rm -rf ~/.cache/pip 2>/dev/null && echo "    ✓ Cache limpo" || echo "    ℹ️  Sem cache para limpar"

# Remove arquivos de log
if [ -f "setup.log" ]; then
    echo "  → Removendo setup.log"
    rm -f setup.log
    echo "    ✓ Removido"
fi

echo ""
echo "✅ Limpeza concluída!"
echo ""
echo "Agora você pode executar o setup novamente:"
echo "  ./setup_local.sh"
echo ""
