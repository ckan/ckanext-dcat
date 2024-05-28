
from .extract import extract
from pathlib import Path

high_value_dataset_category = extract(Path(__file__).parent / 'high-value-dataset-category.rdf')


__all__ = ['high_value_dataset_category']
