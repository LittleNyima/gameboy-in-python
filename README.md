# Game Boy in Python

A Game Boy emulator implemented with pure Python (abbr. **GBP**). GBP is a very simple implement and is able to run some of the GameBoy games (e.g., Dr. Mario). GBP has also passed the blargg's CPU instruction tests.

However, due to its simplicity and Python'ss performance bottleneck, the frame rate is usually only 3 or 4 (tested on the Apple M1 pro silicon).

Feature not implemented:

- Cartridge MBCs.
- Audio.
- Game Boy Color / Super Game Boy functionalities.
- Bootstrap and so on.

# Usage

```shell
gameboy [-h] [--debug] gamerom
```

- `gamerom`: Path to the game ROM file.
- `-h` `--help`: Show the help message and exit.
- `--debug`: Enable debugging mode.

# Installation

- From source: Clone this repository and run `pip install .`
- From pypi: Run `pip install gameboy-python`

Requirements: pysdl2, pysdl2-dll

# Screenshot

![GameBoy](https://i.miji.bid/2024/03/01/8404fe7ed6d20539c76df21bb93d795a.png)

# References

- **[gbdev/pandocs](https://github.com/gbdev/pandocs)**
- **[gbdev/rgbds](https://github.com/gbdev/rgbds)**
- **[Baekalfen/PyBoy](https://github.com/Baekalfen/PyBoy)**
- **[rockytriton/LLD_gbemu](https://github.com/rockytriton/LLD_gbemu)**
