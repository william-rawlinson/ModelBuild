def get_second_fusion_revision_costs_impact(context: EventContext) -> EventImpact:
    """
    Applies costs when patients undergo their second fusion revision.
    Includes fusion device cost plus non-device costs.
    This is a flow impact from Postoperative Fusion Revision 1 to Fusion Revision 2 state.
    """
    impact = initialise_impact(context.health_states)
    
    # Calculate second fusion revision procedure cost (device + non-device)
    fusion_revision_cost = float(context.params["fusion_device_cost"]) + float(context.params["non_device_cost"])
    
    # Apply cost as flow impact from postoperative fusion revision 1 to fusion revision 2
    impact.cost_flow.add("Postoperative Fusion Revision 1", "Fusion Revision 2", fusion_revision_cost)
    
    return impact

second_fusion_revision_costs_event = EventSpec(
    event_name="Second Fusion Revision Costs",
    tags={"cost"},
    calculation_function=get_second_fusion_revision_costs_impact,
)