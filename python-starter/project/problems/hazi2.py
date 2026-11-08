from project.problem import Problem
import argparse
import os
from collections import deque


class Hazi2(Problem):

    def initialize_parser(self, parser: argparse.ArgumentParser):
        parser.add_argument('--det', help='Automata determinizálása', action='store_true')

    def is_chosen_problem(self, args):
        return bool(args.det)

    def run(self, args):
        input_file = args.input
        output_file = args.output

        if not os.path.exists(input_file):
            print(f"A bemeneti fájl ('{input_file}') nem található.")
            return

        with open(input_file, 'r', encoding='utf-8') as f:
            lines = [line.strip() for line in f if line.strip()]

        if len(lines) < 4:
            print("A bemeneti fájl formátuma érvénytelen (kevesebb mint 4 sor).")
            return

        states = lines[0].split()
        alphabet = lines[1].split()
        start_state = lines[2].strip()
        accept_states = lines[3].split()

        valid_states = set(states)
        valid_alphabet = set(alphabet)

        if start_state not in valid_states:
            print(f"A kezdőállapot ('{start_state}') nem szerepel az állapotok között.")
            return

        for acc in accept_states:
            if acc not in valid_states:
                print(f"A '{acc}' végállapot nem szerepel az állapotok között.")
                return

        nfa_transitions = {}
        for line in lines[4:]:
            parts = line.split()
            if len(parts) != 3:
                print(f"Érvénytelen átmenet formátum: '{line}'")
                return

            src, sym, dst = parts

            if src not in valid_states:
                print(f"Ismeretlen kiinduló állapot az átmenetben: '{src}'")
                return
            if dst not in valid_states:
                print(f"Ismeretlen célállapot az átmenetben: '{dst}'")
                return
            if sym not in valid_alphabet:
                print(f"Ismeretlen szimbólum az átmenetben: '{sym}'")
                return

            nfa_transitions.setdefault((src, sym), set()).add(dst)

        sorted_alphabet = sorted(alphabet)
        valid_accept_set = set(accept_states)

        start_subset = frozenset([start_state])
        subset_to_name = {start_subset: 's0'}
        name_to_subset = {'s0': start_subset}

        queue = deque([start_subset])
        dfa_transitions = []

        while queue:
            current_subset = queue.popleft()
            current_name = subset_to_name[current_subset]
            for sym in sorted_alphabet:
                next_subset = set()
                for state in current_subset:
                    if (state, sym) in nfa_transitions:
                        next_subset.update(nfa_transitions[(state, sym)])

                if not next_subset:
                    continue

                next_frozen = frozenset(next_subset)

                if next_frozen not in subset_to_name:
                    new_name = f"s{len(subset_to_name)}"
                    subset_to_name[next_frozen] = new_name
                    name_to_subset[new_name] = next_frozen
                    queue.append(next_frozen)

                target_name = subset_to_name[next_frozen]
                dfa_transitions.append((current_name, sym, target_name))

        dfa_states = list(name_to_subset.keys())

        dfa_accept_states = [
            name for name, subset in name_to_subset.items()
            if subset & valid_accept_set
        ]

        dfa_transitions.sort(key=lambda x: (x[0], x[1], x[2]))

        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(" ".join(dfa_states) + "\n")
            f.write(" ".join(alphabet) + "\n")
            f.write("s0\n")
            f.write(" ".join(dfa_accept_states) + "\n")
            for src, sym, dst in dfa_transitions:
                f.write(f"{src} {sym} {dst}\n")