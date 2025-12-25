def get_health_state_utilities_impact(context: EventContext) -> EventImpact:
    """
    Applies appropriate utility values to each health state based on the patient's current state.
    Uses postop_vbt_utility for Postoperative VBT state, postop_fusion_utility for all postoperative fusion states,
    and preop_utility for procedure states. Adjusts for cycle length to calculate QALYs.
    """
    impact = initialise_impact(context.health_states)
    
    # Get utility values from parameters
    postop_vbt_utility = float(context.params["postop_vbt_utility"])
    postop_fusion_utility = float(context.params["postop_fusion_utility"])
    preop_utility = float(context.params["preop_utility"])
    
    # Calculate cycle length in years
    cycle_length_months = float(context.params["cycle_length"])
    cycle_length_years = cycle_length_months / 12.0
    
    # Apply utilities to postoperative VBT state
    impact.qaly_occupation.add("Postoperative VBT", postop_vbt_utility * cycle_length_years)
    
    # Apply utilities to postoperative fusion states
    postop_fusion_states = [
        "Postoperative Fusion", 
        "Postoperative Fusion Revision 1", 
        "Postoperative Fusion Revision 2", 
        "Ineligible For Further Fusion Revision"
    ]
    for state in postop_fusion_states:
        impact.qaly_occupation.add(state, postop_fusion_utility * cycle_length_years)
    
    # Apply utilities to procedure states
    procedure_states = [
        "Spinal Fusion Index Procedure", 
        "VBT Index Procedure", 
        "VBT Revision", 
        "Fusion Revision 1", 
        "Fusion Revision 2"
    ]
    for state in procedure_states:
        impact.qaly_occupation.add(state, preop_utility * cycle_length_years)
    
    return impact

health_state_utilities_event = EventSpec(
    event_name="Health State Utilities",
    tags={"utility", "qaly"},
    calculation_function=get_health_state_utilities_impact,
)