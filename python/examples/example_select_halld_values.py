import rcdb.provider
t = rcdb.provider.RCDBProvider('mysql://rcdb@hallddb.jlab.org/rcdb')\
    .select_values(['polarization_angle', 'polarization_direction'],
                   search_str="@is_production and event_count>100000", run_min=30000, run_max=32000)
print('\n'.join([' '.join(map(str, r)) for r in t]))
