"""
Entity

Version : v0.1
Author  : Christian Carter
Date    : 10/11/21

Base class for Entities. Characters, animals, items, etc., will all be using the Entity class
"""

import logging
from typing import Dict

logging.basicConfig()
log = logging.getLogger(__name__)
log.setLevel(logging.DEBUG)

class ContainerFull(Exception):
    def __init__(self, cls: 'Entity'):
        self.id = cls.id
        self.name = cls.name

    def __str__(self) -> str:
        return f"Container {self.id}:{self.name} is full"

class NonexistantEntity(Exception):
    def __init__(self, cls : 'Entity', entityID):
        self.id = cls.id
        self.name = cls.name
        self.entity = entityID
    
    def __str__(self) -> str:
        return f"Tried to remove {self.entity} from {self.id}:{self.name} but could not find it"

class Entity:

    def __init__(self, entityID: int, entityName : str, ):
        self.id : int = entityID
        self.name : str = entityName

    def entity_id(self) -> int:
        return self.id

    def entity_name(self) -> str:
        return self.name

class EntityContainer(Entity):

    def __init__(self, maxEntities : int, entityID : int, entityName : str):
        super().__init__(entityID, entityName)
        self.entities = {}
        self.entity_num = 0
        self.max = maxEntities

    def return_contents(self) -> Dict:
        return self.entities

    def add_entity(self, entity : Entity):
        if self.entity_num < self.max:
            if entity.id in self.entities.keys():    
                self.entities[entity.id][1] += 1
            else:
                self.entities[entity.id] = [entity, 1]
            self.entity_num += 1 
        else:
            raise ContainerFull(self)
            
    def remove_entity(self, entityID : int):
        try:
            if self.entities[entityID][1] == 1:
                del self.entities[entityID]
                self.entity_num -= 1
            else:
                self.entities[entityID][1] -= 1
                self.entity_num -= 1
        except KeyError:
            raise NonexistantEntity(self, entityID)

    def take_entity(self, entityID : int, ) -> Entity:
        to_return = self.entities[entityID][0]
        self.remove_entity(entityID)
        return to_return