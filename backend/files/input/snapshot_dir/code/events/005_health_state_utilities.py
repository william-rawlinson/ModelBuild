def get_health_state_utilities_impact(context: EventContext) -> EventImpact:
    """
    Applies appropriate utility values based on patients' current health states.
    Different utility values for different health states.
    Utilities are applied as occupation impacts, adjusted by cycle length to convert to QALYs.
    """
    # Initialize impact object
    impact = initialise_impact(context.health_states)
    
    # Convert cycle length from months to years
    cycle_length_years = float(context.params["cycle_length"]) / 12.0
    
    # Apply utility values as occupation impacts for each health state
    # Index procedure states (preoperative)
    impact.qaly_occupation.add("VBT Index Procedure", float(context.params["preop_utility"]) * cycle_length_years)
    impact.qaly_occupation.add("Spinal Fusion Index Procedure", float(context.params["preop_utility"]) * cycle_length_years)
    
    # Postoperative states
    impact.qaly_occupation.add("Postoperative VBT", float(context.params["postop_vbt_utility"]) * cycle_length_years)
    impact.qaly_occupation.add("Postoperative Fusion", float(context.params["postop_fusion_utility"]) * cycle_length_years)
    
    # Revision states
    impact.qaly_occupation.add("VBT Revision", float(context.params["vbt_revision_utility"]) * cycle_length_years)
    impact.qaly_occupation.add("Fusion Revision 1", float(context.params["fusion_revision_utility"]) * cycle_length_years)
    impact.qaly_occupation.add("Fusion Revision 2", float(context.params["fusion_revision_utility"]) * cycle_length_years)
    
    # Postoperative revision states
    impact.qaly_occupation.add("Postoperative Fusion Revision 1", float(context.params["postop_fusion_revision_utility"]) * cycle_length_years)
    impact.qaly_occupation.add("Postoperative Fusion Revision 2", float(context.params["postop_fusion_revision_utility"]) * cycle_length_years)
    
    # Ineligible state
    impact.qaly_occupation.add("Ineligible For Further Fusion Revision", float(context.params["ineligible_fusion_utility"]) * cycle_length_years)
    
    return impact

health_state_utilities_event = EventSpec(
    event_name="Health State Utilities",
    tags={"utility", "qaly"},
    calculation_function=get_health_state_utilities_impact,
)