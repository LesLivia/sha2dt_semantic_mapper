import configparser
import json
from typing import List, Dict

import src.skg2automata.mgrs.skg_connector as conn
from it.polimi.semantic_mapper.logger.logger import Logger
from it.polimi.semantic_mapper.model.semantic_link import Link, Automaton_Feature, SKG_Feature
from src.skg2automata.mgrs.skg_reader import Skg_Reader
from src.skg2automata.model.automata import Automaton

LOGGER = Logger('Identifier')

config = configparser.ConfigParser()
config.read('resources/config/config.ini')
config.sections()
LINKS_PATH = config['LINKS']['links.config']
LINKS_CONFIG = json.load(open(LINKS_PATH))

AUTOMATON_NAME = config['AUTOMATON']['automaton.name']
AUTOMATON_META_PATH = config['AUTOMATON']['automaton.meta.path'].format(AUTOMATON_NAME)


class Identifier:
    def __init__(self, a: Automaton):
        self.automaton = a

    def identify_edge_links(self, to: str, name: str):
        edge_links: List[Link] = []
        labels_dict: Dict[str, str] = {}

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
        elif to.lower() == 'sensor':
            target_entities = reader.get_entities_by_labels(['Sensor'])

        for edge in self.automaton.edges:
            if to.lower() == 'activity':
                target = [e for e in target_entities if e.act == labels_dict[edge.label]]
            elif to.lower() == 'sensor':
                target = [e for e in target_entities if e.entity_id in labels_dict[edge.label]]

            if len(target) <= 0:
                LOGGER.error('Cannot establish link for {}.'.format(edge.label))
            else:
                auto_feat = Automaton_Feature(e=edge)
                if to.lower() == 'activity':
                    skg_feat = SKG_Feature(a=target[0])
                elif to.lower() == 'sensor':
                    skg_feat = SKG_Feature(e=target[0])
                edge_links.append(Link(name, [auto_feat], [skg_feat]))

        return edge_links

    def identify_semantic_links(self):
        links: List[Link] = []

        for mapping in LINKS_CONFIG['fixed_links']:
            if mapping['from'].lower() == 'edge':
                links.extend(self.identify_edge_links(mapping['to'], mapping['rel_name']))

        LOGGER.info('Identified {} semantic links.'.format(len(links)))

        return links
