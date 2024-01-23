import argparse
import json
import os
import re
from dataclasses import dataclass
from typing import Any, Dict, List, cast

import requests

'''
Part 1 - Code Generation
------------------------
'''


@dataclass(frozen=True)
class Operand:
    name: str
    bytes: int = 1
    immediate: bool = True
    decrement: bool = False
    increment: bool = False


@dataclass
class GenerationResults:
    instr_types: List[str]
    operand_types: List[str]


def generate_indent_codes(attrs: List[str], indent: int = 4):
    conj = '\n' + ' ' * indent
    sorted_attrs = sorted(set(attrs))
    return conj.join([attr.replace('\n', conj) for attr in sorted_attrs])


def generate_instr_type_str(instr_type: str):
    return f"{instr_type} = '{instr_type}'"


def generate_operand_name(operand: Operand):
    name = operand.name
    if name.startswith('$'):
        name = name.replace('$', 'hex')
    if name.isdigit():
        name = 'bit' + name
    if not operand.immediate:
        name += '_mem'
    if operand.decrement:
        name += '_dec'
    if operand.increment:
        name += '_inc'
    return name.upper()


def generate_operand_str(operand: Operand):
    name = generate_operand_name(operand)
    reprstr = f"Operand(name='{operand.name}'"
    if not operand.immediate:
        reprstr += ', immediate=False'
    if operand.decrement:
        reprstr += ', decrement=True'
    if operand.increment:
        reprstr += ', increment=True'
    reprstr += ')'
    return f'{name} = {reprstr}'


def generate_subset(subset: Dict[str, Dict[str, Any]]) -> GenerationResults:
    instr_types: List[str] = []
    operand_types: List[str] = []

    for _, instr in subset.items():
        mnemonic = cast(str, instr.get('mnemonic'))
        operands = cast(List[Dict[str, Any]], instr.get('operands'))
        instr_types.append(generate_instr_type_str(mnemonic))
        if len(operands) > 0:
            operand_types.append(generate_operand_str(Operand(**operands[0])))
        if len(operands) > 1:
            operand_types.append(generate_operand_str(Operand(**operands[1])))

    return GenerationResults(
        instr_types=instr_types,
        operand_types=operand_types,
    )


def generate(instr: Dict[str, Dict]) -> str:
    unprefixed_results = generate_subset(instr.get('unprefixed', {}))
    cbprefixed_results = generate_subset(instr.get('cbprefixed', {}))

    instr_types = generate_indent_codes(
        unprefixed_results.instr_types + cbprefixed_results.instr_types,
    )
    operand_types = generate_indent_codes(
        unprefixed_results.operand_types + cbprefixed_results.operand_types,
    )

    with open('tools/codegen/templates/instructions.tmpl.py') as f:
        tmpl = f.read()

    tmpl = re.sub(r'(?<!# FMT_PREFIX)({.*?})', r'{\1}', tmpl)
    return tmpl.replace('# FMT_PREFIX', '').format(
        instr_types=instr_types,
        operand_types=operand_types,
    )


'''
Part 2 - Utensil Functions
--------------------------
'''


def get_args():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        '--print', action='store_true',
        help='Print generated codes to console.',
    )
    parser.add_argument(
        '--target', type=str,
        help='Target file to write the generated codes.',
    )
    return parser.parse_args()


def fetch_instr_set():
    cache_path = 'gameboy/core/opcodes.json'
    if not os.path.isfile(cache_path):
        r = requests.get(r'https://gbdev.io/gb-opcodes/Opcodes.json')
        if r.status_code == requests.codes.ok:
            data = r.json()
        with open(cache_path, 'w') as f:
            json.dump(data, f, indent=2)
    else:
        with open(cache_path) as f:
            data = json.load(f)
    return data


def dump(contents: str, args: argparse.Namespace):
    if args.print:
        print(contents)
    if args.target:
        os.makedirs(os.path.dirname(args.target), exist_ok=True)
        with open(args.target, 'w') as f:
            f.write(contents)


def main():
    args = get_args()
    instr = fetch_instr_set()
    contents = generate(instr=instr)
    dump(contents=contents, args=args)


if __name__ == '__main__':
    main()
