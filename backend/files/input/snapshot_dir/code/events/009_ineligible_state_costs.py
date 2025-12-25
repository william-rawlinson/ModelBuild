def get_ineligible_state_costs_impact(context: EventContext) -> EventImpact:
    """
    Applies costs specific to patients who reach the 'Ineligible For Further Fusion Revision' state.
    These patients may require alternative management approaches or have higher ongoing care needs.
    Applied as occupation impacts for patients in the ineligible state.
    """
    # Initialize impact object
    impact = initialise_impact(context.health_states)
    
    # Calculate total additional costs for patients in the ineligible state
    pain_management_cost = float(context.params["ineligible_pain_management_cost_quarterly"])
    physical_therapy_cost = float(context.params["ineligible_physical_therapy_cost_quarterly"])
    assistive_device_cost = float(context.params["ineligible_assistive_device_cost_quarterly"])
    other_management_cost = float(context.params["ineligible_other_management_cost_quarterly"])
    
    total_ineligible_additional_cost = (
        pain_management_cost + 
        physical_therapy_cost + 
        assistive_device_cost + 
        other_management_cost
    )
    
    # Apply costs as occupation impact for the ineligible state
    impact.cost_occupation.add("Ineligible For Further Fusion Revision", total_ineligible_additional_cost)
    
    return impact

ineligible_state_costs_event = EventSpec(
    event_name="Ineligible State Costs",
    tags={"cost", "ineligible", "alternative management"},
    calculation_function=get_ineligible_state_costs_impact,
)