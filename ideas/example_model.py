
# PFS, PPS, Death

# health state utility and treatment costs
# treatment costs are one-off in first cycle
# two treatments, treatment A and treatment B

# START MODEL

# ARGUMENTS

def model():

    parameters = {
        "treatment_a_cost": 100,
        "treatment_b_cost": 200,
        "progression_prob_per_cycle_untreated": 0.3,
        "death_prob_pfs": 0.1,
        "death_prob_pps": 0.2,
        "treatment_a_progression_rr": 0.75,
        "treatment_b_progression_rr": 0.80,
        "pfs_utility": 0.7,
        "pps_utility": 0.65,
        "initial_occupancy": {"PFS":1, "PPS":0, "Death":0},
        "cycle_length": 1,          # year
        "time_horizon": 30,         # years
        "discount_rate_cost": 0.05, # 5%
        "discount_rate_QALY": 0.05, # 5%
        "health_states": ["PFS", "PPS", "Death"],
        "treatments": ["treatment_a", "treatment_b"],
    }


    # DEFINE EVENTS

    def get_baseline_utility_event(state, cycle, treatment, parameters):

        event_rate = 1 # constant event - for simple cases don't have to define function

        # don't include cost impact, event transitions, QALY impact when not needed

        def unit_QALY_fn(state, cycle, treatment, parameters):

            if state == "PFS":
                return parameters["pfs_utility"] * parameters["cycle_length"] * event_rate

            if state == "PPS":
                return parameters["pps_utility"] * parameters["cycle_length"] * event_rate

        return {"QALY_impact": unit_QALY_fn(state=state, cycle=cycle, treatment=treatment, parameters=parameters),
                "cost_impact": 0,
                "event_transitions": None,
                "event_name": "Health state utility"}

    def get_treatment_cost_event(state, cycle, treatment, parameters):

        def rate_fn(state, cycle, treatment, parameters):

            if cycle == 0: # cost only applied in first cycle

                return 1

            else:

                return 0

        def unit_cost_fn(state, cycle, treatment, parameters):

            if treatment == "treatment_a":

                return parameters["treatment_a_cost"] * rate_fn(state=state, cycle=cycle, treatment=treatment,
                                                                parameters=parameters)

            if treatment == "treatment_b":

                return parameters["treatment_b_cost"] * rate_fn(state=state, cycle=cycle, treatment=treatment,
                                                                parameters=parameters)

        return {"QALY_impact": 0,
                "cost_impact": unit_cost_fn(state=state, cycle=cycle, treatment=treatment, parameters=parameters),
                "event_transitions": None,
                "event_name": "Treatment cost"}


    def get_transition_pfs_event(state, cycle, treatment, parameters): # todo get rid of some bloat by unpacking automatically

        def rate_fn(state, cycle, treatment, parameters):

            if state == "PFS":

                if treatment == "treatment_a":
                    progression_rr = parameters["treatment_a_progression_rr"]

                if treatment == "treatment_b":
                    progression_rr = parameters["treatment_b_progression_rr"]

                progression_probability = parameters["progression_prob_per_cycle_untreated"] * progression_rr
                death_probability = parameters["death_prob_pfs"]

                return 1 - (progression_probability + death_probability)

            else:

                return 0

        return {"QALY_impact": 0,
                "cost_impact": 0,
                "event_transitions": {"destination_state": "PFS", "origin_state": state,
                                      "rate": rate_fn(state=state, cycle=cycle, treatment=treatment,
                                                      parameters=parameters)},
                "event_name": "PFS transition"}


    def get_transition_pps_event(state, cycle, treatment, parameters): # todo get rid of some bloat by unpacking automatically

        def rate_fn(state, cycle, treatment, parameters):

            if state == "PFS":

                if treatment == "treatment_a":
                    progression_rr = parameters["treatment_a_progression_rr"]

                if treatment == "treatment_b":
                    progression_rr = parameters["treatment_b_progression_rr"]

                return parameters["progression_prob_per_cycle_untreated"] * progression_rr

            elif state == "PPS":

                death_probability = parameters["death_prob_pps"]

                return 1 - death_probability # stay in state

            else:

                return 0

        return {"QALY_impact": 0,
                "cost_impact": 0,
                "event_transitions": {"destination_state": "PPS", "origin_state": state,
                                      "rate": rate_fn(state=state, cycle=cycle, treatment=treatment,
                                                      parameters=parameters)},
                "event_name": "PPS transition"}


    def get_death_event(state, cycle, treatment, parameters):

        def rate_fn(state, cycle, treatment, parameters):

            if state == "PFS":

                return parameters["death_prob_pfs"]

            elif state == "PPS":

                return parameters["death_prob_pps"]

            if state == "Death":

                return 1

        return {"QALY_impact": 0,
                "cost_impact": 0,
                "event_transitions": {"destination_state": "Death", "origin_state": state,
                                      "rate": rate_fn(state=state, cycle=cycle, treatment=treatment,
                                                      parameters=parameters)},
                "event_name": "Death transition"}

    events = [get_baseline_utility_event, get_treatment_cost_event, get_transition_pfs_event, get_transition_pps_event, get_death_event]

    # MODEL SCRIPT

    initial_occupancy = parameters["initial_occupancy"]
    health_states = parameters["health_states"]
    treatments = parameters["treatments"]
    n_cycles = int(parameters["time_horizon"] / parameters["cycle_length"])

    # Each state each cycle each treatment, are subject to events
    # Each event has and/or cost impact, QALY impact, transition
    # multiply each by the state occupancy to get the absolute cost impact, absolute QALY impact, and absolute number of transitions
    # At start of model we have a state occupancy, we need to recalculate the state occupancies after each cycle.
    # Can we do this by collecting absolute transitions? Or just adding the absolute transitions into the states as we go?
    # adding as we go works

    from collections import defaultdict

    totals = defaultdict(
        lambda: defaultdict(
            lambda: defaultdict(dict)
        )
    )

    state_occupancies = defaultdict(
        lambda: defaultdict(
            lambda: defaultdict(dict)
        )
    )

    for cycle in n_cycles:
        for state in health_states:
            for treatment in treatments:
                for event in events:
                    event_name = event["name"]
                    totals[cycle][state][treatment]
                    state_occupancies[cycle][state][treatment]






















    totals = {"treatment_a": {}, "treatment_b": {}}
    state_occupancies = {"treatment_a":{}, "treatment_b":{}}

    for treatment in treatments:

        for cycle in range(n_cycles):

            state_occupancies[treatment][cycle] = {}
            totals[treatment][cycle] = {}

            for state in health_states:

                totals[treatment][cycle][state] = {}

                for event in events:

                    event_impact = event(state=state, cycle=cycle, treatment=treatment,
                                                        parameters=parameters)

                    totals[treatment][cycle][state][event_impact["event_name"]] = {}
                    totals[treatment][cycle][state][event_impact["event_name"]]["QALYs"] = event_impact["QALY_impact"]
                    totals[treatment][cycle][state][event_impact["event_name"]]["costs"] = event_impact["cost_impact"]

                    if cycle == 0: # todo reapplying not right

                        state_occupancies[treatment][cycle][state] = initial_occupancy[state]

                    elif event_impact["event_transitions"] is not None:

                        destination = event_impact["event_transitions"]["destination_state"]
                        origin = event_impact["event_transitions"]["origin_state"]
                        rate = event_impact["event_transitions"]["rate"]

                        prev_value = state_occupancies[treatment][cycle - 1][origin] * rate

                        if destination not in state_occupancies[treatment][cycle]:
                            state_occupancies[treatment][cycle][destination] = 0.0

                        state_occupancies[treatment][cycle][destination] += prev_value

    return state_occupancies, totals


if __name__ == "__main__":

    state_occupancies, totals = model()

    pass








