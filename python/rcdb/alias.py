class ConditionSearchAlias(object):
    def __init__(self, name, expression, comment):
        self.name = name
        self.expression = expression
        self.comment = comment


default_aliases = [
    ConditionSearchAlias('is_production', """run_type in ['hd_all.tsg', 'hd_all.tsg_ps', 'hd_all.bcal_fcal_st.tsg'] and
                                             beam_current > 2 and
                                             event_count > 500000 and
                                             solenoid_current > 100 and
                                             collimator_diameter != 'Blocking'""",
                         "Is production run"),

    ConditionSearchAlias('is_cosmic', "(run_type == 'hd_all.tsg_cosmic' and 'COSMIC' in daq_run and beam_current < 1) or (radiator_type == 'RETRACTED' and collimator_diameter == 'Blocking')",
                         "Is cosmic run"),

    ConditionSearchAlias('is_empty_target', "target_type == 'EMPTY & Ready'", "Target is empty"),

    # These should be true starting in 2017.  Need to check to make sure that 2016 data is accurate...
    ConditionSearchAlias('is_amorph_radiator', "polarization_angle < 0.",  "Amorphous Radiator"),                         
    ConditionSearchAlias('is_coherent_beam', "polarization_angle >= 0.", "Coherent Beam"),
    #ConditionSearchAlias('is_amorph_radiator', "radiator_index == -1 and radiator_type != 'None' and target_type == 'FULL & Ready'",
    #                     "Amorphous Radiator"),
    #ConditionSearchAlias('is_coherent_beam', "(radiator_id != 5  and radiator_id > 0) and target_type == 'FULL & Ready'", "Coherent Beam"),

    ConditionSearchAlias('is_field_off', "solenoid_current < 100", " Field Off"),

    ConditionSearchAlias('is_field_on', "solenoid_current >= 100", " Field On"),

    ConditionSearchAlias('status_approved_long', "status == 2", "Run status = approved (long)"),

    ConditionSearchAlias('status_approved', "status == 1", "Run status = approved"),

    ConditionSearchAlias('status_unchecked', "status == -1", "Run status = unchecked"),

    ConditionSearchAlias('status_reject', " status == 0", "Run status = reject"),
]

_def_al_by_name = None


def get_default_aliases_by_name():
    global _def_al_by_name
    if _def_al_by_name is None:
        _def_al_by_name = {al.name:al for al in default_aliases }
    return _def_al_by_name
