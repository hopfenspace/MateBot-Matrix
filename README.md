# MateBot

Matrix Bot as frontend to the [MateBot API](https://github.com/hopfenspace/MateBot)
that allows users to buy Mate, ice cream and pizza or more, easily share bills
or get refunds from the community when they paid for something used by everyone.

## Setup

### Installation

1. Make sure you have Python (>= 3.7), pip (>= 19) and `libolm` installed.
   See [hopfenmatrix](https://github.com/hopfenspace/hopfenmatrix) for
   installation instructions and further details.
2. Clone this repository.
3. `python3 -m venv venv`
4. `venv/bin/pip3 install -r requirements.txt`
5. `venv/bin/python3 -m matebot_matrix`
6. Adapt the newly generated `config.json` file according to your needs.
   Especially the `matrix` section is most important.
7. Start the bot using `venv/bin/python3 -m matebot_matrix` again.

### Requirements

- Python 3.7 or above
- [libolm](https://gitlab.matrix.org/matrix-org/olm)
- [hopfenmatrix](https://github.com/hopfenspace/hopfenmatrix)

## Documentation

See docs folder or [our deployed documentation](https://docs.hopfenspace.org/matebot).

## License

See [license](LICENSE).
