import json
import os
import requests

owner = "WCRP-CMIP"
repo = "WCRP-universe"
branch = "esgvoc_dev"
folder = "known_branded_variable"
out_root = "CMIP7_brandedVariable"

# Optionnel : token GitHub pour éviter les limites d'API anonymes
headers = {}
token = os.getenv("GITHUB_TOKEN")
if token:
    headers["Authorization"] = f"token {token}"


def list_files_in_folder(owner, repo, branch, folder):
    """
    Retourne la liste des chemins (remote) des fichiers .json sous `folder`.
    """
    branch_url = f"https://api.github.com/repos/{owner}/{repo}/branches/{branch}"
    r = requests.get(branch_url, headers=headers)
    r.raise_for_status()
    commit_sha = r.json()["commit"]["sha"]

    tree_url = f"https://api.github.com/repos/{owner}/{repo}/git/trees/{commit_sha}?recursive=1"
    r = requests.get(tree_url, headers=headers)
    r.raise_for_status()
    tree = r.json()["tree"]

    folder = folder.rstrip("/") + "/"
    files = [
        item["path"]
        for item in tree
        if item["type"] == "blob"
        and item["path"].startswith(folder)
        and item["path"].lower().endswith(".json")  # garder uniquement les .json
    ]
    return files


if __name__ == "__main__":
    os.makedirs(out_root, exist_ok=True)

    remote_files = list_files_in_folder(owner, repo, branch, folder)

    # détection des basenames dupliqués
    seen = {}
    for remote_path in remote_files:
        basename = os.path.basename(remote_path)
        if basename in seen:
            seen[basename].append(remote_path)
        else:
            seen[basename] = [remote_path]

    # Avertir s'il y a des duplicates
    duplicates = {k: v for k, v in seen.items() if len(v) > 1}
    if duplicates:
        print(
            "Attention : plusieurs fichiers distants partagent le même nom (basename). "
            "Ils écraseront potentiellement l'un l'autre si on écrit seulement le basename."
        )
        for name, paths in duplicates.items():
            print(f"  {name}:")
            for p in paths:
                print(f"    - {p}")
        print(
            "Si tu veux conserver la structure en sous-dossiers, dis-le et j'ajoute ça.\n"
        )

    for remote_path in remote_files:
        basename = os.path.basename(remote_path)
        cv_path = os.path.join(out_root, basename)

        data = {
            "@context": "000_context.jsonld",
            "id": os.path.basename(remote_path).split(".")[0],
            "type": "known_branded_variable",
        }

        with open(cv_path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=4, ensure_ascii=False)
