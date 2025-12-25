def get_procedure_disutility_impact(context: EventContext) -> EventImpact:
    """
    Applies temporary disutility during cycles when patients are undergoing procedures (index or revision).
    This reflects the temporary reduction in quality of life during the procedure and immediate recovery period.
    This is an occupancy impact for procedure states.
    """
    impact = initialise_impact(context.health_states)
    
    # Convert cycle length from months to years
    cycle_length_years = float(context.params["cycle_length"]) / 12.0
    
    # Get disutility values from parameters
    vbt_procedure_disutility = float(context.params["vbt_procedure_disutility"])
    fusion_procedure_disutility = float(context.params["fusion_procedure_disutility"])
    
    # Apply VBT procedure disutilities (as negative QALYs)
    impact.qaly_occupation.add("VBT Index Procedure", -vbt_procedure_disutility * cycle_length_years)
    impact.qaly_occupation.add("VBT Revision", -vbt_procedure_disutility * cycle_length_years)
    
    # Apply fusion procedure disutilities (as negative QALYs)
    impact.qaly_occupation.add("Spinal Fusion Index Procedure", -fusion_procedure_disutility * cycle_length_years)
    impact.qaly_occupation.add("Fusion Revision 1", -fusion_procedure_disutility * cycle_length_years)
    impact.qaly_occupation.add("Fusion Revision 2", -fusion_procedure_disutility * cycle_length_years)
    
    return impact

procedure_disutility_event = EventSpec(
    event_name="Procedure Disutility",
    tags={"utility"},
    calculation_function=get_procedure_disutility_impact,
)