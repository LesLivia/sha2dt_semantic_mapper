import src.skg2automata.mgrs.skg_connector as conn
from src.skg2automata.mgrs.skg_reader import Skg_Reader

driver = conn.get_driver()
reader: Skg_Reader = Skg_Reader(driver)
unique_events = reader.get_activities()

print(unique_events[0].act)
