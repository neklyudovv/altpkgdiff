import requests


def fetch(branch: str):
    url = f"https://rdb.altlinux.org/api/export/branch_binary_packages/{branch}"
    resp = requests.get(url)
    resp.raise_for_status()
    return resp.json()["packages"]


def main():
    sisyphus = fetch("sisyphus")
    p11 = fetch("p11")
    print("packages in sisyphus: " + str(len(sisyphus)))
    print("packages in p11: " + str(len(p11)))


if __name__ == "__main__":
    main()
