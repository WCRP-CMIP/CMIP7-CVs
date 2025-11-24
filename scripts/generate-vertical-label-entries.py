"""
Generate vertical label entries
"""

import json


def main():
    to_write = [
        "sl",
        "al",
        "alh",
        "ol",
        "olh",
        "rho",
        "h2m",
        "h10m",
        "h100m",
        "d10cm",
        "d100cm",
        "d0m",
        "d100m",
        "d300m",
        "d700m",
        "d2000m",
        "20bar",
        "10hPa",
        "100hPa",
        "200hPa",
        "220hPa",
        "500hPa",
        "560hPa",
        "700hPa",
        "840hPa",
        "850hPa",
        "925hPa",
        "1000hPa",
        "h16",
        "h40",
        "p3",
        "p4",
        "p5u",
        "p6",
        "p8",
        "p7c",
        "p7h",
        "p19",
        "p27",
        "p39",
        "op4",
        "u",
    ]

    for drs_name in to_write:
        id = drs_name.lower()
        content = {
            "@context": "000_context.jsonld",
            "id": id,
            "type": "vertical_label",
        }

        out_file = f"vertical_label/{id}.json"
        with open(out_file, "w") as fh:
            json.dump(content, fh, indent=4)
            fh.write("\n")

        print(f"Wrote {out_file}")


if __name__ == "__main__":
    main()
