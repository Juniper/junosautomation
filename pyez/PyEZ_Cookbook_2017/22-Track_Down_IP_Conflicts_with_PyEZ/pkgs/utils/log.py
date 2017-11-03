import logging.config
import os
from datetime import datetime

import yaml
from yamlordereddictloader import Loader


base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.realpath(__file__))))
conf_dir = os.path.join(base_dir, 'conf')
log_dir = os.path.join(base_dir, 'logs')
if not os.path.exists(log_dir):
    os.makedirs(log_dir)

with open(os.path.join(conf_dir, 'logging.yml')) as f:
    config_dict = yaml.load(f, Loader=Loader)
    config_dict['handlers']['file']['filename'] = os.path.join(
        log_dir, '{}.log'.format(datetime.now().isoformat('-')))
    logging.config.dictConfig(config_dict)
    handlers = logging.root.handlers
    logging.root.handlers = [logging.NullHandler()]

loggers_dict = {}


def reconfig(log_file):
    if not log_file:
        log_file = os.path.split(config_dict['handlers']['file']['filename'])[1]
    assert isinstance(log_file, str)
    old_path = config_dict['handlers']['file']['filename']
    new_path = os.path.join(os.path.split(old_path)[0], log_file)
    config_dict['handlers']['file']['filename'] = new_path
    logging.config.dictConfig(config_dict)
    global handlers
    handlers = logging.root.handlers
    logging.root.handlers = [logging.NullHandler()]
    for _, logger in loggers_dict.items():
        logger.handlers = handlers
        logger.disabled = False
        logger.propagate = False


def get_logger(name):
    if name not in loggers_dict:
        logger = logging.getLogger(name=name)
        logger.handlers = handlers
        logger.disabled = False
        logger.propagate = False
        loggers_dict[name] = logger

    return loggers_dict[name]
