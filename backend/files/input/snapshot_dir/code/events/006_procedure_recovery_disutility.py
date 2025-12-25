def get_procedure_recovery_disutility_impact(context: EventContext) -> EventImpact:
    """
    Captures temporary utility decrements during procedure and immediate recovery periods.
    Applied as flow impacts when patients transition into any procedure state (index or revision).
    This accounts for the temporary decrease in quality of life during surgical procedures and recovery.
    """
    # Initialize impact object
    impact = initialise_impact(context.health_states)
    
    # Convert cycle length from months to years
    cycle_length_years = float(context.params["cycle_length"]) / 12.0
    
    # Calculate QALY decrements for each procedure type
    recovery_fraction = float(context.params["recovery_duration_fraction"])
    
    vbt_index_qaly_decrement = -float(context.params["vbt_index_procedure_disutility"]) * recovery_fraction * cycle_length_years
    fusion_index_qaly_decrement = -float(context.params["fusion_index_procedure_disutility"]) * recovery_fraction * cycle_length_years
    vbt_revision_qaly_decrement = -float(context.params["vbt_revision_procedure_disutility"]) * recovery_fraction * cycle_length_years
    fusion_revision_qaly_decrement = -float(context.params["fusion_revision_procedure_disutility"]) * recovery_fraction * cycle_length_years
    
    # Apply disutilities as flow impacts for transitions into procedure states
    # For VBT revision
    impact.qaly_flow.add("Postoperative VBT", "VBT Revision", vbt_revision_qaly_decrement)
    
    # For fusion revisions
    impact.qaly_flow.add("Postoperative Fusion", "Fusion Revision 1", fusion_revision_qaly_decrement)
    impact.qaly_flow.add("Postoperative Fusion Revision 1", "Fusion Revision 2", fusion_revision_qaly_decrement)
    
    # For index procedures (model starts with patients in these states, but included for completeness)
    for state in context.health_states:
        if state != "VBT Index Procedure":
            impact.qaly_flow.add(state, "VBT Index Procedure", vbt_index_qaly_decrement)
        if state != "Spinal Fusion Index Procedure":
            impact.qaly_flow.add(state, "Spinal Fusion Index Procedure", fusion_index_qaly_decrement)
    
    return impact

procedure_recovery_disutility_event = EventSpec(
    event_name="Procedure Recovery Disutility",
    tags={"utility", "disutility", "procedure"},
    calculation_function=get_procedure_recovery_disutility_impact,
)