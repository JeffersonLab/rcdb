/*
CREATE VIEW condition_values_view AS
SELECT
  runs.number    run,
  C1.int_value   event_count,
  C2.float_value events_rate,
  C3.int_value   temperature
FROM runs
  LEFT JOIN conditions C1
    ON C1.run_number = runs.number AND C1.condition_type_id = 1
  LEFT JOIN conditions C2
    ON C2.run_number = runs.number AND C2.condition_type_id = 2
  LEFT JOIN conditions C3
    ON C3.run_number = runs.number AND C3.condition_type_id = 3;
*/
/*
DROP VIEW IF EXISTS rcdb.condition_values_view RESTRICT;
CREATE VIEW condition_values_view AS
SELECT runs.number run
  ,event_count_table.int_value event_count
  ,events_rate_table.float_value events_rate
  ,temperature_table.int_value temperature
 FROM runs
  LEFT JOIN conditions event_count_table   ON event_count_table.run_number = runs.number AND event_count_table.condition_type_id = 1
  LEFT JOIN conditions events_rate_table   ON events_rate_table.run_number = runs.number AND events_rate_table.condition_type_id = 2
  LEFT JOIN conditions temperature_table   ON temperature_table.run_number = runs.number AND temperature_table.condition_type_id = 3
;
*/

DROP VIEW IF EXISTS rcdb.condition_values_view;
-- CREATE VIEW condition_values_view AS
CREATE TEMPORARY TABLE condition_values
SELECT runs.number run
  ,event_rate_table.float_value event_rate
  ,event_count_table.int_value event_count
  ,run_type_table.text_value run_type
  ,run_config_table.text_value run_config
  ,session_table.text_value session
  ,user_comment_table.text_value user_comment
  ,components_table.text_value components
  ,rtvs_table.text_value rtvs
  ,component_stats_table.text_value component_stats
  ,radiator_type_table.text_value radiator_type
  ,solenoid_current_table.float_value solenoid_current
  ,ps_converter_table.text_value ps_converter
  ,status_table.int_value status
  ,beam_energy_table.float_value beam_energy
  ,luminosity_table.float_value luminosity
  ,coherent_peak_table.float_value coherent_peak
  ,beam_current_table.float_value beam_current
  ,target_type_table.text_value target_type
  ,collimator_diameter_table.text_value collimator_diameter
  ,seandb_event_count_table.int_value seandb_event_count
  ,daq_run_table.text_value daq_run
  ,daq_setup_table.text_value daq_setup
  ,daq_config_table.text_value daq_config
  ,daq_trigger_table.text_value daq_trigger
  ,daq_mode_table.text_value daq_mode
  ,daq_blocks_table.text_value daq_blocks
  ,daq_calib_table.text_value daq_calib
  ,is_valid_run_end_table.bool_value is_valid_run_end
  ,radiator_index_table.int_value radiator_index
  ,radiator_id_table.int_value radiator_id
  ,polarization_direction_table.text_value polarization_direction
  ,run_length_table.int_value run_length
  ,polarimeter_converter_table.text_value polarimeter_converter
  ,evio_files_count_table.int_value evio_files_count
  ,evio_last_file_table.text_value evio_last_file
  ,trigger_eq_table.text_value trigger_eq
  ,trigger_type_table.text_value trigger_type
  ,cdc_fadc125_mode_table.int_value cdc_fadc125_mode
  ,offline_comment_table.text_value offline_comment
  ,trigger_ts_type_table.int_value trigger_ts_type
  ,trigger_ts_gtp_pres_table.text_value trigger_ts_gtp_pres
  ,trigger_ts_coin_wind_table.int_value trigger_ts_coin_wind
  ,trigger_ts_sync_int_table.int_value trigger_ts_sync_int
  ,trigger_block_level_table.int_value trigger_block_level
  ,trigger_buffer_level_table.int_value trigger_buffer_level
  ,fcal_fadc250_mode_table.int_value fcal_fadc250_mode
  ,bcal_fadc250_mode_table.int_value bcal_fadc250_mode
  ,beam_on_current_table.float_value beam_on_current
  ,polarization_angle_table.float_value polarization_angle
 FROM runs
  LEFT JOIN conditions event_rate_table   ON event_rate_table.run_number = runs.number AND event_rate_table.condition_type_id = 1
  LEFT JOIN conditions event_count_table   ON event_count_table.run_number = runs.number AND event_count_table.condition_type_id = 2
  LEFT JOIN conditions run_type_table   ON run_type_table.run_number = runs.number AND run_type_table.condition_type_id = 3
  LEFT JOIN conditions run_config_table   ON run_config_table.run_number = runs.number AND run_config_table.condition_type_id = 4
  LEFT JOIN conditions session_table   ON session_table.run_number = runs.number AND session_table.condition_type_id = 5
  LEFT JOIN conditions user_comment_table   ON user_comment_table.run_number = runs.number AND user_comment_table.condition_type_id = 6
  LEFT JOIN conditions components_table   ON components_table.run_number = runs.number AND components_table.condition_type_id = 7
  LEFT JOIN conditions rtvs_table   ON rtvs_table.run_number = runs.number AND rtvs_table.condition_type_id = 8
  LEFT JOIN conditions component_stats_table   ON component_stats_table.run_number = runs.number AND component_stats_table.condition_type_id = 9
  LEFT JOIN conditions radiator_type_table   ON radiator_type_table.run_number = runs.number AND radiator_type_table.condition_type_id = 10
  LEFT JOIN conditions solenoid_current_table   ON solenoid_current_table.run_number = runs.number AND solenoid_current_table.condition_type_id = 11
  LEFT JOIN conditions ps_converter_table   ON ps_converter_table.run_number = runs.number AND ps_converter_table.condition_type_id = 12
  LEFT JOIN conditions status_table   ON status_table.run_number = runs.number AND status_table.condition_type_id = 13
  LEFT JOIN conditions beam_energy_table   ON beam_energy_table.run_number = runs.number AND beam_energy_table.condition_type_id = 14
  LEFT JOIN conditions luminosity_table   ON luminosity_table.run_number = runs.number AND luminosity_table.condition_type_id = 15
  LEFT JOIN conditions coherent_peak_table   ON coherent_peak_table.run_number = runs.number AND coherent_peak_table.condition_type_id = 16
  LEFT JOIN conditions beam_current_table   ON beam_current_table.run_number = runs.number AND beam_current_table.condition_type_id = 17
  LEFT JOIN conditions target_type_table   ON target_type_table.run_number = runs.number AND target_type_table.condition_type_id = 18
  LEFT JOIN conditions collimator_diameter_table   ON collimator_diameter_table.run_number = runs.number AND collimator_diameter_table.condition_type_id = 19
  LEFT JOIN conditions seandb_event_count_table   ON seandb_event_count_table.run_number = runs.number AND seandb_event_count_table.condition_type_id = 20
  LEFT JOIN conditions daq_run_table   ON daq_run_table.run_number = runs.number AND daq_run_table.condition_type_id = 21
  LEFT JOIN conditions daq_setup_table   ON daq_setup_table.run_number = runs.number AND daq_setup_table.condition_type_id = 22
  LEFT JOIN conditions daq_config_table   ON daq_config_table.run_number = runs.number AND daq_config_table.condition_type_id = 23
  LEFT JOIN conditions daq_trigger_table   ON daq_trigger_table.run_number = runs.number AND daq_trigger_table.condition_type_id = 24
  LEFT JOIN conditions daq_mode_table   ON daq_mode_table.run_number = runs.number AND daq_mode_table.condition_type_id = 25
  LEFT JOIN conditions daq_blocks_table   ON daq_blocks_table.run_number = runs.number AND daq_blocks_table.condition_type_id = 26
  LEFT JOIN conditions daq_calib_table   ON daq_calib_table.run_number = runs.number AND daq_calib_table.condition_type_id = 27
  LEFT JOIN conditions is_valid_run_end_table   ON is_valid_run_end_table.run_number = runs.number AND is_valid_run_end_table.condition_type_id = 28
  LEFT JOIN conditions radiator_index_table   ON radiator_index_table.run_number = runs.number AND radiator_index_table.condition_type_id = 29
  LEFT JOIN conditions radiator_id_table   ON radiator_id_table.run_number = runs.number AND radiator_id_table.condition_type_id = 30
  LEFT JOIN conditions polarization_direction_table   ON polarization_direction_table.run_number = runs.number AND polarization_direction_table.condition_type_id = 31
  LEFT JOIN conditions run_length_table   ON run_length_table.run_number = runs.number AND run_length_table.condition_type_id = 32
  LEFT JOIN conditions polarimeter_converter_table   ON polarimeter_converter_table.run_number = runs.number AND polarimeter_converter_table.condition_type_id = 33
  LEFT JOIN conditions evio_files_count_table   ON evio_files_count_table.run_number = runs.number AND evio_files_count_table.condition_type_id = 34
  LEFT JOIN conditions evio_last_file_table   ON evio_last_file_table.run_number = runs.number AND evio_last_file_table.condition_type_id = 35
  LEFT JOIN conditions trigger_eq_table   ON trigger_eq_table.run_number = runs.number AND trigger_eq_table.condition_type_id = 36
  LEFT JOIN conditions trigger_type_table   ON trigger_type_table.run_number = runs.number AND trigger_type_table.condition_type_id = 37
  LEFT JOIN conditions cdc_fadc125_mode_table   ON cdc_fadc125_mode_table.run_number = runs.number AND cdc_fadc125_mode_table.condition_type_id = 38
  LEFT JOIN conditions offline_comment_table   ON offline_comment_table.run_number = runs.number AND offline_comment_table.condition_type_id = 39
  LEFT JOIN conditions trigger_ts_type_table   ON trigger_ts_type_table.run_number = runs.number AND trigger_ts_type_table.condition_type_id = 40
  LEFT JOIN conditions trigger_ts_gtp_pres_table   ON trigger_ts_gtp_pres_table.run_number = runs.number AND trigger_ts_gtp_pres_table.condition_type_id = 41
  LEFT JOIN conditions trigger_ts_coin_wind_table   ON trigger_ts_coin_wind_table.run_number = runs.number AND trigger_ts_coin_wind_table.condition_type_id = 42
  LEFT JOIN conditions trigger_ts_sync_int_table   ON trigger_ts_sync_int_table.run_number = runs.number AND trigger_ts_sync_int_table.condition_type_id = 43
  LEFT JOIN conditions trigger_block_level_table   ON trigger_block_level_table.run_number = runs.number AND trigger_block_level_table.condition_type_id = 44
  LEFT JOIN conditions trigger_buffer_level_table   ON trigger_buffer_level_table.run_number = runs.number AND trigger_buffer_level_table.condition_type_id = 45
  LEFT JOIN conditions fcal_fadc250_mode_table   ON fcal_fadc250_mode_table.run_number = runs.number AND fcal_fadc250_mode_table.condition_type_id = 46
  LEFT JOIN conditions bcal_fadc250_mode_table   ON bcal_fadc250_mode_table.run_number = runs.number AND bcal_fadc250_mode_table.condition_type_id = 54
  LEFT JOIN conditions beam_on_current_table   ON beam_on_current_table.run_number = runs.number AND beam_on_current_table.condition_type_id = 55
  LEFT JOIN conditions polarization_angle_table   ON polarization_angle_table.run_number = runs.number AND polarization_angle_table.condition_type_id = 56
;