def get_vbt_revision_costs_impact(context: EventContext) -> EventImpact:
    """
    Applies costs when patients undergo VBT revision.
    Includes VBT revision device cost plus non-device costs.
    Applied as a flow impact when patients transition from Postoperative VBT to VBT Revision state.
    """
    # Initialize impact object
    impact = initialise_impact(context.health_states)
    
    # Calculate total cost for VBT revision
    vbt_revision_total_cost = float(context.params["vbt_revision_device_cost"]) + float(context.params["non_device_cost"])
    
    # Apply cost as flow impact for transition from Postoperative VBT to VBT Revision
    impact.cost_flow.add("Postoperative VBT", "VBT Revision", vbt_revision_total_cost)
    
    return impact

vbt_revision_costs_event = EventSpec(
    event_name="VBT Revision Costs",
    tags={"cost", "procedure", "revision"},
    calculation_function=get_vbt_revision_costs_impact,
)