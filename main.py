import configparser

import skg_main.skg_mgrs.connector_mgr as conn
from semantic_main.semantic_logger.logger import Logger
from semantic_main.semantic_mgrs.dot2sha import parse_sha
from semantic_main.semantic_mgrs.semantic_links_identifier import Identifier
from semantic_main.semantic_mgrs.sha2upp import generate_upp_model
from skg_main.skg_mgrs.skg_writer import Skg_Writer
from skg_main.skg_model.automata import Automaton

config = configparser.ConfigParser()
config.read('resources/config/config.ini')
config.sections()
AUTOMATON_NAME = config['AUTOMATON']['automaton.name']
AUTOMATON_PATH = config['AUTOMATON']['automaton.graph.path'].format(AUTOMATON_NAME)

LOGGER = Logger('Main')

AUTOMATON = Automaton("AUTO_TWIN_SKG_501_source", AUTOMATON_PATH)

LOGGER.info('Loaded automaton.')

links_identifier = Identifier(AUTOMATON)
links = links_identifier.identify_semantic_links()

driver = conn.get_driver()
writer: Skg_Writer = Skg_Writer(driver)

# for link in links:
#     if link.aut_feat[0].edge is not None:
#         writer.create_semantic_link(AUTOMATON, name=link.name, edge=link.aut_feat[0].edge,
#                                     ent=link.skg_feat[0].entity, entity_labels=['Sensor'])
#     else:
#         writer.create_semantic_link(AUTOMATON, name=link.name, loc=link.aut_feat[0].loc,
#                                     ent=link.skg_feat[0].entity, entity_labels=['Station'])

driver.close()

sha = parse_sha(AUTOMATON_PATH, AUTOMATON_NAME)
generate_upp_model(sha, AUTOMATON_NAME, links)

LOGGER.info('Done.')
