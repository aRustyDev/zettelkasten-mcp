"""Base repository interface for data storage."""

import abc
from typing import Any, Generic, TypeVar

from pydantic import BaseModel

T = TypeVar("T", bound=BaseModel)


class Repository(Generic[T], abc.ABC):
    """Abstract base class for repositories."""

    @abc.abstractmethod
    def create(self, entity: T) -> T:
        """Create a new entity."""
        pass

    @abc.abstractmethod
    def get(self, id: str) -> T | None:
        """Get an entity by ID."""
        pass

    @abc.abstractmethod
    def get_all(self) -> list[T]:
        """Get all entities."""
        pass

    @abc.abstractmethod
    def update(self, entity: T) -> T:
        """Update an entity."""
        pass

    @abc.abstractmethod
    def delete(self, id: str) -> None:
        """Delete an entity by ID."""
        pass

    @abc.abstractmethod
    def search(self, **kwargs: Any) -> list[T]:
        """Search for entities based on criteria."""
        pass
