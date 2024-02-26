import argparse

from gameboy import GameBoy


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        prog='gameboy',
        description='GameBoy Emulator in Python.',
    )
    parser.add_argument(
        'gamerom',
        type=str,
        help='Path to the game rom file.',
    )
    parser.add_argument(
        '--debug',
        action='store_true',
        help='Enable debugging mode.',
    )

    return parser.parse_args()


def setup_debugging(enabled: bool, gameboy: GameBoy):
    if enabled:
        import logging

        from gameboy.common import set_level
        set_level(logging.DEBUG)
        gameboy.plugins.debugging_serial.enable()
        gameboy.plugins.debugging_tile_view.enable()
        gameboy.plugins.debugging_memory_view.enable()


def main():
    args = parse_args()
    with GameBoy(
        gamerom=args.gamerom,
    ) as gameboy:
        setup_debugging(enabled=args.debug, gameboy=gameboy)
        while gameboy.tick():
            pass


main()
