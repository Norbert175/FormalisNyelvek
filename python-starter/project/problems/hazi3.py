from project.problem import Problem
import argparse
import os


class Hazi3(Problem):

    def initialize_parser(self, parser: argparse.ArgumentParser):
        parser.add_argument('--mini', help='Automata minimalizálása', action='store_true')

    def is_chosen_problem(self, args):
        return bool(args.mini)

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
                print(f"A(z) '{acc}' végállapot nem szerepel az állapotok között.")
                return

        transitions = {}
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

            transitions[(src, sym)] = dst

        accept_set = set(accept_states)
        partitions = []
        acc_group = {s for s in states if s in accept_set}
        non_acc_group = {s for s in states if s not in accept_set}
        if acc_group:
            partitions.append(acc_group)
        if non_acc_group:
            partitions.append(non_acc_group)

        sorted_alphabet = sorted(alphabet)

        while True:
            new_partitions = []
            for group in partitions:
                subgroups = {}
                for state in group:
                    signature = []
                    for sym in sorted_alphabet:
                        dst = transitions.get((state, sym), None)
                        dst_group_idx = None
                        if dst is not None:
                            for idx, g in enumerate(partitions):
                                if dst in g:
                                    dst_group_idx = idx
                                    break
                        signature.append(dst_group_idx)

                    sig_tuple = tuple(signature)
                    subgroups.setdefault(sig_tuple, set()).add(state)

                new_partitions.extend(subgroups.values())

            if len(new_partitions) == len(partitions):
                break
            partitions = new_partitions

        def to_s_name(q_name):
            return 's' + q_name[1:] if q_name.startswith('q') else 's' + q_name

        state_to_new = {}
        for group in partitions:
            smallest_state = min(group)
            new_name = to_s_name(smallest_state)
            for state in group:
                state_to_new[state] = new_name

        new_states = sorted(set(state_to_new.values()))
        new_start = state_to_new[start_state]
        new_accept = sorted({state_to_new[s] for s in accept_states})

        new_transitions_set = set()
        for (src, sym), dst in transitions.items():
            new_transitions_set.add((state_to_new[src], sym, state_to_new[dst]))

        new_transitions = sorted(new_transitions_set, key=lambda x: (x[0], x[1], x[2]))

        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(" ".join(new_states) + "\n")
            f.write(" ".join(alphabet) + "\n")
            f.write(f"{new_start}\n")
            f.write(" ".join(new_accept) + "\n")
            for src, sym, dst in new_transitions:
                f.write(f"{src} {sym} {dst}\n")