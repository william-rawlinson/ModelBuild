def get_vbt_to_fusion_conversion_costs_impact(context: EventContext) -> EventImpact:
    """
    Applies costs when VBT patients later undergo an index fusion procedure.
    Includes fusion device cost plus non-device costs.
    Applied as a flow impact when patients transition from Postoperative VBT to Postoperative Fusion state.
    """
    # Initialize impact object
    impact = initialise_impact(context.health_states)
    
    # Calculate total cost for fusion conversion
    fusion_conversion_total_cost = float(context.params["fusion_device_cost"]) + float(context.params["non_device_cost"])
    
    # Apply cost as flow impact for transition from Postoperative VBT to Postoperative Fusion
    impact.cost_flow.add("Postoperative VBT", "Postoperative Fusion", fusion_conversion_total_cost)
    
    return impact

vbt_to_fusion_conversion_costs_event = EventSpec(
    event_name="VBT to Fusion Conversion Costs",
    tags={"cost", "procedure", "conversion"},
    calculation_function=get_vbt_to_fusion_conversion_costs_impact,
)