import configparser
import json
import os
import sys
from typing import List, Dict, Tuple, Any

import skg_main.skg_mgrs.connector_mgr as conn
from skg_main.skg_mgrs.skg_reader import Skg_Reader
from skg_main.skg_model.automata import Automaton, Location

from semantic_main.semantic_logger.logger import Logger
from semantic_main.semantic_model.semantic_link import Link, Automaton_Feature, SKG_Feature

LOGGER = Logger('Identifier')

config = configparser.ConfigParser()
config.read(
    os.path.dirname(os.path.abspath(__file__)).split('semantic_main')[0] + 'semantic_main/resources/config/config.ini')


class Identifier:
    def setup(self):
        LINKS_PATH = config['LINKS']['links.config'].format(
            os.path.dirname(os.path.abspath(__file__)).split('semantic_main')[0] + 'semantic_main/',
            os.environ['NEO4J_SCHEMA'])
        LINKS_CONFIG = json.load(open(LINKS_PATH))

        return LINKS_CONFIG

    def __init__(self, a: Automaton):
        self.automaton = a
        self.LINKS_CONFIG = self.setup()

    def identify_edge_links(self, to: str, name: str, format_str: str, automaton_name: str = None,
                            to_attr=None, path=None):
        edge_links: List[Link] = []
        labels_dict: Dict[str, str] = {}

        if automaton_name is None:
            AUTOMATON_NAME = sys.argv[1]
        else:
            AUTOMATON_NAME = automaton_name

        AUTOMATON_META_PATH = config['AUTOMATON']['automaton.meta.path'].format(path, AUTOMATON_NAME)

        with open(AUTOMATON_META_PATH) as auto_meta:
            lines = auto_meta.readlines()
            start_index = lines.index('--EVENT LABELS DICT--\n')
            end_index = lines.index('--OBSERVABLE EVENTS--\n')
            lines = lines[start_index:end_index]

            for line in lines:
                if ':' in line:
                    fields = line.split(':')
                    labels_dict[fields[0].replace(' ', '').lower()] = fields[1][1:].replace('\n', '')

        driver = conn.get_driver()
        reader: Skg_Reader = Skg_Reader(driver)
        if to.lower() == 'activity':
            target_entities = reader.get_activities()
        else:
            target_entities = reader.get_entities_by_labels([to])

        for edge in self.automaton.edges:
            if to.lower() == 'activity':
                target = [e for e in target_entities if e.act == labels_dict[edge.label]]
            else:
                if to_attr is None:
                    target = [e for e in target_entities if format_str.format(e.entity_id) == labels_dict[edge.label]]
                else:
                    target = [e for e in target_entities if
                              format_str.format(e.extra_attr[to_attr]) == labels_dict[edge.label]]

            if len(target) <= 0:
                LOGGER.error('Cannot establish link for {}.'.format(edge.label))
            else:
                auto_feat = Automaton_Feature(e=edge)
                if to.lower() == 'activity':
                    skg_feat = SKG_Feature(a=target[0])
                else:
                    skg_feat = SKG_Feature(e=target[0])
                edge_links.append(Link(name, [auto_feat], [skg_feat]))

        driver.close()
        return edge_links

    def identify_location_links(self, to: str, name: str, edge_to: str, edge_links: List[Link]):
        loc_links: List[Link] = []

        driver = conn.get_driver()
        reader: Skg_Reader = Skg_Reader(driver)

        loc_to_act: List[Tuple[Location, Any]] = []

        for loc in self.automaton.locations:
            for edge in self.automaton.edges:
                # TODO: This only works with the automaton learned with the 'item' POV.
                # TODO: Semantic links for other POVs yet to be conceptualized/developed.
                if edge.target.name == loc.name:
                    for link in edge_links:
                        edge_2 = link.aut_feat[0].edge
                        if edge_2.target == edge.target and edge_2.source == edge.source and edge_2.label == edge.label:
                            if link.skg_feat[0].act is not None:
                                loc_to_act.append((loc, link.skg_feat[0].act))
                            else:
                                loc_to_act.append((loc, link.skg_feat[0].entity))
                            break
                    break

        for pair in loc_to_act:
            if edge_to.lower() == 'activity':
                target_entity = reader.get_related_entities(edge_to, to, filter1=pair[1].act, limit=1)[0][0]
                loc_links.append(Link(name, [Automaton_Feature(l=pair[0])], [SKG_Feature(a=target_entity)]))
            else:
                target_entity = reader.get_related_entities(edge_to, to, filter1=pair[1].entity_id, limit=1)[0][0]
                loc_links.append(Link(name, [Automaton_Feature(l=pair[0])], [SKG_Feature(e=target_entity)]))

        return loc_links

    def identify_semantic_links(self, automaton_name: str = None, path=None):
        links: List[Link] = []
        edge_links: List[Link] = []
        edge_to = None

        for mapping in self.LINKS_CONFIG['fixed_links']:
            if mapping['from'].lower() == 'edge':
                edge_to = mapping['to']
                if 'to_attr' in mapping:
                    edge_links = self.identify_edge_links(mapping['to'], mapping['rel_name'], mapping['format'],
                                                          automaton_name, mapping['to_attr'], path)
                else:
                    edge_links = self.identify_edge_links(mapping['to'], mapping['rel_name'], mapping['format'],
                                                          automaton_name, path=path)
                links.extend(edge_links)
            elif mapping['from'].lower() == 'location':
                links.extend(self.identify_location_links(mapping['to'], mapping['rel_name'], edge_to, edge_links))

        LOGGER.info('Identified {} semantic links.'.format(len(links)))

        return links
