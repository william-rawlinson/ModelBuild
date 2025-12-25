def get_vbt_revision_procedure_cost_impact(context: EventContext) -> EventImpact:
    """
    Applies the cost of VBT revision when patients transition from Postoperative VBT to VBT Revision state.
    Includes both device cost (vbt_revision_device_cost) and non-device costs (non_device_cost).
    """
    impact = initialise_impact(context.health_states)
    
    # Calculate total VBT revision procedure cost (device + non-device costs)
    vbt_revision_device_cost = float(context.params["vbt_revision_device_cost"])
    non_device_cost = float(context.params["non_device_cost"])
    total_vbt_revision_cost = vbt_revision_device_cost + non_device_cost
    
    # Apply cost when patients transition from Postoperative VBT to VBT Revision
    impact.cost_flow.add("Postoperative VBT", "VBT Revision", total_vbt_revision_cost)
    
    return impact

vbt_revision_procedure_cost_event = EventSpec(
    event_name="VBT Revision Procedure Cost",
    tags={"cost", "procedure", "vbt", "revision"},
    calculation_function=get_vbt_revision_procedure_cost_impact,
)