import argparse
import re
from collections import Counter

LOG = re.compile(r"^([0-9-]+ [0-9:.]+)\s+(\d+)\s+(\d+)\s+([IDVEFAW])\s+(.+?):(?: (.*))?$")
JAVA = re.compile(r"\b([A-Za-z0-9_$]+\.java):\d+\b")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", required=True)
    parser.add_argument("--output", required=True)
    parser.add_argument("--rgx", type=int, choices=range(1, 6), required=True)
    args = parser.parse_args()

    with open(args.input, encoding="utf-8", errors="replace") as f:
        lines = f.readlines()

    data = []
    for line in lines:
        m = LOG.match(line)
        data.append((line, m.groups() if m else None))

    result = []

    if args.rgx == 1:
        counts = [0] * 10

        for _, e in data:
            if not e:
                continue

            time, pid, tid, level, tag, msg = e

            checks = (
                re.search(r"^10-15", time),
                re.search(r"^10-15 10:18:51", time),
                re.search(r"\d\d:\d\d:51", time),
                re.search(r"lowmemorykiller", tag, re.I),
                pid == "221" and re.search(r"10:18:51", time),
                level == "E",
                level == "W" and re.search(r"PackageManager", tag, re.I),
                level == "D" and re.search(r"ExoPlayer", tag, re.I),
                level in ("E", "W") and re.search(r"\.java:\d+", msg or ""),
                re.search(r"\bThread\b", msg or "")
            )

            counts = [n + bool(x) for n, x in zip(counts, checks)]

        result = [str(n) for n in counts]

    elif args.rgx == 2:
        in_error = False

        for line, e in data:
            if e:
                in_error = e[3] == "E"
                text = (e[5] or "") if in_error else ""
            else:
                text = line if in_error else ""

            result.extend(JAVA.findall(text))

    else:
        entries = [e for _, e in data if e]

        if args.rgx == 3:
            seen = set()
            for e in entries:
                if e[1] not in seen:
                    seen.add(e[1])
                    result.append(e[1])

        elif args.rgx == 4:
            errors = Counter(e[1] for e in entries if e[3] == "E")
            if errors:
                pid, count = errors.most_common(1)[0]
                result = [f"PID={pid} ({count} errors)"]

        else:
            result = [str(sum(
                e[3] == "E" and e[1] == e[2] for e in entries
            ))]

    with open(args.output, "w", encoding="utf-8") as f:
        f.write("\n".join(result) + ("\n" if result else ""))


if __name__ == "__main__":
    main()