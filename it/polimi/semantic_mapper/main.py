import configparser

from it.polimi.semantic_mapper.logger.logger import Logger
from it.polimi.semantic_mapper.mgrs.semantic_links_identifier import Identifier
from src.skg2automata.model.automata import Automaton

config = configparser.ConfigParser()
config.read('resources/config/config.ini')
config.sections()
AUTOMATON_NAME = config['AUTOMATON']['automaton.name']
AUTOMATON_PATH = config['AUTOMATON']['automaton.graph.path'].format(AUTOMATON_NAME)

LOGGER = Logger('Main')

AUTOMATON = Automaton(AUTOMATON_PATH)

LOGGER.info('Loaded automaton.')

links_identifier = Identifier(AUTOMATON)
links = links_identifier.identify_semantic_links()

LOGGER.info('Done.')
