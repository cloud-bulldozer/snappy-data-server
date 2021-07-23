from vyper import v
import dataclasses
from typing import Iterable

@dataclasses.dataclass
class PruneConfig:
    path: str
    days_to_live: int

@dataclasses.dataclass
class Config:
    prune_configs: Iterable[PruneConfig]
    def __post_init__(self):
        self.prune_configs = (PruneConfig(**c) for c in self.prune_configs)

def get_config() -> Config:
    v.set_config_name('pruner_config')
    v.add_config_path('.')
    v.read_in_config()
    return Config(
        prune_configs=v.get('pruner'))
