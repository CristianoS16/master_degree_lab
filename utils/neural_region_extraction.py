# Arquivo: utils/neural_region_extraction.py

import numpy as np
import pandas as pd
import json
from pathlib import Path
from typing import Dict, List, Tuple, Optional
import h5py  # Para HDF5 - mais robusto

from llm_mri import ActivationAreas


class NeuralRegionExtractor:
    """
    Extrai dados de regiões neurais da biblioteca llm-mri para realizar
    probing por região neural (ao invés de por camada).

    Salva dados em formatos robustos e portáveis (HDF5, CSV, JSON).
    """

    def __init__(self, llm_mri_object, output_dir: str = "./neural_region_data"):
        """
        Parameters
        ----------
        llm_mri_object : ActivationAreas
            Objeto ActivationAreas após process_activation_areas()
        output_dir : str
            Diretório onde salvar arquivos extraídos
        """
        self.llm_mri = llm_mri_object
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(exist_ok=True, parents=True)

        self.n_samples = len(self.llm_mri.dataset)
        self.n_layers = len(self.llm_mri.graph_class.reduced_dataset)
        self.class_names = self.llm_mri.class_names  # Armazenar nomes das classes

    def _convert_label_to_name(self, label) -> str:
        """
        Converte um índice de label para seu nome legível.

        Parameters
        ----------
        label : int, str, or tensor
            O rótulo (pode ser um índice, string, ou tensor)

        Returns
        -------
        str
            Nome da classe legível para humanos
        """
        # Converter tensor para int se necessário
        if hasattr(label, "item"):
            label = label.item()

        # Converter para int se for string
        if isinstance(label, str):
            try:
                label = int(label)
            except ValueError:
                return label  # Já é uma string válida

        # Mapear índice para nome da classe
        if isinstance(label, int) and 0 <= label < len(self.class_names):
            return self.class_names[label]

        return str(label)

    def extract_region_assignments(self) -> pd.DataFrame:
        """
        Extrai assignments de região para cada (amostra, camada).

        Returns
        -------
        pd.DataFrame
            Colunas: [sample_id, layer, region_id, region_x, region_y, class_label]
            Uma linha por amostra-camada, indicando qual região foi ativada
        """
        assignments = []

        for layer_idx in range(self.n_layers):
            grid_df = self.llm_mri.graph_class.reduced_dataset[layer_idx]

            for sample_idx in range(self.n_samples):
                row = grid_df.iloc[sample_idx]

                assignments.append(
                    {
                        "sample_id": sample_idx,
                        "layer": layer_idx,
                        "region_id": row["cell_label"],  # "layer_x_y"
                        "region_x": int(row["X"]),
                        "region_y": int(row["Y"]),
                        "class_label": self._convert_label_to_name(row["label"]),
                    }
                )

        df_assignments = pd.DataFrame(assignments)
        return df_assignments

    def extract_region_activations(self) -> Dict[Tuple[int, str], List[Dict]]:
        """
        Extrai ativações brutas (768D) organizadas por (camada, região_id).

        Returns
        -------
        Dict[(layer, region_id) → List[Dict]]
            Cada região contém lista de dicts com:
            - 'activations': array 768D
            - 'sample_id': índice da amostra
            - 'class_label': rótulo da classe
        """
        region_activations = {}

        for sample_idx in range(self.n_samples):
            for layer_idx in range(self.n_layers):
                # 1. Obter ID da região
                grid_df = self.llm_mri.graph_class.reduced_dataset[layer_idx]
                region_id = grid_df.iloc[sample_idx]["cell_label"]

                # 2. Chave para armazenar
                key = (layer_idx, region_id)
                if key not in region_activations:
                    region_activations[key] = []

                # 3. Extrair ativações brutas (768D)
                try:
                    activations = self.llm_mri.hidden_states_dataset[sample_idx][
                        f"hidden_state_{layer_idx}"
                    ]
                except (KeyError, IndexError):
                    activations = self.llm_mri.hidden_states_dataset[sample_idx][
                        layer_idx
                    ]

                # 4. Obter label e converter para nome da classe
                label_idx = self.llm_mri.dataset[sample_idx]["label"]
                class_label = self._convert_label_to_name(label_idx)

                # 5. Armazenar
                region_activations[key].append(
                    {
                        "activations": np.array(activations, dtype=np.float32),
                        "sample_id": sample_idx,
                        "class_label": class_label,
                    }
                )

        return region_activations

    def get_samples_per_region(self) -> Dict[Tuple[int, str], List[int]]:
        """
        Mapeia cada (camada, região) → lista de sample_ids que a ativam.

        Returns
        -------
        Dict[(layer, region_id) → List[sample_ids]]
        """
        samples_per_region = {}

        for layer_idx in range(self.n_layers):
            grid_df = self.llm_mri.graph_class.reduced_dataset[layer_idx]

            for sample_idx in range(self.n_samples):
                region_id = grid_df.iloc[sample_idx]["cell_label"]
                key = (layer_idx, region_id)

                if key not in samples_per_region:
                    samples_per_region[key] = []

                samples_per_region[key].append(sample_idx)

        return samples_per_region

    # ========== SALVAMENTO EM HDF5 (Recomendado) ==========

    def save_region_assignments(
        self, filename: str = "region_assignments.csv"
    ) -> pd.DataFrame:
        """Salva assignments em CSV (universal)."""
        df = self.extract_region_assignments()
        filepath = self.output_dir / filename
        df.to_csv(filepath, index=False)
        print(f"✓ Region assignments salvos em: {filepath}")
        print(f"  Shape: {df.shape}")
        return df

    def save_region_activations_hdf5(self, filename: str = "region_activations.h5"):
        """
        Salva ativações brutas (768D) por região em HDF5.

        Estrutura:
        - /{layer}_{region_id}/
          - activations: array [n_samples, 768]
          - sample_ids: array [n_samples]
          - class_labels: array [n_samples]
        """
        region_activations = self.extract_region_activations()
        filepath = self.output_dir / filename

        with h5py.File(filepath, "w") as f:
            for (layer, region_id), activations_list in region_activations.items():
                group_name = f"layer_{layer}_{region_id}"
                group = f.create_group(group_name)

                # Converter para arrays NumPy
                acts = np.array([act["activations"] for act in activations_list])
                sample_ids = np.array([act["sample_id"] for act in activations_list])
                class_labels = [act["class_label"] for act in activations_list]

                # Salvar em HDF5
                group.create_dataset("activations", data=acts, compression="gzip")
                group.create_dataset("sample_ids", data=sample_ids)
                group.create_dataset(
                    "class_labels",
                    data=class_labels,
                    dtype=h5py.string_dtype(encoding="utf-8"),
                )
                group.attrs["n_samples"] = len(activations_list)

        print(f"✓ Region activations (HDF5) salvos em: {filepath}")
        print(f"  Total de regiões: {len(region_activations)}")
        return region_activations

    def save_region_activations_npz(self, filename: str = "region_activations.npz"):
        """
        Alternativa: Salva em NPZ (NumPy compressed) com metadados em JSON.
        Mais simples que HDF5, mas menos estruturado.
        """
        region_activations = self.extract_region_activations()
        filepath = self.output_dir / filename

        # Preparar dados
        data_dict = {}
        metadata = {}

        for idx, ((layer, region_id), activations_list) in enumerate(
            region_activations.items()
        ):
            key = f"region_{idx}"
            acts = np.array([act["activations"] for act in activations_list])
            data_dict[key] = acts

            # Metadados salvos separadamente
            metadata[key] = {
                "layer": layer,
                "region_id": region_id,
                "sample_ids": [act["sample_id"] for act in activations_list],
                "class_labels": [act["class_label"] for act in activations_list],
                "n_samples": len(activations_list),
            }

        # Salvar arrays
        np.savez_compressed(filepath, **data_dict)

        # Salvar metadados em JSON
        metadata_file = filepath.with_suffix(".json")
        with open(metadata_file, "w") as f:
            json.dump(metadata, f, indent=2)

        print(f"✓ Region activations (NPZ) salvos em: {filepath}")
        print(f"✓ Metadados (JSON) salvos em: {metadata_file}")
        print(f"  Total de regiões: {len(region_activations)}")
        return region_activations

    def save_samples_per_region(self, filename: str = "samples_per_region.json"):
        """Salva mapeamento de amostras por região em JSON."""
        samples_map = self.get_samples_per_region()

        # Converter chaves tupla para string (para JSON)
        samples_map_str_keys = {
            f"{layer}_{region}": samples
            for (layer, region), samples in samples_map.items()
        }

        filepath = self.output_dir / filename
        with open(filepath, "w") as f:
            json.dump(samples_map_str_keys, f, indent=2)

        print(f"✓ Samples per region salvos em: {filepath}")
        return samples_map

    def save_raw_activations_by_region_jsonl(
        self, filename: str = "raw_activations_by_region.jsonl"
    ):
        """
        Salva ativações brutas por região em JSONL (uma linha por região).
        Menos eficiente em espaço, mas fácil para inspeccionar.
        """
        region_activations = self.extract_region_activations()
        filepath = self.output_dir / filename

        with open(filepath, "w") as f:
            for (layer, region_id), activations_list in region_activations.items():
                line_data = {
                    "layer": layer,
                    "region_id": region_id,
                    "n_samples": len(activations_list),
                    "activations": [
                        {
                            "sample_id": int(act["sample_id"]),
                            "class_label": act["class_label"],
                            "activations": act["activations"].tolist(),
                        }
                        for act in activations_list
                    ],
                }
                f.write(json.dumps(line_data) + "\n")

        print(f"✓ Raw activations by region (JSONL) salvos em: {filepath}")
        return region_activations

    def get_region_statistics(self) -> pd.DataFrame:
        """Retorna estatísticas sobre distribuição de amostras por região."""
        assignments = self.extract_region_assignments()

        stats = (
            assignments.groupby(["layer", "region_id"])
            .agg(
                {"sample_id": "count", "class_label": lambda x: dict(x.value_counts())}
            )
            .reset_index()
        )

        stats.columns = ["layer", "region_id", "n_samples", "class_distribution"]

        return stats

    def save_all(self, format: str = "hdf5"):
        """
        Salva todos os dados extraídos.

        Parameters
        ----------
        format : str
            'hdf5' (recomendado) ou 'npz'
        """
        print("Extraindo e salvando dados de regiões neurais...")
        print("-" * 60)

        self.save_region_assignments()

        if format.lower() == "hdf5":
            self.save_region_activations_hdf5()
        elif format.lower() == "npz":
            self.save_region_activations_npz()
        else:
            raise ValueError(f"Format {format} não suportado. Use 'hdf5' ou 'npz'")

        self.save_samples_per_region()

        # Salvar também JSONL para inspeção visual
        # self.save_raw_activations_by_region_jsonl()

        # Salvar estatísticas
        stats = self.get_region_statistics()
        stats_file = self.output_dir / "region_statistics.csv"
        stats.to_csv(stats_file, index=False)

        print("-" * 60)
        print(f"✓ Todos os dados salvos em: {self.output_dir}")
        print(f"  Arquivos gerados:")
        print(f"    - region_assignments.csv (mapeamento amostra → região)")
        print(f"    - region_activations.{format} (ativações 768D por região)")
        print(f"    - samples_per_region.json (índice reverso)")
        print(f"    - raw_activations_by_region.jsonl (inspeção visual)")
        print(f"    - region_statistics.csv (estatísticas)")


# ============================================================================
# FUNÇÕES AUXILIARES PARA INTEGRAÇÃO FÁCIL
# ============================================================================


def extract_neural_region_data(
    llm_mri_object: ActivationAreas,
    output_dir: str = "./neural_region_data",
    format: str = "hdf5",
):
    """
    Função simplificada para extrair e salvar todos os dados de regiões.

    Parameters
    ----------
    llm_mri_object : ActivationAreas
        Objeto após process_activation_areas()
    output_dir : str
        Diretório para salvar arquivos
    format : str
        'hdf5' (recomendado) ou 'npz'

    Returns
    -------
    extractor : NeuralRegionExtractor
        Objeto com os dados extraídos

    Example
    -------
    from utils.neural_region_extraction import extract_neural_region_data

    llm_mri = ActivationAreas(...)
    llm_mri.process_activation_areas(...)

    extract_neural_region_data(llm_mri, format='hdf5')
    """
    extractor = NeuralRegionExtractor(llm_mri_object, output_dir)
    extractor.save_all(format=format)
    return extractor


# # HDF5
# import h5py

# with h5py.File('neural_region_data/region_activations.h5', 'r') as f:
#     layer_0_region_1 = f['layer_0_3_5']  # Acesso por chave
#     activations = layer_0_region_1['activations'][:]  # Array [n, 768]
#     sample_ids = layer_0_region_1['sample_ids'][:]

# # NPZ
# data = np.load('neural_region_data/region_activations.npz')
# # data.files = lista de regiões
# # data['region_0'] acessa os arrays
