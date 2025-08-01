import argparse
import json
from altpkgdiff import fetch, compare_branches, FetchError


def main():
    parser = argparse.ArgumentParser(description="compare binary packages between ALT branches.")
    parser.add_argument("--branch1", default="sisyphus", help="first branch to compare")
    parser.add_argument("--branch2", default="p11", help="second branch to compare")
    parser.add_argument("--output", help="output file path (if not specified print to stdout)")

    args = parser.parse_args()

    try:
        first_branch_pkgs = fetch(args.branch1)
        second_branch_pkgs = fetch(args.branch2)
    except FetchError as e:
        print(e)
        exit(1)

    diff = json.dumps({
        "branch1": args.branch1,
        "branch2": args.branch2,
        "results": compare_branches(first_branch_pkgs, second_branch_pkgs)}, indent=2)

    if args.output:
        with open(args.output, "w") as f:
            f.write(diff)
            print(f"output written in {args.output}")
    else:
        print(diff)


if __name__ == "__main__":
    main()
