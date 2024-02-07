import configparser

import src.skg2automata.mgrs.skg_connector as conn
from it.polimi.semantic_mapper.logger.logger import Logger
from it.polimi.semantic_mapper.mgrs.semantic_links_identifier import Identifier
from src.skg2automata.mgrs.skg_writer import Skg_Writer
from src.skg2automata.model.automata import Automaton

config = configparser.ConfigParser()
config.read('resources/config/config.ini')
config.sections()
AUTOMATON_NAME = config['AUTOMATON']['automaton.name']
AUTOMATON_PATH = config['AUTOMATON']['automaton.graph.path'].format(AUTOMATON_NAME)

LOGGER = Logger('Main')

AUTOMATON = Automaton("AUTO_TWIN_SKG_301_source", AUTOMATON_PATH)

LOGGER.info('Loaded automaton.')

links_identifier = Identifier(AUTOMATON)
links = links_identifier.identify_semantic_links()

driver = conn.get_driver()
writer: Skg_Writer = Skg_Writer(driver)

for link in links:
    if link.aut_feat[0].edge is not None:
        writer.create_semantic_link(AUTOMATON, name=link.name, edge=link.aut_feat[0].edge,
                                    ent=link.skg_feat[0].entity, entity_labels=['Sensor'])
    else:
        writer.create_semantic_link(AUTOMATON, name=link.name, loc=link.aut_feat[0].loc,
                                    ent=link.skg_feat[0].entity, entity_labels=['Station'])

driver.close()

LOGGER.info('Done.')
