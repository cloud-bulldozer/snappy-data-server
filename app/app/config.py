import dataclasses
from pathlib import Path

from vyper import v


@dataclasses.dataclass
class Config:
    pruner_path: Path
    days_to_live: int = 14
    pruner_enabled: bool = False
    

def get_config() -> Config:
    v.set_config_name('snappy')
    v.add_config_path('.') 
    v.read_in_config()
    return Config(
        pruner_path=Path(v.get('pruner.path')),
        days_to_live=v.get('pruner.days_to_live'),
        pruner_enabled=v.get('pruner.enabled')
    )
