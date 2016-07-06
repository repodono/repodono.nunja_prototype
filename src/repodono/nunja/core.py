from .registry import create_default_registry
from .engine import Engine


engine = Engine(create_default_registry(__name__))
engine.registry.init_entrypoints()
