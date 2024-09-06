import configparser
import os
from datetime import datetime

import matplotlib.pyplot as plt
import numpy as np

from semantic_main.semantic_mgrs.sha2upp import generate_upp_model, get_time_distr, get_dicts

config = configparser.ConfigParser()
config.read(
    os.path.dirname(os.path.abspath(__file__)).split('semantic_main')[0] + 'semantic_main/resources/config/config.ini')
config.sections()

SCRIPT_PATH = config['UPPAAL SETTINGS']['UPPAAL_SCRIPT_PATH']
UPPAAL_PATH = config['UPPAAL SETTINGS']['UPPAAL_PATH']
UPPAAL_OUT_PATH = config['UPPAAL SETTINGS']['UPPAAL_OUT_PATH']
BIN_W = float(config['UPPAAL SETTINGS']['HIST_W'])


def generate_uppaal_model(sha, AUTOMATON_NAME, AUTOMATON_START, AUTOMATON_END, links):
    generate_upp_model(sha, AUTOMATON_NAME, AUTOMATON_START, AUTOMATON_END, links)


def get_ts():
    ts = datetime.now()
    ts_split = str(ts).split('.')[0]
    ts_str = ts_split.replace('-', '_')
    ts_str = ts_str.replace(' ', '_')
    return ts_str


def run_exp(name, model_path, query_path):
    res_name = name + '_' + get_ts()
    os.system('{} {} {} {} {} {}'.format(SCRIPT_PATH, UPPAAL_PATH, model_path, query_path,
                                         UPPAAL_OUT_PATH.format(res_name), BIN_W))
    return UPPAAL_OUT_PATH.format(res_name)


def validate_uppaal_model(name, model_path, query_path, links, start, end):
    time_distrs = dict()
    res_dict = get_dicts(links)
    for link in links:
        if link.aut_feat[0].loc is not None:
            time_distrs[res_dict[link.skg_feat[0].entity.entity_id]] = get_time_distr(name, start, end,
                                                                                      link.aut_feat[0].loc.name)

    with open(query_path) as q:
        lines = q.readlines()
        entity_order = [int(l.split('Tcdf[')[1].replace('])\n', '')) for l in lines]

    out_file = run_exp(name, model_path, query_path)

    with open(out_file) as f:
        lines = f.readlines()
        lines = [l for l in lines if l.startswith('Values in')]
        upp_ecdfs = [(l.split(' mean')[0].replace('Values in ', ''), l.split(': ')[1]) for l in lines]
        upp_ecdfs = [(x[0].replace('[', '').replace(']', ''),
                      x[1].split(' ')) for x in upp_ecdfs]
        upp_ecdfs = [(list(np.arange(float(x[0].split(',')[0]), float(x[0].split(',')[1]), BIN_W)),
                      [float(y) for y in x[1]]) for x in upp_ecdfs]
        upp_ecdfs = [(x[0], [sum(x[1][:i + 1]) / sum(x[1]) for i, y in enumerate(x[1])]) for x in upp_ecdfs]

        for i, x in enumerate(upp_ecdfs):
            if len(x[1]) < len(x[0]):
                x[1].append(x[1][-1])
            if len(x[0]) < len(x[1]):
                x[0].append(x[0][-1] + BIN_W)

            skg_distr = time_distrs[entity_order[i]]

            plt.figure()
            plt.plot(x[0], x[1], label='uppaal')
            plt.plot(skg_distr[2], skg_distr[3], label='skg')
            plt.title(entity_order[i])
            plt.legend()
            plt.show()

    return run_exp(name, model_path, query_path)
