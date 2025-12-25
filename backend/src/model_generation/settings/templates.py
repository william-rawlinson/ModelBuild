health_states_prompt = """We are going to work together to design the health states for a cohort Markov model.
Your task is to propose a suitable list of health states based on the model description and the available parameters.

Key objective: MINIMAL state space
- Your primary goal is to propose the smallest (minimal) set of health states that can faithfully represent the model
  described and can be parameterised using the available parameters.
- Do NOT add states “just in case”. Only add a state if it is required to represent different costs, QALYs, or transition
  structure that cannot be represented otherwise.

Respect the model description, but do not be constrained by it
- The model description may explicitly suggest a set of health states (e.g., “use states A, B, C”).
- If that proposed set is not sufficient or is mismatched with the required costs/QALYs/transitions, you MUST modify it.
  It is acceptable to add, remove, merge, or rename states to achieve a coherent and minimal state space, but only \
if there is a good reason to do so.

When tunnel states are required (important)
- If costs or QALYs depend on “time since entering” a state(e.g., higher cost in the second cycle after surgery, different
  utility in the third year post-event, or different transition risk in cycles 2+ after an event), a standard Markov
  state will not be sufficient. 
- In those cases you should introduce TUNNEL STATES:
  - Tunnel states are time-limited states that represent being in a condition for a specific duration since entry.
  - Patients pass through them sequentially (e.g., PostOp_0 → PostOp_1 → PostOp_LongTerm), enabling different per-cycle
    occupancy costs/QALYs and/or different transition risks by time-since-entry.
  - Use tunnel states only when necessary (i.e., when time-since-entry changes costs/QALYs/transition behavior).
- IMPORTANTLY, we do not need tunnel states for costs / QALYs that are incurred upon transition to a state, these can be \
handled by simply associating cost and QALY impacts with transitions

Tunnel state naming convention (use this exactly)
- If a state requires tunnel structure, use:
    "<BASE_STATE>__tunnel_<k>"
  for k = 0, 1, 2, ... for sequential cycles after entry, and then a final non-tunnel long-term state:
    "<BASE_STATE>__long_term"
Examples:
- "PostOp__tunnel_0", "PostOp__tunnel_1", "PostOp__long_term"
- "Revision__tunnel_0", "Revision__long_term"

Output requirements
1) Provide a short rationale explaining:
   - why the proposed states are sufficient and minimal
   - where (if anywhere) tunnel states were required and why
2) Return ONLY the final ordered list of health state names inside:
   <model_health_states></model_health_states>
   Use a JSON array of strings inside the tags.

Here is the model description and available parameters:

<model_description>
{model_description}
</model_description>

<available_parameters>
{available_parameters}
</available_parameters>
"""

initial_occupancy_prompt = """We are now going to define the INITIAL HEALTH STATE OCCUPANCIES for the cohort
at the start of the Markov model (cycle 0).

Your task is to specify, for each treatment arm, the proportion of the cohort that begins in each health state.

Important principles
- Initial occupancies must form a valid probability distribution for EACH treatment:
    - All proportions must be between 0 and 1
    - Proportions must sum to exactly 1.0 for each treatment
- Initial occupancies may differ by treatment arm if this is clinically or logically implied
  (e.g., different index procedures, eligibility criteria, or starting pathways).
- If there is no strong justification for differences, it is acceptable (and often preferred)
  for treatments to share the same initial distribution.

Respect the model, but prioritise coherence
- The model description may explicitly state where patients start (e.g., “all patients begin in PFS”).
- If that statement is inconsistent with the final set of health states (e.g., tunnel states, procedural states),
  you MUST adapt the initial occupancies accordingly.
- In particular:
    - If tunnel states exist that represent an index event or immediate post-event period,
      it is often appropriate for patients to start in the earliest tunnel state (e.g., "__tunnel_0")
      rather than a long-term state.
    - Long-term states (e.g., "__long_term") should generally NOT have initial occupancy unless
      explicitly justified.

Minimality and realism
- Do NOT spread small probabilities across many states unless necessary.
- In most models, the majority (or all) of the cohort should start in a single clinically meaningful state.
- Use additional non-zero occupancies only when clearly required by the model structure.

Output requirements
- Return a single dictionary inside:
    <initial_state_occupancy></initial_state_occupancy>
- The dictionary must be of the form:
    {{
        "<TREATMENT_NAME>": {{
            "<HEALTH_STATE>": <proportion>,
            ...
        }},
        ...
    }}
- Every health state must appear for every treatment (use 0.0 where appropriate).
- Use numeric values (floats), not strings.
- Do NOT include explanatory text inside the tags.

You may include brief reasoning outside the tags if helpful.

The list of modelled treatments is provided below.

<treatments>
{treatments}
</treatments>
"""
