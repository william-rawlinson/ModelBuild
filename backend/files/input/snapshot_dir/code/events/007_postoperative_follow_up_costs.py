def get_postoperative_followup_costs_impact(context: EventContext) -> EventImpact:
    """
    Captures routine follow-up costs in the postoperative periods.
    Applied as occupation impacts for patients in postoperative states.
    Varies between VBT and fusion patients based on different monitoring requirements.
    Costs decrease over time as follow-up visits become less frequent.
    """
    # Initialize impact object
    impact = initialise_impact(context.health_states)
    
    # Determine current cycle number (0-based)
    cycle = context.cycle
    
    # Calculate time-dependent adjustment factor (approximating years)
    years_since_start = cycle / 4  # 4 quarters per year
    time_adjustment = float(context.params["followup_cost_time_dependency"]) ** years_since_start
    
    # Apply adjusted follow-up costs as occupation impacts for each postoperative state
    vbt_followup_cost = float(context.params["postop_vbt_followup_cost_quarterly"]) * time_adjustment
    fusion_followup_cost = float(context.params["postop_fusion_followup_cost_quarterly"]) * time_adjustment
    fusion_revision_followup_cost = float(context.params["postop_fusion_revision_followup_cost_quarterly"]) * time_adjustment
    ineligible_followup_cost = float(context.params["ineligible_fusion_followup_cost_quarterly"]) * time_adjustment
    
    # Apply costs to respective states
    impact.cost_occupation.add("Postoperative VBT", vbt_followup_cost)
    impact.cost_occupation.add("Postoperative Fusion", fusion_followup_cost)
    impact.cost_occupation.add("Postoperative Fusion Revision 1", fusion_revision_followup_cost)
    impact.cost_occupation.add("Postoperative Fusion Revision 2", fusion_revision_followup_cost)
    impact.cost_occupation.add("Ineligible For Further Fusion Revision", ineligible_followup_cost)
    
    return impact

postoperative_followup_costs_event = EventSpec(
    event_name="Postoperative Follow-up Costs",
    tags={"cost", "followup", "monitoring"},
    calculation_function=get_postoperative_followup_costs_impact,
)