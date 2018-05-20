from sys import argv

from pypaint.connection import Connection
from pypaint.paint_controller import PaintController


def main(args):
    connection = None
    if len(argv) > 1:
        is_host = bool(argv[1])
        port = int(argv[2])
        peer_ip = None

        if not is_host:
            peer_ip = argv[3]

        connection = Connection(is_host, port, peer_ip)

    paint = PaintController(connection)
    paint.start()

if __name__ == "__main__":
    main(argv)
