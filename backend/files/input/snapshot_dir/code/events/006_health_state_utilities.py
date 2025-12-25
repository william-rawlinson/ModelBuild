def get_health_state_utilities_impact(context: EventContext) -> EventImpact:
    """
    Applies appropriate utility values based on patients' current health states.
    Applies postop_vbt_utility for Postoperative VBT state, postop_fusion_utility for all fusion postoperative states,
    and preop_utility for procedure states. Utilities are multiplied by cycle length to convert to QALYs.
    This is an occupancy impact.
    """
    impact = initialise_impact(context.health_states)
    
    # Convert cycle length from months to years
    cycle_length_years = float(context.params["cycle_length"]) / 12.0
    
    # Get utility values from parameters
    postop_vbt_utility = float(context.params["postop_vbt_utility"])
    postop_fusion_utility = float(context.params["postop_fusion_utility"])
    preop_utility = float(context.params["preop_utility"])
    
    # Apply postoperative VBT utility
    impact.qaly_occupation.add("Postoperative VBT", postop_vbt_utility * cycle_length_years)
    
    # Apply postoperative fusion utilities to all fusion postoperative states
    impact.qaly_occupation.add("Postoperative Fusion", postop_fusion_utility * cycle_length_years)
    impact.qaly_occupation.add("Postoperative Fusion Revision 1", postop_fusion_utility * cycle_length_years)
    impact.qaly_occupation.add("Postoperative Fusion Revision 2", postop_fusion_utility * cycle_length_years)
    impact.qaly_occupation.add("Ineligible For Further Fusion Revision", postop_fusion_utility * cycle_length_years)
    
    # Apply preoperative/procedure utilities to all procedure states
    impact.qaly_occupation.add("VBT Index Procedure", preop_utility * cycle_length_years)
    impact.qaly_occupation.add("Spinal Fusion Index Procedure", preop_utility * cycle_length_years)
    impact.qaly_occupation.add("VBT Revision", preop_utility * cycle_length_years)
    impact.qaly_occupation.add("Fusion Revision 1", preop_utility * cycle_length_years)
    impact.qaly_occupation.add("Fusion Revision 2", preop_utility * cycle_length_years)
    
    return impact

health_state_utilities_event = EventSpec(
    event_name="Health State Utilities",
    tags={"utility"},
    calculation_function=get_health_state_utilities_impact,
)