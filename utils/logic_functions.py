from backend.db_dictionaries import feature_units_dict

def contains_both_axis(cols):
    units = list(set([feature_units_dict[col] for col in cols]))
    return len(units) > 1, sorted(units)