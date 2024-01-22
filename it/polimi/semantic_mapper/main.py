import src.skg2automata.mgrs.skg_connector as conn
from src.skg2automata.mgrs.skg_reader import Skg_Reader
from it.polimi.semantic_mapper.logger.logger import Logger
from src.skg2automata.model.automata import Automaton
from it.polimi.semantic_mapper.mgrs.semantic_links_identifier import Identifier
import configparser

config = configparser.ConfigParser()
config.read('resources/config/config.ini')
config.sections()
AUTOMATON_PATH = config['AUTOMATON']['automaton.path']

LOGGER = Logger('Main')

AUTOMATON = Automaton(AUTOMATON_PATH)

LOGGER.info('Loaded automaton.')

links_identifier = Identifier(AUTOMATON)
links = links_identifier.identify_semantic_links()

driver = conn.get_driver()
reader: Skg_Reader = Skg_Reader(driver)
unique_events = reader.get_activities()

print(unique_events[0].act)

LOGGER.info('Done.')
