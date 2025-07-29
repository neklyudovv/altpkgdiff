import requests
from rpm_vercmp import vercmp


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


def beautify_package(package):
    return {
        "name": package["name"],
        "version": package["version"],
        "release": package["release"]
    }


def compare_branches(first_branch_pkgs, second_branch_pkgs):
    arch_set = set(pkg["arch"] for pkg in first_branch_pkgs + second_branch_pkgs)
    result = {}

    for arch in arch_set:
        # "pkg name": {pkg attr}
        first_map = {p["name"]: beautify_package(p) for p in first_branch_pkgs if p["arch"] == arch}
        second_map = {p["name"]: beautify_package(p) for p in second_branch_pkgs if p["arch"] == arch}

        only_in_first_branch = [first_map[name] for name in sorted(set(first_map) - set(second_map))]
        only_in_second_branch = [second_map[name] for name in sorted(set(second_map) - set(first_map))]

        newer = []
        for name in set(first_map) & set(second_map):  # both contains same pkg
            if compare_versions(first_map[name]["version"], first_map[name]["release"],
                                second_map[name]["version"], second_map[name]["release"]) > 0:
                newer.append(first_map[name])  # but if first_branch ver is newer - append

        result[arch] = {  # arch name: {br1: [pkgs], br2: [pkgs], newer_in_b1: [pkgs]}
            "only_in_branch1": only_in_first_branch,
            "only_in_branch2": only_in_second_branch,
            "newer_in_branch1": newer
        }
    return result
