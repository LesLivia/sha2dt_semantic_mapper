import configparser
import json
import os

import skg_main.skg_mgrs.connector_mgr as conn
from semantic_main.semantic_logger.logger import Logger
from semantic_main.semantic_mgrs.semantic_links_identifier import Identifier
from skg_main.skg_mgrs.skg_writer import Skg_Writer
from skg_main.skg_model.automata import Automaton

config = configparser.ConfigParser()
config.read('{}/config/config.ini'.format(os.environ['SEM_RES_PATH']))
config.sections()

LOGGER = Logger('Main')

config = configparser.ConfigParser()
config.read('{}/config/config.ini'.format(os.environ['SEM_RES_PATH']))

LINKS_PATH = config['LINKS']['links.config'].format(os.environ['SEM_RES_PATH'], os.environ['NEO4J_SCHEMA'])
LINKS_CONFIG = json.load(open(LINKS_PATH))


def write_semantic_links(name: str = None, pov: str = None, start=None, end=None):
    AUTOMATON_NAME = config['AUTOMATON']['automaton.name']

    if name is None:
        name = AUTOMATON_NAME

    AUTOMATON_PATH = config['AUTOMATON']['automaton.graph.path'].format(os.environ['RES_PATH'], name)

    AUTOMATON = Automaton(name, AUTOMATON_PATH)

    LOGGER.info('Loaded automaton.')

    links_identifier = Identifier(AUTOMATON)
    links = links_identifier.identify_semantic_links(name)

    driver = conn.get_driver()
    writer: Skg_Writer = Skg_Writer(driver)

    for link in links:
        if link.aut_feat[0].edge is not None:
            writer.create_semantic_link(AUTOMATON, name=link.name, edge=link.aut_feat[0].edge,
                                        ent=link.skg_feat[0].entity,
                                        entity_labels=[LINKS_CONFIG['fixed_links'][0]['to']],
                                        pov=pov, start=start, end=end)
        else:
            writer.create_semantic_link(AUTOMATON, name=link.name, loc=link.aut_feat[0].loc,
                                        ent=link.skg_feat[0].entity,
                                        entity_labels=[LINKS_CONFIG['fixed_links'][1]['to']],
                                        pov=pov, start=start, end=end)

    driver.close()

    LOGGER.info('Done creating semantic links.')
