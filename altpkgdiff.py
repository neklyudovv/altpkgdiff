import requests
from rpm_vercmp import vercmp
import json


class FetchError(Exception):
    pass


def fetch(branch: str):
    url = f"https://rdb.altlinux.org/api/export/branch_binary_packages/{branch}"
    try:
        resp = requests.get(url)
        resp.raise_for_status()
        data = resp.json()
        if "packages" not in data:
            raise FetchError(f"No packages found in branch {branch}")
        return data["packages"]
    except requests.exceptions.HTTPError as e:
        raise FetchError(f"HTTP error for branch {branch}: {e}")
    except requests.exceptions.RequestException as e:
        raise FetchError(f"Request error for branch {branch}: {e}")
    except ValueError:
        raise FetchError(f"Invalid JSON response for branch {branch}")


def compare_versions(v1, r1, v2, r2):
    cmp_ver = vercmp(v1, v2)
    if cmp_ver != 0:
        return cmp_ver
    return vercmp(r1, r2)


def diff_branches_json(first_branch, second_branch):
    arch_set = set(pkg["arch"] for pkg in first_branch + second_branch)
    result = {}

    for arch in arch_set:
        # "pkg name": {pkg attr}
        s_map = {p["name"]: p for p in first_branch if p["arch"] == arch}
        p_map = {p["name"]: p for p in second_branch if p["arch"] == arch}

        only_in_first_branch = sorted(set(s_map) - set(p_map))
        only_in_second_branch = sorted(set(p_map) - set(s_map))

        newer = []
        for name in set(s_map) & set(p_map):  # both contains same pkg
            if compare_versions(s_map[name]["version"], s_map[name]["release"],
                                p_map[name]["version"], p_map[name]["release"]) > 0:
                newer.append(name)  # but if first_branch ver is newer - append

        result[arch] = {  # generating json -> arch name: {b1: [pkgs], b2: [pkgs], newer_in_b1: [pkgs]}
            "only_in_branch1": only_in_first_branch,
            "only_in_branch2": only_in_second_branch,
            "newer_in_branch1": sorted(newer)
        }
    return json.dumps(result, indent=2)
