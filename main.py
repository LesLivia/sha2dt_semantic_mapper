import configparser
import os
import sys

from semantic_main.semantic_logger.logger import Logger
from semantic_main.semantic_mgrs.dot2sha import parse_sha
from semantic_main.semantic_mgrs.semantic_links_identifier import Identifier
from semantic_main.semantic_mgrs.sha2upp import generate_upp_model
from skg_main.skg_model.automata import Automaton

config = configparser.ConfigParser()
config.read('resources/config/config.ini')
config.sections()
AUTOMATON_NAME = sys.argv[1]
AUTOMATON_START, AUTOMATON_END = sys.argv[2], sys.argv[3]
AUTOMATON_PATH = config['AUTOMATON']['automaton.graph.path'].format(os.environ['RES_PATH'],
                                                                    AUTOMATON_NAME)

LOGGER = Logger('Main')

AUTOMATON = Automaton(sys.argv[1], AUTOMATON_PATH)

LOGGER.info('Loaded automaton.')

links_identifier = Identifier(AUTOMATON)
links = links_identifier.identify_semantic_links(sys.argv[1])

sha = parse_sha(AUTOMATON_PATH, AUTOMATON_NAME)
generate_upp_model(sha, AUTOMATON_NAME, AUTOMATON_START, AUTOMATON_END, links)

LOGGER.info('Done.')
