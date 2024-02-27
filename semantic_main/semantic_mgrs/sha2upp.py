import configparser
import os
from typing import List, Dict

from semantic_main.semantic_logger.logger import Logger
from semantic_main.semantic_model.semantic_link import Link
from semantic_main.semantic_model.sha import SHA, Edge, Location

config = configparser.ConfigParser()
config.sections()
config.read('{}/config/config.ini'.format(os.environ['SEM_RES_PATH']))
config.sections()

N = 10
TAU = 10

LOGGER = Logger('UppaalModelGenerator')

NTA_TPLT_PATH = config['MODEL GENERATION']['tplt.path']
NTA_TPLT_NAME = 'nta_template.xml'
MACHINE_TPLT_NAME = 'sha_template.xml'

LOCATION_TPLT = """<location id="{}" x="{}" y="{}">\n\t<name x="{}" y="{}">{}</name>\n
<label kind="exponentialrate" x="{}" y="{}">1</label>
</location>\n"""

QUERY_TPLT = """E[<=TAU;{}](max: m_1.E)\nsimulate[<=TAU; {}]{m_1.w, m_1.P, m_1.E}"""

X_START = 0
X_MAX = 900
X_RANGE = 300
Y_START = 0
Y_RANGE = 300

EDGE_TPLT = """<transition>\n\t<source ref="{}"/>\n\t<target ref="{}"/>
\t<label kind="synchronisation" x="{}" y="{}">{}</label>\n
\t<label kind="assignment" x="{}" y="{}">update_entities({}, {})</label>\n
</transition>"""

SAVE_PATH = config['MODEL GENERATION']['save.path']


def process_links(links: List[Link], edge: Edge, target: Location,
                  entity_to_int: Dict[str, int]):
    sync = edge.sync.replace('!', '')
    loc_entity = 1
    edge_entity = 1
    for link in links:
        link_edge = link.aut_feat[0].edge
        link_loc = link.aut_feat[0].loc
        link_entity = link.skg_feat[0].entity
        if link_edge is not None and link_edge.label == sync:
            edge_entity = entity_to_int[link_entity.entity_id]
        if link_loc is not None and target.name == link_loc.name:
            loc_entity = entity_to_int[link_entity.entity_id]

    return loc_entity, edge_entity


def get_dicts(links: List[Link]):
    ent_list = list(set([link.skg_feat[0].entity.entity_id for link in links]))
    return {x: i for i, x in enumerate(ent_list)}


def sha_to_upp_tplt(learned_sha: SHA, links: List[Link]):
    machine_path = NTA_TPLT_PATH + MACHINE_TPLT_NAME
    with open(machine_path, 'r') as machine_tplt:
        lines = machine_tplt.readlines()
        learned_sha_tplt = ''.join(lines)

    locations_str = ''
    x = X_START
    y = Y_START
    for loc in learned_sha.locations:
        new_loc_str = LOCATION_TPLT.format('id' + str(loc.id), x, y, x, y - 20, loc.name, x, y - 30, x, y - 35)

        loc.x = x
        loc.y = y
        locations_str += new_loc_str

        if loc.initial:
            learned_sha_tplt = learned_sha_tplt.replace('**INIT_ID**', 'id' + str(loc.id))

        if x < X_MAX:
            x = x + X_RANGE
        else:
            x = X_START
            y = y + Y_RANGE
    learned_sha_tplt = learned_sha_tplt.replace('**LOCATIONS**', locations_str)

    edges_str = ''
    for edge in learned_sha.edges:
        start_id = 'id' + str(edge.start.id)
        dest_id = 'id' + str(edge.dest.id)
        x1, y1, x2, y2 = edge.start.x, edge.start.y, edge.dest.x, edge.dest.y
        mid_x = abs(x1 - x2) / 2 + min(x1, x2)
        mid_y = abs(y1 - y2) / 2 + min(y1, y2)

        link_params = process_links(links, edge, edge.dest, get_dicts(links))
        new_edge_str = EDGE_TPLT.format(start_id, dest_id, mid_x, mid_y, edge.sync, mid_x,
                                        mid_y + 10, link_params[0], link_params[1])
        edges_str += new_edge_str
    learned_sha_tplt = learned_sha_tplt.replace('**TRANSITIONS**', edges_str)

    entity_dict = ['{}: {}'.format(x, get_dicts(links)[x]) for x in get_dicts(links)]
    learned_sha_tplt = learned_sha_tplt.replace('**DICT**', '\n'.join(entity_dict))

    return learned_sha_tplt


def generate_query_file(name: str):
    with open(SAVE_PATH + name + '.q', 'w') as q_file:
        q_file.write(QUERY_TPLT.replace('{}', str(N)))


def generate_upp_model(learned_sha: SHA, name: str, links: List[Link]):
    LOGGER.info("Starting Uppaal semantic_model generation...")

    # Learned SHA Management

    learned_sha_tplt = sha_to_upp_tplt(learned_sha, links)

    nta_path = NTA_TPLT_PATH + NTA_TPLT_NAME
    with open(nta_path, 'r') as nta_tplt:
        lines = nta_tplt.readlines()
        nta_tplt = ''.join(lines)

    unique_syncs = list(set([e.sync.replace('!', '') for e in learned_sha.edges]))
    nta_tplt = nta_tplt.replace('**CHANNELS**', ','.join(unique_syncs))
    nta_tplt = nta_tplt.replace('**MONITORS**', ','.join(['s.' + l.name for l in learned_sha.locations]))

    nta_tplt = nta_tplt.replace('**MACHINE**', learned_sha_tplt)
    nta_tplt = nta_tplt.replace('**TAU**', str(TAU))

    with open(SAVE_PATH + name + '.xml', 'w') as new_model:
        new_model.write(nta_tplt)

    LOGGER.info('Uppaal semantic_model successfully created.')

    generate_query_file(name)

    LOGGER.info('Uppaal query file successfully created.')
