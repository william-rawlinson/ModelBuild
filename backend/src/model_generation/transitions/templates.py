
transition_matrix_introduction = """We are going to work together to produce a transition matrix generation function \
for a cohort Markov model. The generation function (written using Python) calculates the transition probabilities for \
for all health states for a given cycle and treatment arm. Guidance on building the generation function \
is provided below (see <guidance_on_building_transition_matrix_generation_function>\
</guidance_on_building_transition_matrix_generation_function>). 

<guidance_on_building_transition_matrix_generation_function>
- You should name the transition matrix generation function get_transition_matrix
- The transition matrix generation function must have the signature:
    def get_transition_matrix(context: TransitionMatrixContext) -> np.ndarray
- To ensure you return an array, you should use transition_matrix.as_array() where transition_matrix is your \
NamedTransitionMatrix
- Within the transition matrix generation function, use the provided TransitionContext fields:
    - context.health_states (list (string) of all states in model)
    - context.cycle (int)
    - context.treatment (string)
    - context.params (dict of parameters, see <available_parameters></available_parameters> below)
    - context.cycle_length_years (float) variable with cycle length in years
    - context.time_horizon_years (float) variable with time horizon in years
- Do NOT hard-code parameter values, always use the parameters from the context.params dictionary
- Use this helper to initialise the transition matrix
    transition_matrix = NamedTransitionMatrix(context.health_states)
- Set explicit probabilities using:
    transition_matrix.set("<ORIGIN_STATE>", "<DESTINATION_STATE>", <probability_expression>)
- Ensure the transition_matrix represents probabilities (not rates). If you are given rates, convert using:
    p = 1 - exp(-rate * cycle_length_years)
  (cycle_length_years should come from params if needed).
-  You do not need to define NamedTransitionMatrix, or TransitionMatrixContext. These have already been defined
</guidance_on_building_transition_matrix_generation_function>

A description of the model we are going to build is provided below (demarked by <model_description></model_description>). \
A description of the available model parameters is also provided below (demarked by <available_model_parameters></available_model_parameters>). \
A list of the model health states is also provided below (demarked by <model_health_states>).

<model_description>
{model_description}
</model_description>

<available_model_parameters>
{model_parameters}
</available_model_parameters>

<model_health_states>
{model_health_states}
</model_health_states>

Once you have understood all these instructions, and the model we are building, please acknowledge this. Then, I will \
follow up with the instructions for building the transition matrix generation function. 
"""

transition_matrix_conceptualisation = """Brilliant. Now I want you to conceptualise the transition matrix \
generation function. Please plan out the calculations you will \
programme. You should note all of the parameters you will be using, and \
any assumptions you will make. Importantly, you may be missing some parameters required to produce the \
generation function. If this is the case, you should use the mechanism described below (<adding_parameters_mechanism>\
</adding_parameters_mechanism>) to add parameters with sensible, assumed values, so you can complete the \
calculations. These parameters will then be accessible through the context.params dictionary when you write the \
calculation function code. You should not add parameters that are simply \
conversions of other parameters, as these are not true independent parameters. Instead perform the conversion \
calculation in your code.

<adding_parameters_mechanism>
- To add parameters you must include a JSON array within <additional_parameters></additional_parameters> tags as \
part of your answer. 
- Each element must have the following fields:
    - parameter_name: string
    - value: number or null
    - description: string 
    - distribution: string or null
    - standard_error: number or null
    - notes: string (optional; include only if something is ambiguous)
</adding_parameters_mechanism>

Now, please thoroughly conceptualise the transition matrix generation function, and define additional parameters if \
they are needed."""

transition_set_build = """Amazing. Now, please build the transition matrix generation function. 
Return your final code within <final_code></final_code> tags. Please note, to access parameter values, you just need \
to use the variable name (e.g., params[variable_name], you must not try to access values using 'params[variable_name]["value"]' as the parameters \
dictionary will be flattened.
"""

transitions_meta_data = """Brilliant. Now we are going to generate some helpful metadata for the transition matrix. 

Requirements:
- Always include the metadata within <metadata></metadata> tags.
- Include only a JSON within the <metadata> tags
- the JSON should have the fields:
        - 'description': Describe the patient flow through the model in terms of possible transitions, and the approach used to calculate the transitions
    - 'assumptions': Any important assumptions made in calculating the transitions
    - 'transitions': A dictionary with keys that match exactly each and every health state name. The values are the exact health \
states names for which a transition is possible from the key health state.  YOU MUST INCLUDE EVERY HEALTH STATE AS A KEY.
    - 'state_diagram': A list of lists, each sublist is one 'row' of a state diagram, and the content of each sublist \
are the exact health state names of the health states that should occupy that row. Used to order the health states \
in the diagram in a sensible, logical way, to make interpretation of the diagram easy
"""


