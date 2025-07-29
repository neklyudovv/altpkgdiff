import argparse
from altpkgdiff import fetch, diff_branches_json


def main():
    parser = argparse.ArgumentParser(description="compare binary packages between ALT branches.")
    parser.add_argument("--branch1", default="sisyphus", help="first branch to compare")
    parser.add_argument("--branch2", default="p11", help="second branch to compare")
    parser.add_argument("--output", help="output file path (if not specified print to stdout)")

    args = parser.parse_args()

    first_branch = fetch(args.branch1)
    second_branch = fetch(args.branch2)
    diff = diff_branches_json(first_branch, second_branch)

    if args.output:
        with open(args.output, "w") as f:
            f.write(diff)
            print(f"output written to {args.output}")
    else:
        print(diff)


if __name__ == "__main__":
    main()
