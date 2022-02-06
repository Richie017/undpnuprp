from enum import Enum


class ModelRelationType(Enum):
    NORMAL = 'normal'
    INVERTED = 'inverted'
    INTERMEDIATE_MODEL = 'intermediate_model'
    INVERTED_M2M = 'inverted_m2m'
    CUSTOM = 'custom'
