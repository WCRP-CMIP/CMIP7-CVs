import esgvoc.api as ev
from icecream import IceCreamDebugger
import devtools

ic = IceCreamDebugger(argToStringFunction=devtools.pformat)


def main():
    known_bv_in_universe = ev.get_all_terms_in_data_descriptor("known_branded_variable")
    i = 0
    for bv in known_bv_in_universe:
        i = i + 1
        if i == 5:
            break
        ic(bv)
        temporal_label = bv.temporal_label
        vertical_label = bv.vertical_label
        horizontal_label = bv.horizontal_label
        area_label = bv.area_label
        ic([temporal_label, vertical_label, horizontal_label, area_label])


if __name__ == "__main__":
    main()
