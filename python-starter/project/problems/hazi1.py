from project.problem import Problem
import argparse
import os

class Hazi1(Problem):

    def initialize_parser(self, parser: argparse.ArgumentParser):
        parser.add_argument('--check', help='Ellenőrizendő szavak vesszővel elválasztva', type=str)

    def is_chosen_problem(self, args):
        return args.check is not None

    def run(self, args):
        input_file = args.input
        output_file = args.output

        if not os.path.exists(input_file):
            print(f"A bemeneti fájl nem található.")
            return

        with open(input_file, 'r', encoding='utf-8') as f:
            lines = [line.strip() for line in f if line.strip()]

        if len(lines) < 4:
            print("A bemeneti fájl formátuma érvénytelen.")
            return

        states = lines[0].split()
        alphabet = lines[1].split()
        start_state = lines[2]
        accept_states = set(lines[3].split())

        transitions = {}
        for line in lines[4:]:
            parts = line.split()
            if len(parts) == 3:
                src, sym, dst = parts
                transitions[(src, sym)] = dst

        words_to_check = args.check.split(',')
        results = []

        for word in words_to_check:
            current_state = start_state
            is_accepted = True

            for char in word:
                if char not in alphabet or (current_state, char) not in transitions:
                    is_accepted = False
                    break

                current_state = transitions[(current_state, char)]

            if is_accepted and current_state in accept_states:
                results.append((word, "IGEN"))
            else:
                results.append((word, "NEM"))

        with open(output_file, 'w', encoding='utf-8') as f:
            for word, res in results:
                f.write(f"{word:<20}{res}\n")