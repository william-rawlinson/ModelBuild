# -------------------------------
# 1) ORCHESTRATOR INTRO (first prompt)
# -------------------------------

orchestrator_introduction = """We are going to work together to code a health economic Markov model in Python. \
The model will be built using a framework. The framework uses parameters, a transition matrix, Events, and a generic runner. \
For now, your task is to create a set of Events we can use for the model. To do this, first read the \
description of Events and their role in detail.

<events_and_their_role>
- In each model cycle, Events are evaluated to determine cost and QALY impacts for that cycle and treatment arm.
- An Event can contribute impacts in two distinct ways:
    - Occupancy impacts: per-patient costs and QALYs accrued while patients occupy particular health states
      (represented as vectors over health states).
    - Flow impacts: per-transition costs and QALYs accrued when patients move from one health state to another
      within the cycle (represented as matrices over state→state transitions).
- Event calculation functions may depend on the model cycle, treatment arm, and model parameters.
- The generic runner combines state occupancies and the model’s transition matrix to convert Event impacts into
  cohort-level costs and QALYs for each cycle, aggregates these over time, and applies all discounting.
</events_and_their_role>

<defining_a_good_set_of_events>
- Each distinct real-world mechanism/trigger should be represented by exactly one Event. That Event may include both
  cost and QALY impacts (and both occupancy and flow components) so the trigger/event rate is calculated once and
  its full consequences are applied together.
- Avoid duplicating the same event-rate logic across multiple Events.
- Overlapping Events that describe the same consequence will result in double counting and must be avoided.
- Events must not attempt to define or reproduce transition probabilities. If a cost/QALY impact is conditional
  on a transition, express it as a flow impact rather than recalculating transition probabilities within the Event.
- Events must only define per-patient cost and/or QALY impacts (via occupancy and/or flow).
  They must not update state occupancies, apply discounting, calculate transitions, or implement other model mechanics. \
  Assume all transition probabilities and state occupancies have already been calculated, as they have been elsewhere.
- A good set of Events is not overly granular.
</defining_a_good_set_of_events>

Two simple Events are provided below to illustrate the concept.

<simple_event_examples>
def get_progression_cost_impact(context: EventContext) -> EventImpact:
    impact = initialise_impact(context.health_states)
    cost = float(context.params["progression_cost"])
    impact.cost_flow.add("PFS", "PPS", cost)
    return impact

progression_cost_event = EventSpec(
    event_name="Progression cost",
    calculation_function=progression_cost_event,
)

def get_healthstate_utility_impact(context: EventContext) -> EventImpact:
    impact = initialise_impact(context.health_states)
    cycle_length = float(context.params["cycle_length"])
    impact.qaly_occupation.add("PFS", float(context.params["pfs_utility"]) * cycle_length)
    impact.qaly_occupation.add("PPS", float(context.params["pps_utility"]) * cycle_length)
    return impact

healthstate_utility_event = EventSpec(
    event_name="Health state utility",
    calculation_function=healthstate_utility_event,
)
</simple_event_examples>

Now, demarcated by <model_description></model_description> is a description of the model.
Demarcated by <available_parameters></available_parameters> is an initial set of parameters (we may add more).
Based on these, devise a list of Events for the model. You should stick to the model description \
as much as you can, avoid adding extra elements unless these are needed to complete the model.

Return a dictionary where each key is an Event name and each value is a description of the Event.
Return your dictionary in <event_recommendations></event_recommendations> tags.

<model_description>
{model_description}
</model_description>

<available_parameters>
{available_parameters}
</available_parameters>
"""


# -----------------------------------------
# 2) BUILD-LOOP INTRO (second prompt, one time)
# -----------------------------------------

events_build_loop_introduction = """Great. We will now implement the Events you listed, one-by-one. 

We will repeat two steps per Event:
1) Conceptualise the Event precisely 
2) Implement the Event in code.

First, read through the detailed account of Event mechanics below (<event_mechanics></event_mechanics>). Then, \
read through guidance on how you can add additional parameters to the model if required (<adding_additional_parameters>\
</adding_additional_parameters>). 

<event_mechanics>
- Each Event consists of:
  (1) a calculation function:
        def <get_event_name_impact>(ctx: EventContext) -> EventImpact
  (2) an EventSpec that references it.
- For the calculation function, you should use the following helpers (pre-defined, you do not need to build these)
- impact = initialise_impact(ctx.health_states), to initialise the impact return
- Occupancy impacts:
    impact.cost_occupation.add("<STATE>", <cost_value>), to add a cost occupancy impact to a state
    impact.qaly_occupation.add("<STATE>", <qaly_value>), to add a QALY occupancy impact to a state
- Flow impacts:
    impact.cost_flow.add("<ORIGIN_STATE>", "<DEST_STATE>", <cost_value>), to add a cost flow impact to a transition
    impact.qaly_flow.add("<ORIGIN_STATE>", "<DEST_STATE>", <qaly_value>), to add a qaly flow impact to a transition
</event_mechanics>

<adding_additional_parameters>
Importantly, you may be missing some parameters required to produce the \
calculation function of an event. If this is the case, you should add parameters with sensible, assumed values, \
during conceptualisation. These parameters will then be accessible through the context.params \
dictionary when you write the calculation function code. You should not add parameters that are simply \
conversions of other parameters, as these are not true independent parameters. Instead perform the conversion \
calculation in your code.

- To add parameters you must include a JSON array within <additional_parameters></additional_parameters> tags as \
part of your response to the conceptualisation prompt.
- Each element must have the following fields:
    - parameter_name: string
    - value: number or null
    - description: string 
    - distribution: string or null
    - standard_error: number or null
    - notes: string (optional; include only if something is ambiguous)
</adding_additional_parameters>

Acknowledge, and I will provide the first Event to conceptualise and implement.
"""


# -----------------------------------------
# 3) PER-EVENT CONCEPTUALISATION (called each iteration)
# -----------------------------------------

event_conceptualisation = """Now conceptualise the following Event in detail.
Please plan out the calculations you will \
programme. You should note all of the parameters you will be using, and \
any assumptions you will make. Importantly, you may be missing some parameters required to produce the \
generation function. If this is the case, you should use the mechanism described above to add these. \
Please note you will have access to the time horizon (in years) and cycle length (in years) as further variables.


Target Event:
<current_event_name>
{current_event_name}
</current_event_name>

Event description (from recommendations):
<current_event_description>
{current_event_description}
</current_event_description>

Context:
<model_description>
{model_description}
<model_description>

<available_parameters>
{available_parameters}
</available_parameters>

<model_health_states>
{model_health_states}
</model_health_states>

Return:
- A clear conceptual plan in prose/bullets
- Optionally <additional_parameters>...</additional_parameters> if needed
"""


# -----------------------------------------
# 4) PER-EVENT BUILD (called each iteration)
# -----------------------------------------

event_build = """Now implement the Event in Python code, exactly as conceptualised.

Requirements:
- Always include the Event code within <final_code></final_code> tags.
- The <final_code> block must contain exactly ONE Event function and exactly ONE EventSpec.
- The Event function name should be stable and descriptive (snake_case, of the form get_<event_name>_impact
- Access the cycle number by using context.cycle
- Access the treatment name by using context.treatment
- Access the model health states using context.health_states
- Use context.params["..."] for all parameter values; do not hard-code numbers.
- Use context.cycle_length_years, and context.time_horizon_years if you need to access these variable values
- Please note, to access parameter values, you just need \
to use the variable name (e.g., params[variable_name], you must not try to access values using 'params[variable_name]["value"]' as the parameters \
dictionary will be flattened.
- Use occupancy vs flow impacts correctly:
    - Occupancy impacts for costs/utilities that accrue while in a state.
    - Flow impacts for costs/utilities that occur only when a transition happens.


Return only:
- Any thinking you require
- <final_code>...</final_code> with exactly ONE Event function and exactly ONE EventSpec
"""

event_meta_data = """Brilliant. Now we are going to generate some helpful metadata for the event. 

Requirements:
- Always include the metadata within <metadata></metadata> tags.
- Include only a JSON within the <metadata> tags
- the JSON should have the fields:
    - 'description': a brief description of the real-world mechanism/trigger the Event represents, and the cost and/or \
QALY impact associated with the event (including what under conditions/rate this is applied)
    - 'assumptions': Any important calculation assumptions made in the Event
    - 'applies_to_treatments': List of exact treatment names to which the event applies (e.g., for which the event has non-zero impacts)
    - 'applies_to_states': List of exact health state names to which the event applies (e.g., for which the event has non-zero impacts)
    - 'impact_type': 'cost' if the event has purely cost impact, 'qaly' if the event has purely qaly impact, 'both' if the event has both cost and qaly impact
"""

#TODO complete