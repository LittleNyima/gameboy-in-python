import argparse

from gameboy import GameBoy


def parse_args():
    parser = argparse.ArgumentParser(
        prog='gameboy',
        description='GameBoy Emulator in Python.',
    )
    parser.add_argument(
        'gamerom',
        type=str,
        help='Path to the game rom file.',
    )

    return parser.parse_args()


def main():
    args = parse_args()
    with GameBoy(
        gamerom=args.gamerom,
    ) as gameboy:
        while gameboy.tick():
            pass


main()
