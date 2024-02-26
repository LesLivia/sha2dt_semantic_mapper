from typing import List

from skg_main.skg_model.automata import Location, Edge
from skg_main.skg_model.schema import Entity, Activity


class Automaton_Feature:
    def __init__(self, l: Location = None, e: Edge = None):
        self.loc = l
        self.edge = e

    def __str__(self):
        if self.loc is not None and self.edge is None:
            return '{}'.format(self.loc.name)
        elif self.loc is None and self.edge is not None:
            return '{}'.format(self.edge.label)
        else:
            return '{}, {}'.format(self.loc.name, self.edge.label)


class SKG_Feature:
    def __init__(self, e: Entity = None, a: Activity = None):
        self.entity = e
        self.act = a

    def __str__(self):
        if self.entity is not None and self.act is None:
            return '{}'.format(self.entity.entity_id)
        elif self.entity is None and self.act is not None:
            return '{}'.format(self.act.act)
        else:
            return '{}, {}'.format(self.entity.entity_id, self.act.act)


class Link:
    def __init__(self, name: str, aut: List[Automaton_Feature], skg: List[SKG_Feature]):
        self.name = name
        self.aut_feat = aut
        self.skg_feat = skg

    def __str__(self):
        return '{} -[:{}]-> {}'.format(','.join([str(f) for f in self.aut_feat]), self.name,
                                       ','.join([str(f) for f in self.skg_feat]))
