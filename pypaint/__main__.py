from logging        import Formatter, StreamHandler, DEBUG, INFO, getLogger

from .controller    import Controller
from .paint_state   import PaintState


__version__ = "2.0.5"

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

def main(debug_level):
    logger = create_logger(debug_level)
    state = PaintState()
    controller = Controller(state)
    controller.start()

if __name__ == "__main__":
    main(DEBUG)
