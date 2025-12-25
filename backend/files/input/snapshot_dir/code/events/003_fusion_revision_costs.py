def get_fusion_revision_costs_impact(context: EventContext) -> EventImpact:
    """
    Applies costs when patients undergo fusion revision procedures.
    Includes fusion device cost plus non-device costs.
    Applied as flow impacts when patients transition to Fusion Revision 1 or Fusion Revision 2 states.
    """
    # Initialize impact object
    impact = initialise_impact(context.health_states)
    
    # Calculate total cost for fusion revision
    fusion_revision_total_cost = float(context.params["fusion_device_cost"]) + float(context.params["non_device_cost"])
    
    # Apply costs as flow impacts for transitions to fusion revision states
    impact.cost_flow.add("Postoperative Fusion", "Fusion Revision 1", fusion_revision_total_cost)
    impact.cost_flow.add("Postoperative Fusion Revision 1", "Fusion Revision 2", fusion_revision_total_cost)
    
    return impact

fusion_revision_costs_event = EventSpec(
    event_name="Fusion Revision Costs",
    tags={"cost", "procedure", "revision"},
    calculation_function=get_fusion_revision_costs_impact,
)