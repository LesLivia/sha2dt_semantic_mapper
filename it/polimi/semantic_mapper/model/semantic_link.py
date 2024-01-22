from typing import List

from src.skg2automata.model.automata import Location, Edge
from src.skg2automata.model.schema import Entity, Activity


class Automaton_Feature:
    def __init__(self, l: Location = None, e: Edge = None):
        self.loc = l
        self.edge = e


class SKG_Feature:
    def __init__(self, e: Entity = None, a: Activity = None):
        self.entity = e
        self.act = a


class Link:
    def __init__(self, aut: List[Automaton_Feature], skg: List[SKG_Feature]):
        self.aut_feat = aut
        self.skg_feat = skg
