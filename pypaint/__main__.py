from chadlib.utility.main_script    import (create_argument_parser, 
                                            create_logger)

from .controller                    import Controller
from .paint_state                   import PaintState


VERSION = "2.0.11"
APPLICATION_NAME = "PyPaint"
APPLICATION_DESCRIPTION = "Simple, networked paint application"


def create_application_controller():
    state = PaintState()
    controller = Controller(APPLICATION_NAME, state)
    return controller

def main():
    """
    Create the parser, logger, and application controller, then start up the 
    application.
    """
    parser = create_argument_parser(APPLICATION_NAME, VERSION, 
                                    APPLICATION_DESCRIPTION)
    args = parser.parse_args()

    logger = create_logger(args.debug, args.logfile)

    controller = create_application_controller()
    controller.start()

if __name__ == "__main__":
    main()
