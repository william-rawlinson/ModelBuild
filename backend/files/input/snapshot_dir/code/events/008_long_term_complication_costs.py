def get_longterm_complication_costs_impact(context: EventContext) -> EventImpact:
    """
    Captures costs associated with managing long-term complications in each health state.
    Applied as occupation impacts that differ between VBT and fusion patients based on different complication profiles.
    Complication rates increase over time as hardware ages and patients age.
    """
    # Initialize impact object
    impact = initialise_impact(context.health_states)
    
    # Determine current cycle number (0-based)
    cycle = context.cycle
    
    # Calculate time-dependent adjustment factor (approximating years)
    years_since_start = cycle / 4  # 4 quarters per year
    time_adjustment = float(context.params["complication_rate_time_dependency"]) ** years_since_start
    
    # Get base complication rates
    vbt_rate = float(context.params["vbt_complication_rate"]) * time_adjustment
    fusion_rate = float(context.params["fusion_complication_rate"]) * time_adjustment
    fusion_rev1_rate = float(context.params["fusion_revision1_complication_rate"]) * time_adjustment
    fusion_rev2_rate = float(context.params["fusion_revision2_complication_rate"]) * time_adjustment
    ineligible_rate = float(context.params["ineligible_complication_rate"]) * time_adjustment
    
    # Get complication management cost
    complication_cost = float(context.params["complication_management_cost"])
    
    # Calculate expected complication costs per cycle for each health state
    vbt_complication_cost = vbt_rate * complication_cost
    fusion_complication_cost = fusion_rate * complication_cost
    fusion_rev1_complication_cost = fusion_rev1_rate * complication_cost
    fusion_rev2_complication_cost = fusion_rev2_rate * complication_cost
    ineligible_complication_cost = ineligible_rate * complication_cost
    
    # Apply costs as occupation impacts for each health state
    impact.cost_occupation.add("Postoperative VBT", vbt_complication_cost)
    impact.cost_occupation.add("Postoperative Fusion", fusion_complication_cost)
    impact.cost_occupation.add("Postoperative Fusion Revision 1", fusion_rev1_complication_cost)
    impact.cost_occupation.add("Postoperative Fusion Revision 2", fusion_rev2_complication_cost)
    impact.cost_occupation.add("Ineligible For Further Fusion Revision", ineligible_complication_cost)
    
    return impact

longterm_complication_costs_event = EventSpec(
    event_name="Long-term Complication Costs",
    tags={"cost", "complication", "long-term"},
    calculation_function=get_longterm_complication_costs_impact,
)