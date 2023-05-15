from configparser import ConfigParser
from src.date_modifier import DateModifier
import logging
import os


def initialize_config():
    config = ConfigParser(os.environ)
    # If config.ini does not exists original config object is not modified
    config.read("config.ini")

    config_params = {}
    try:
        config_params["logging_level"] = config.get("DEFAULT", "LOGGING_LEVEL", fallback=None)
        config_params["input_queue_name"] = config.get("DEFAULT", "INPUT_QUEUE_NAME", fallback=None)
        config_params["output_exchange"] = config.get("DEFAULT", "OUTPUT_EXCHANGE", fallback=None)
        config_params["output_exchange_type"] = config.get("DEFAULT", "OUTPUT_EXCHANGE_TYPE", fallback=None)

    except KeyError as e:
        raise KeyError("Key was not found. Error: {} .Aborting packet-distributor".format(e))
    except ValueError as e:
        raise ValueError("Key could not be parsed. Error: {}. Aborting packet-distributor".format(e))

    return config_params


def main():
    config_params = initialize_config()
    logging_level = config_params["logging_level"] 
    input_queue_name = config_params["input_queue_name"]
    output_exchange = config_params["output_exchange"]
    output_exchange_type = config_params["output_exchange_type"]

    initialize_log(logging_level)

    # Log config parameters at the beginning of the program to verify the configuration
    # of the component
    logging.debug(f"action: config | result: success | logging_level: {logging_level}")

    try:
        date_modifier = DateModifier(input_queue_name, output_exchange, output_exchange_type)
        date_modifier.run()
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
