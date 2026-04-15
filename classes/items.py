# -*- coding: utf-8 -*-
"""
Handles items including battle items, held items, and overworld items
"""

class item:
    def __init__(self, name, itemtype, effects):
        self.name = name
        self.itemtype = itemtype
        self.effects = effects