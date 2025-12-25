def get_fusion_procedure_costs_after_vbt_impact(context: EventContext) -> EventImpact:
    """
    Applies costs when VBT patients later undergo fusion.
    Includes fusion device cost plus non-device costs.
    This is a flow impact from Postoperative VBT to Postoperative Fusion state.
    """
    impact = initialise_impact(context.health_states)
    
    # Calculate fusion procedure cost (device + non-device)
    fusion_cost = float(context.params["fusion_device_cost"]) + float(context.params["non_device_cost"])
    
    # Apply cost as flow impact from postoperative VBT to postoperative fusion
    impact.cost_flow.add("Postoperative VBT", "Postoperative Fusion", fusion_cost)
    
    return impact

fusion_procedure_costs_after_vbt_event = EventSpec(
    event_name="Fusion Procedure Costs After VBT",
    tags={"cost"},
    calculation_function=get_fusion_procedure_costs_after_vbt_impact,
)