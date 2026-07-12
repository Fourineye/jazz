from typing import Iterator
from .base_object import GameObject


# TODO Rework "Group" into some other tag type system

class Group:
    """A container for Entities that allows for checking of collisions and other methods"""

    def __init__(self, initial_items: list[GameObject] | None = None, name: str = "group") -> None:
        """Initializes the Group container.

        Args:
            initial_items (list[GameObject], optional): Initial list of game objects to populate the group with.
            name (str, optional): The name of the group. Defaults to "group".
        """
        self.name = name
        self._entities = []
        if initial_items:
            self.add_entities(initial_items)

    def __len__(self) -> int:
        return len(self._entities)

    def __iter__(self) -> Iterator[GameObject]:
        return iter(self._entities)

    def __getitem__(self, i: int) -> GameObject:
        return self._entities[i]

    def __setitem__(self, i: int, val: GameObject) -> None:
        self._entities[i] = val

    def __delitem__(self, i: int) -> None:
        self.remove(self._entities[i])

    def __contains__(self, key: GameObject) -> bool:
        return key in self._entities

    def add(self, entity: GameObject) -> None:
        """
        Add an Entity to the group and ensure that the group is referenced
        in the entity's groups attribute.

        Args:
            entity (Entity): The entity to be added to the group.
        """
        if not isinstance(entity, GameObject):
            raise ValueError("Only Entity objects may be added to an EntityGroup")
        if entity not in self._entities:
            self._entities.append(entity)
            if self not in entity.groups:
                entity.add_group(self)
        else:
            print("Entity already in group")

    def remove(self, entity: GameObject) -> None:
        """
        Remove an Entity from the group and ensure that the group is no longer
        referenced in the entity's groups attribute.

        Args:
            entity (Entity): The entity to be removed to the group.
        """
        if entity not in self._entities:
            print("Entity not in group")
        else:
            if self in entity.groups:
                entity.remove_group(self)
            self._entities.remove(entity)

    def add_entities(self, entities: list[GameObject]) -> None:
        """
        Iterates through a list of Entities and adds them to the group.

        Args:
            entities (list): List of entities to be added to the group.
        """
        for entity in entities:
            self.add(entity)
