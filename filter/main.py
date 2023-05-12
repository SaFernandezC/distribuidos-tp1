from configparser import ConfigParser
from src.Filter import Filter
import logging
import os
from dotenv import load_dotenv

load_dotenv()

CANTIDAD = int(os.getenv('CANT_CONDICIONES', 0))
SELECT = os.getenv('SELECT', None)
OPERATORS = os.getenv('OPERATORS', None)

INPUT_QUEUE = os.getenv('INPUT_QUEUE', None)
INPUT_EXCHANGE = os.getenv('INPUT_EXCHANGE', None)
INPUT_EXCHANGE_TYPE = os.getenv('INPUT_EXCHANGE_TYPE', None)
INPUT_BIND = True if os.getenv('INPUT_BIND') == "True" else False

OUTPUT_EXCHANGE = os.getenv('OUTPUT_EXCHANGE', None)
OUTPUT_EXCHANGE_TYPE = os.getenv('OUTPUT_EXCHANGE_TYPE', None)
OUTPUT_QUEUE_NAME = os.getenv('OUTPUT_QUEUE_NAME', None)

SHOW_LOGS =  True if os.getenv("SHOW_LOGS") == "True" else False


def initialize_config():
    config = ConfigParser(os.environ)
    # If config.ini does not exists original config object is not modified
    config.read("config.ini")

    config_params = {}
    try:
        config_params["logging_level"] = os.getenv('LOGGING_LEVEL', config["DEFAULT"]["LOGGING_LEVEL"])
    except KeyError as e:
        raise KeyError("Key was not found. Error: {} .Aborting packet-distributor".format(e))
    except ValueError as e:
        raise ValueError("Key could not be parsed. Error: {}. Aborting packet-distributor".format(e))

    return config_params


def main():
    config_params = initialize_config()
    logging_level = config_params["logging_level"]

    initialize_log(logging_level)

    # Log config parameters at the beginning of the program to verify the configuration
    # of the component
    logging.debug(f"action: config | result: success | logging_level: {logging_level}")

    raw_filters = []
    for i in range(CANTIDAD):
        raw_filters.append(os.getenv('FILTER_'+str(i)))

    try:
        filter = Filter(SELECT, raw_filters, CANTIDAD, OPERATORS, INPUT_EXCHANGE, INPUT_EXCHANGE_TYPE, INPUT_QUEUE,
                        OUTPUT_EXCHANGE, OUTPUT_EXCHANGE_TYPE, OUTPUT_QUEUE_NAME)
        filter.run()
    except OSError as e:
        logging.error(f'action: initialize_distance_calculator | result: fail | error: {e}')

def initialize_log(logging_level):
    """
    Python custom logging initialization

    Current timestamp is added to be able to identify in docker
    compose logs the date when the log has arrived
    """
    logging.basicConfig(
        format='%(asctime)s %(levelname)-8s %(message)s',
        level=logging_level,
        datefmt='%Y-%m-%d %H:%M:%S',
    )


if __name__ == "__main__":
    main()
