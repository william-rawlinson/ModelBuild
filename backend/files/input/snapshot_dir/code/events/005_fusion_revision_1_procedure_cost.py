def get_fusion_revision_1_procedure_cost_impact(context: EventContext) -> EventImpact:
    """
    Applies the cost of the first fusion revision when patients transition from Postoperative Fusion to Fusion Revision 1 state.
    Includes both device cost (fusion_device_cost) and non-device costs (non_device_cost).
    """
    impact = initialise_impact(context.health_states)
    
    # Calculate total fusion revision procedure cost (device + non-device costs)
    fusion_device_cost = float(context.params["fusion_device_cost"])
    non_device_cost = float(context.params["non_device_cost"])
    total_fusion_revision_cost = fusion_device_cost + non_device_cost
    
    # Apply cost when patients transition from Postoperative Fusion to Fusion Revision 1
    impact.cost_flow.add("Postoperative Fusion", "Fusion Revision 1", total_fusion_revision_cost)
    
    return impact

fusion_revision_1_procedure_cost_event = EventSpec(
    event_name="Fusion Revision 1 Procedure Cost",
    tags={"cost", "procedure", "fusion", "revision"},
    calculation_function=get_fusion_revision_1_procedure_cost_impact,
)