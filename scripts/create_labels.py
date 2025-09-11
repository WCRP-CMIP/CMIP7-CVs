import json
import os
from pathlib import Path
import esgvoc.api as ev
from icecream import IceCreamDebugger
import devtools

ic = IceCreamDebugger(argToStringFunction=devtools.pformat)


def main():
    known_bv_in_universe = ev.get_all_terms_in_data_descriptor("known_branded_variable")
    i = 0
    for bv in known_bv_in_universe:
        i = i + 1
        ic(bv)
        temporal_label = bv.temporal_label
        vertical_label = bv.vertical_label
        horizontal_label = bv.horizontal_label
        area_label = bv.area_label
        ic([temporal_label, vertical_label, horizontal_label, area_label])

        temporal_label_data = {
            "@context": "000_context.jsonld",
            "id": temporal_label,
            "type": "temporal_label",
        }

        vertical_label_data = {
            "@context": "000_context.jsonld",
            "id": vertical_label,
            "type": "vertical_label",
        }

        horizontal_label_data = {
            "@context": "000_context.jsonld",
            "id": horizontal_label,
            "type": "horizontal_label",
        }

        area_label_data = {
            "@context": "000_context.jsonld",
            "id": area_label,
            "type": "area_label",
        }

        with open(Path("CMIP7_temporalLabel") / f"{temporal_label}.json", "w") as f:
            json.dump(temporal_label_data, f, indent=4, ensure_ascii=False)
        
        with open(Path("CMIP7_verticalLabel") / f"{vertical_label}.json", "w") as f:
            json.dump(vertical_label_data, f, indent=4, ensure_ascii=False)
        
        with open(Path("CMIP7_horizontalLabel") / f"{horizontal_label}.json", "w") as f:
            json.dump(horizontal_label_data, f, indent=4, ensure_ascii=False)
        
        with open(Path("CMIP7_areaLabel") / f"{area_label}.json", "w") as f:
            json.dump(area_label_data, f, indent=4, ensure_ascii=False)


if __name__ == "__main__":
    main()