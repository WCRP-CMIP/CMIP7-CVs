import os
import json

def extract_json(data_descriptor_dir, cv_dir):
    os.makedirs(cv_dir, exist_ok=True)

    success = 0
    for i, filename in enumerate(os.listdir(data_descriptor_dir), start=1):
        if filename.endswith(".json"):
            data_descriptor_path = os.path.join(data_descriptor_dir, filename)
            cv_path = os.path.join(cv_dir, filename)

            try:
                with open(data_descriptor_path, "r", encoding="utf-8") as f:
                    data = json.load(f)

                data = {
                    "@context": data.get("@context", ""),
                    "id": data.get("id", ""),
                    "type": data.get("type", "")
                }

                with open(cv_path, "w", encoding="utf-8") as f:
                    json.dump(data, f, indent=4, ensure_ascii=False)
                
                success += 1
            except Exception as e:
                print(f"❌ Error with {filename}: {e}")

    print(f"✅ {success}/{i} DD files converted to CV files in : {cv_dir}")
    if success != i:
        print(f"❌ {i - success} files failed to convert.")


# Exemple d'utilisation
if __name__ == "__main__":
    dossier_source = "scripts/WCRP-universe_known_branded_variable"
    dossier_cible = "CMIP7_known_branded_variable"
    extract_json(dossier_source, dossier_cible)
