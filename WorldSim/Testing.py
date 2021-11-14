"""
Testing

Version : v0.1
Author  : Christian Carter
Date    : 10/11/21

Code base for testing the various modules in WorldSim
"""

import logging
import unittest
from Entity import *
from Being import *

logging.basicConfig()
log = logging.getLogger(__name__)
log.setLevel(logging.INFO)

class TestEntity(unittest.TestCase):

    entityID = 0
    entityName = 'test entity'
    testEntity = Entity(entityID, entityName)

    def test_init(self):
        self.assertTrue(self.testEntity.id == self.entityID)
        self.assertTrue(self.testEntity.name == self.entityName)

    def test_return_funcs(self):
        self.assertTrue(self.testEntity.entity_id() == self.entityID)
        self.assertTrue(self.testEntity.entity_name() == self.entityName)
    
class TestEntityContainer(unittest.TestCase):

    entityID = 12
    entityName = 'test container'
    testContainer = EntityContainer(6, entityID, entityName)

    testEntity0 = Entity(0, 'test Entity')
    testEntity1 = Entity(1, 'test entity')
    testEntity2 = Entity(2, 'test entity')
    testEntity3 = Entity(3, 'test entity')
    testEntity4 = Entity(4, 'test entity')
    testEntity5 = Entity(0, 'test entity')
    master_dict = {
        0: [testEntity0, 2],
        1: [testEntity1, 1],
        2: [testEntity2, 1],
        3: [testEntity3, 1],
        4: [testEntity4, 1],
    }
        
    def test_add_entity(self):
        self.testContainer.add_entity(self.testEntity0)
        self.testContainer.add_entity(self.testEntity1)
        self.testContainer.add_entity(self.testEntity2)
        self.testContainer.add_entity(self.testEntity3)
        self.testContainer.add_entity(self.testEntity4)
        self.testContainer.add_entity(self.testEntity5)
        log.debug(self.testContainer.return_contents())
        log.debug(self.testContainer.entity_num)
        self.assertTrue(self.testContainer.return_contents() == self.master_dict)
    
    def test_container_full(self):
        testEntity6 = Entity(5, 'test entity')
        log.debug(self.testContainer.entity_num)
        try:
            self.testContainer.add_entity(testEntity6)
        except ContainerFull:
            self.assertTrue(True)
        except Exception as e:
            self.assertTrue(False)
        log.debug(self.testContainer.return_contents())
        log.debug(self.testContainer.entity_num)

    def test_remove_entity(self):
        del self.master_dict[1]
        self.testContainer.remove_entity(1)
        self.assertTrue(self.testContainer.return_contents() == self.master_dict)
        self.master_dict[0][1] -= 1
        self.testContainer.remove_entity(0)
        self.assertTrue(self.testContainer.return_contents() == self.master_dict)

    def test_take_entity(self):
        self.assertTrue(self.testContainer.take_entity(2) == self.testEntity2)
        del self.master_dict[2]
        self.assertTrue(self.master_dict == self.testContainer.return_contents())

    def test_nonexistant_entity(self):
        try:
            self.testContainer.remove_entity(45)
        except NonexistantEntity:
            self.assertTrue(True)
        except Exception as e:
            log.debug(e)
            self.assertTrue(False)

if __name__ == '__main__':
    unittest.main()