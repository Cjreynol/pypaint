from sys import argv

from pypaint.paint_controller import PaintController


def main(*args):
    c = PaintController(*args)
    c.start()

if __name__ == "__main__":
    is_host = bool(argv[1])
    port = int(argv[2])
    peer_ip = None
    if not is_host:
        peer_ip = argv[3]
    main(is_host, port, peer_ip)
