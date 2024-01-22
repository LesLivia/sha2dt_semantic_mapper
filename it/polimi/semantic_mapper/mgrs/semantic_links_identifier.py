import configparser
import json
from typing import List

from it.polimi.semantic_mapper.logger.logger import Logger
from it.polimi.semantic_mapper.model.semantic_link import Link
from src.skg2automata.model.automata import Automaton

LOGGER = Logger('Identifier')

config = configparser.ConfigParser()
config.read('resources/config/config.ini')
config.sections()
LINKS_PATH = config['LINKS']['links.config']
LINKS_CONFIG = json.load(open(LINKS_PATH))


class Identifier:
    def __init__(self, a: Automaton):
        self.automaton = a

    def identify_semantic_links(self):
        for mapping in LINKS_CONFIG['fixed_links']:
            print(mapping['from'], mapping['to'])

        links: List[Link] = []

        LOGGER.info('Identified {} semantic links.'.format(len(links)))

        return links
