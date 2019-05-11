from argparse       import ArgumentParser
from logging        import Formatter, StreamHandler, getLogger, DEBUG, INFO

from .controller    import Controller
from .paint_state   import PaintState


VERSION = "2.0.7"
APPLICATION_NAME = "PyPaint"
APPLICATION_DESCRIPTION = "Simple, networked paint application"

LOG_FORMAT = "%(asctime)s::%(name)s::%(levelname)s::%(message)s"
TIMESTAMP_FORMAT = "%H:%M:%S"


def create_logger(debug_level):
    logger = getLogger()
    logger.setLevel(debug_level)

    std_err = StreamHandler()
    std_err.setLevel(debug_level)
    std_err.setFormatter(Formatter(LOG_FORMAT, TIMESTAMP_FORMAT))

    logger.addHandler(std_err)
    return logger

def create_argument_parser():
    parser = ArgumentParser(prog = APPLICATION_NAME, 
                            description = APPLICATION_DESCRIPTION)
    parser.add_argument("-v", "--version", action = "version", 
                        version = VERSION)
    parser.add_argument("-d", "--debug", action = "store_true", 
                        help = "Output more messages that can be used to "
                                "help debug the application")
    return parser

def create_application_controller():
    state = PaintState()
    controller = Controller(APPLICATION_NAME, state)
    return controller

def main():
    parser = create_argument_parser()
    args = parser.parse_args()

    logging_level = INFO
    if args.debug:
        logging_level = DEBUG
    logger = create_logger(logging_level)

    controller = create_application_controller()
    controller.start()

if __name__ == "__main__":
    main()
