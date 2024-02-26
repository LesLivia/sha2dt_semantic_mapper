import configparser
import os

import skg_main.skg_mgrs.connector_mgr as conn
from semantic_logger.logger import Logger
from semantic_mgrs.semantic_links_identifier import Identifier
from skg_main.skg_mgrs.skg_writer import Skg_Writer
from skg_main.skg_model.automata import Automaton

config = configparser.ConfigParser()
if 'submodules' in os.listdir():
    curr_path = os.getcwd() + '/submodules/sha2dt_semantic_mapper'
else:
    curr_path = os.getcwd().split('src/sha2dt_semantic_mapper')[0]
config.read('{}/resources/config/config.ini'.format(curr_path))
config.sections()

LOGGER = Logger('Main')


def write_semantic_links(name: str = None):
    AUTOMATON_NAME = config['AUTOMATON']['automaton.name']

    if name is None:
        name = AUTOMATON_NAME

    AUTOMATON_PATH = config['AUTOMATON']['automaton.graph.path'].format(name)

    AUTOMATON = Automaton(name, AUTOMATON_PATH)

    LOGGER.info('Loaded automaton.')

    links_identifier = Identifier(AUTOMATON)
    links = links_identifier.identify_semantic_links(name)

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

    LOGGER.info('Done creating semantic links.')
