def get_index_fusion_procedure_cost_impact(context: EventContext) -> EventImpact:
    """
    Applies the cost of the initial spinal fusion procedure when patients are in the Spinal Fusion Index Procedure state.
    Includes both device cost and non-device costs.
    """
    impact = initialise_impact(context.health_states)
    
    # Calculate total fusion index procedure cost (device + non-device costs)
    fusion_device_cost = float(context.params["fusion_device_cost"])
    non_device_cost = float(context.params["non_device_cost"])
    total_fusion_index_cost = fusion_device_cost + non_device_cost
    
    # Apply cost to patients in the Spinal Fusion Index Procedure state
    impact.cost_occupation.add("Spinal Fusion Index Procedure", total_fusion_index_cost)
    
    return impact

index_fusion_procedure_cost_event = EventSpec(
    event_name="Index Fusion Procedure Cost",
    tags={"cost", "procedure", "fusion"},
    calculation_function=get_index_fusion_procedure_cost_impact,
)