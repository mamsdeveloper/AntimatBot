from pathlib import Path
from typing import Generic, Type, TypeAlias, TypeVar

from pydantic import BaseModel, TypeAdapter


class BaseStorageModel(BaseModel):
    key: str


T = TypeVar('T', bound=BaseStorageModel)
Models: TypeAlias = dict[str, T]


class JsonStorage(Generic[T]):
    def __init__(self, model_type: Type[T], storage_path: Path) -> None:
        self.storage_path = storage_path
        self.model_type = model_type
        self.models_adapter = TypeAdapter(Models[model_type])

    def get(self, key: str) -> T | None:
        models = self._load()
        return models.get(key)

    def get_all(self) -> list[T]:
        models = self._load()
        return list(models.values())

    def save(self, model: T) -> None:
        models = self._load()
        models[model.key] = model
        self._dump(models)

    def delete(self, key: str) -> T | None:
        models = self._load()
        model = models.pop(key, None)
        self._dump(models)
        return model

    def _load(self) -> Models[T]:
        if not self.storage_path.exists():
            return {}

        return self.models_adapter.validate_json(self.storage_path.read_bytes())

    def _dump(self, models: Models) -> None:
        self.storage_path.write_bytes(self.models_adapter.dump_json(models))
