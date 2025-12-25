def get_first_fusion_revision_costs_impact(context: EventContext) -> EventImpact:
    """
    Applies costs when patients undergo their first fusion revision.
    Includes fusion device cost plus non-device costs.
    This is a flow impact from Postoperative Fusion to Fusion Revision 1 state.
    """
    impact = initialise_impact(context.health_states)
    
    # Calculate first fusion revision procedure cost (device + non-device)
    fusion_revision_cost = float(context.params["fusion_device_cost"]) + float(context.params["non_device_cost"])
    
    # Apply cost as flow impact from postoperative fusion to fusion revision 1
    impact.cost_flow.add("Postoperative Fusion", "Fusion Revision 1", fusion_revision_cost)
    
    return impact

first_fusion_revision_costs_event = EventSpec(
    event_name="First Fusion Revision Costs",
    tags={"cost"},
    calculation_function=get_first_fusion_revision_costs_impact,
)