class ConditionSearchAlias(object):
    def __init__(self, name, expression, comment):
        self.name = name
        self.expression = expression
        self.comment = comment


default_aliases = [
    ConditionSearchAlias('is_production', """run_type in ['hd_all.tsg', 'hd_all.tsg_ps', 'hd_all.bcal_fcal_st.tsg'] and
                                             beam_current and beam_current > 2 and
                                             event_count > 500000 and
                                             solenoid_current and solenoid_current > 100 and
                                             collimator_diameter != 'Blocking'""",
                         "Is production run"),

    ConditionSearchAlias('is_2018production', """daq_run == 'PHYSICS' and
                                             beam_current > 2 and
                                             event_count > 10000000 and
                                             solenoid_current > 100 and
                                             collimator_diameter != 'Blocking'""",
                         "Is production run"),

    ConditionSearchAlias('is_primex_production', """daq_run == 'PHYSICS_PRIMEX' and
                                             event_count > 1000000 and
                                             collimator_diameter != 'Blocking'""",
                         "Is PrimEx production run"),

    ConditionSearchAlias('is_dirc_production', """daq_run == 'PHYSICS_DIRC' and 
                                                  beam_current > 2 and 
                                                  event_count > 5000000 and 
                                                  solenoid_current > 100 and 
                                                  collimator_diameter != 'Blocking'""",
                         "Is DIRC production run"),

    ConditionSearchAlias('is_src_production', """daq_run == 'PHYSICS_SRC' and 
                                                  beam_current > 2 and 
                                                  event_count > 5000000 and 
                                                  solenoid_current > 100 and 
                                                  collimator_diameter != 'Blocking'""",
                         "Is SRC production run"),

    ConditionSearchAlias('is_cpp_production', """daq_run == 'PHYSICS_CPP' and 
                                                  beam_current > 2 and 
                                                  event_count > 5000000 and 
                                                  solenoid_current > 100 and 
                                                  collimator_diameter != 'Blocking'""",
                         "Is CPP production run"),

    ConditionSearchAlias('is_production_long', """daq_run == 'PHYSICS_raw'
                                             beam_current > 2 and
                                             event_count > 5000000 and
                                             solenoid_current > 100 and
                                             collimator_diameter != 'Blocking'""",
                         "Is production run with long mode data"),

    ConditionSearchAlias('is_cosmic', '"cosmic" in run_config and beam_current < 1 and event_count > 5000',
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

    ConditionSearchAlias('status_calibration', "status == 3", "Run status = calibration"),

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
