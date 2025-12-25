def get_index_vbt_procedure_cost_impact(context: EventContext) -> EventImpact:
    """
    Applies the cost of the initial VBT procedure when patients are in the VBT Index Procedure state.
    Includes both device cost and non-device costs.
    """
    impact = initialise_impact(context.health_states)
    
    # Calculate total VBT index procedure cost (device + non-device costs)
    vbt_device_cost = float(context.params["vbt_device_cost"])
    non_device_cost = float(context.params["non_device_cost"])
    total_vbt_index_cost = vbt_device_cost + non_device_cost
    
    # Apply cost to patients in the VBT Index Procedure state
    impact.cost_occupation.add("VBT Index Procedure", total_vbt_index_cost)
    
    return impact

index_vbt_procedure_cost_event = EventSpec(
    event_name="Index VBT Procedure Cost",
    tags={"cost", "procedure", "vbt"},
    calculation_function=get_index_vbt_procedure_cost_impact,
)