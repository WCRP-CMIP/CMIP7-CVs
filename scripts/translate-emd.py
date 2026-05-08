import json


def slugify(s):
    # Replace hyphens with underscores and lowercase
    return s.replace("-", "_").lower()


def transform_model_component(comp_config):
    # e.g., "atmosphere_arpege-climat-version-6-3_h100_v100" -> "arpege_climat_version_6_3"
    # TODO: check this.
    # I assume there's more to it than this,
    # the model component tells us the component,
    # model name, horizontal grid and vertical grid?
    parts = comp_config.split("_")
    if len(parts) >= 3:
        # Assume middle part(s) is the component name
        comp_name = "_".join(parts[1:-2])
        return slugify(comp_name)
    return slugify(comp_config)


def translate_model(source):
    target = {
        "@context": "000_context.jsonld",
        # TODO: check whether a simple slugify is going to work in all cases
        "id": slugify(source.get("@id", "")),
        "type": "model",
    }

    # Map simple fields
    target["name"] = source.get("name", "")
    target["drs_name"] = source.get("name", "")

    # Family - target has uppercase and multiple families, source has lowercase single.
    # TODO: check whether simple logic here is going to work in all cases
    # or we need something more complex.
    target["family"] = (
        source.get("family", "").upper().replace("-", "-")
    )  # Minimal change

    # TODO: check whether slugify is enough.
    # TODO: add generation of dynamic components to ensure internal esgvoc links.
    target["dynamic_components"] = [
        slugify(c) for c in source.get("dynamic_components", [])
    ]
    # TODO: check whether slugify is enough.
    # TODO: add generation of prescribed components to ensure internal esgvoc links.
    target["prescribed_components"] = [
        slugify(c) for c in source.get("prescribed_components", [])
    ]
    # TODO: check whether slugify is enough.
    # TODO: add generation of omitted components to ensure internal esgvoc links.
    target["omitted_components"] = [
        slugify(c) for c in source.get("omitted_components", [])
    ]

    # TODO: figure out what to do if description or calendar is missing,
    # raise error then follow up in issue in EMD?
    # Note: Target files in WCRP-universe sometimes contain enriched data
    # (e.g., expanded descriptions, corrected grid resolutions) that are not
    # present in the EMD source. These must be handled manually or via lookups.
    target["description"] = source.get("description", "")
    target["calendar"] = source.get("calendar", [])
    target["release_year"] = source.get("release_year")

    # References - convert DOIs to internal IDs
    # TODO: harden this logic
    # (current implementation definitely wrong,
    # need to instead write the reference file, then use the relevant ID here)
    target["references"] = []
    for i, ref in enumerate(source.get("references", []), 1):
        target["references"].append(f"{target['id']}_ref_{i:03d}")

    # Component Configs -> Model Components
    # TODO: double check this mapping and add writing of component config files
    target["model_components"] = [
        transform_model_component(c) for c in source.get("component_configs", [])
    ]

    # Embedded Components - swap order [parent, child] -> [child, parent]
    # TODO: check why order is swapped (and ideally remove need for swapping)
    # TODO: check if slugify is ok
    # TODO: write embedded components too
    target["embedded_components"] = [
        [slugify(pair[1]), slugify(pair[0])]
        for pair in source.get("embedded_components", [])
    ]

    # Coupling Groups -> Coupled Components (binary pairs)
    # TODO: double check this logic
    coupled = []
    for group in source.get("coupling_groups", []):
        # Generate all unique pairs
        for i in range(len(group)):
            for j in range(i + 1, len(group)):
                pair = sorted([slugify(group[i]), slugify(group[j])])
                if pair not in coupled:
                    coupled.append(pair)
    target["coupled_components"] = coupled

    return target


def translate_grid(source):
    target = {
        "@context": "000_context.jsonld",
        # TODO: double check this mapping
        "id": source.get("@id", ""),
        "type": "horizontal_grid_cell",
    }

    # TODO: double check this mapping
    target["name"] = source.get("@id", "")

    # Region array -> string
    # TODO: add error raising if more than one region ?
    region = source.get("region", [])
    if isinstance(region, list) and len(region) > 0:
        target["region"] = region[0]
    else:
        target["region"] = region

    # TODO: check slugify
    # TODO: write these components into esgvoc branches too
    target["grid_type"] = slugify(source.get("grid_type", ""))
    target["grid_mapping"] = slugify(source.get("grid_mapping", ""))
    target["temporal_refinement"] = source.get("temporal_refinement", "")
    target["drs_name"] = source.get("@id", "")

    # Numeric fields
    # TODO: raise error if empty? (Need to check EMD spec)
    target["x_resolution"] = source.get("x_resolution")
    target["y_resolution"] = source.get("y_resolution")

    # Rename units -> horizontal_units
    # TODO: raise error if empty? (Need to check EMD spec)
    target["horizontal_units"] = source.get("units", "")

    # TODO: raise error if empty? (Need to check EMD spec)
    target["southernmost_latitude"] = source.get("southernmost_latitude")
    target["westernmost_longitude"] = source.get("westernmost_longitude")
    target["n_cells"] = source.get("n_cells")

    return target


def translate_file(input_path, output_path):
    with open(input_path, "r") as f:
        source = json.load(f)

    type_info = source.get("@type", [])
    if "wcrp:model" in type_info:
        target = translate_model(source)
    elif "wcrp:horizontal_grid_cell" in type_info:
        target = translate_grid(source)
    else:
        print(f"Unknown type for {input_path}")
        return

    with open(output_path, "w") as f:
        json.dump(target, f, indent=2)


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(
        description="Translate EMD JSON to WCRP-universe JSON."
    )
    parser.add_argument("input", help="Path to source EMD JSON file")
    parser.add_argument("output", help="Path to target WCRP-universe JSON file")

    args = parser.parse_args()
    translate_file(args.input, args.output)
