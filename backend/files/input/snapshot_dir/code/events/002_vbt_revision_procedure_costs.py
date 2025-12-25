def get_vbt_revision_procedure_costs_impact(context: EventContext) -> EventImpact:
    """
    Applies costs when patients undergo VBT revision.
    Includes VBT revision device cost plus non-device costs.
    This is a flow impact from Postoperative VBT to VBT Revision state.
    """
    impact = initialise_impact(context.health_states)
    
    # Calculate VBT revision procedure cost (device + non-device)
    vbt_revision_cost = float(context.params["vbt_revision_device_cost"]) + float(context.params["non_device_cost"])
    
    # Apply cost as flow impact from postoperative VBT to VBT revision
    impact.cost_flow.add("Postoperative VBT", "VBT Revision", vbt_revision_cost)
    
    return impact

vbt_revision_procedure_costs_event = EventSpec(
    event_name="VBT Revision Procedure Costs",
    tags={"cost"},
    calculation_function=get_vbt_revision_procedure_costs_impact,
)