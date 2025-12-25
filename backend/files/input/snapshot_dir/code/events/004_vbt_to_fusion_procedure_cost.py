def get_vbt_to_fusion_procedure_cost_impact(context: EventContext) -> EventImpact:
    """
    Applies the cost of fusion procedure when patients transition from Postoperative VBT to Spinal Fusion Index Procedure state.
    Includes both device cost (fusion_device_cost) and non-device costs (non_device_cost).
    """
    impact = initialise_impact(context.health_states)
    
    # Calculate total fusion procedure cost (device + non-device costs)
    fusion_device_cost = float(context.params["fusion_device_cost"])
    non_device_cost = float(context.params["non_device_cost"])
    total_fusion_cost = fusion_device_cost + non_device_cost
    
    # Apply cost when patients transition from Postoperative VBT to Spinal Fusion Index Procedure
    impact.cost_flow.add("Postoperative VBT", "Spinal Fusion Index Procedure", total_fusion_cost)
    
    return impact

vbt_to_fusion_procedure_cost_event = EventSpec(
    event_name="VBT to Fusion Procedure Cost",
    tags={"cost", "procedure", "fusion"},
    calculation_function=get_vbt_to_fusion_procedure_cost_impact,
)