import pandas as pd
from datasets import Dataset, ClassLabel
import os


def csv_to_huggingface_dataset(csv_path, save_path=None):
    """
    Converte um CSV para um Dataset do HuggingFace com validações.

    Args:
        csv_path (str): Caminho para o arquivo CSV.
        save_path (str, optional): Caminho para salvar o dataset em disco.
    """
    df = pd.read_csv(csv_path)

    # 1. Verificar se tem exatamente 2 colunas
    if len(df.columns) != 2:
        raise ValueError(
            f"O CSV deve ter exatamente 2 colunas. Encontradas: {len(df.columns)}"
        )

    # 2. Verificar se a coluna 'label' existe
    if "label" not in df.columns:
        raise KeyError("Uma das colunas deve obrigatoriamente se chamar 'label'.")

    # 3. Identificar a outra coluna e renomear para 'text'
    other_column = [col for col in df.columns if col != "label"][0]
    df = df.rename(columns={other_column: "text"})

    # 4. Criar o Dataset do HuggingFace
    hf_data = Dataset.from_pandas(df)

    # 5. Configurar ClassLabel (importante para modelos de classificação)
    unique_classes = sorted(df["label"].unique())
    class_label = ClassLabel(names=list(unique_classes))
    hf_data = hf_data.cast_column("label", class_label)

    # 6. Salvar o resultado, se um caminho for fornecido
    if save_path:
        hf_data.save_to_disk(save_path)
        print(f"Dataset salvo com sucesso em: {save_path}")

    return hf_data
