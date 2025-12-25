def get_index_procedure_costs_impact(context: EventContext) -> EventImpact:
    """
    Applies the initial procedure costs when patients enter the model.
    For VBT arm, applies VBT index device cost plus non-device costs.
    For Fusion arm, applies fusion device cost plus non-device costs.
    These are one-time costs applied as flow impacts when patients transition from the index procedure states.
    """
    # Initialize impact object
    impact = initialise_impact(context.health_states)
    
    # Calculate total costs for each procedure type
    vbt_index_total_cost = float(context.params["vbt_index_device_cost"]) + float(context.params["non_device_cost"])
    fusion_index_total_cost = float(context.params["fusion_device_cost"]) + float(context.params["non_device_cost"])
    
    # Apply costs as flow impacts for transitions from index procedure states to postoperative states
    impact.cost_flow.add("VBT Index Procedure", "Postoperative VBT", vbt_index_total_cost)
    impact.cost_flow.add("Spinal Fusion Index Procedure", "Postoperative Fusion", fusion_index_total_cost)
    
    return impact

index_procedure_costs_event = EventSpec(
    event_name="Index Procedure Costs",
    tags={"cost", "procedure"},
    calculation_function=get_index_procedure_costs_impact,
)