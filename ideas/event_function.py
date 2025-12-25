
def example_event(state, cycle, treatment, event_name, **kwargs):

    def event_rate(state, cycle, treatment, **kwargs):

        return None

    def QALY_impact(state, cycle, treatment, **kwargs):

        return None

    def cost_impact(state, cycle, treatment, **kwargs):

        return None

    def event_transitions(state, cycle, treatment, **kwargs):

        return None


    QALY_impact = QALY_impact(state=state, cycle=cycle, treatment=treatment, kwargs=kwargs)

    cost_impact = cost_impact(state=state, cycle=cycle, treatment=treatment, kwargs=kwargs)

    event_transitions = event_transitions(state=state, cycle=cycle, treatment=treatment, kwargs=kwargs)

    return {"QALY_impact": QALY_impact, "cost_impact": cost_impact, "event_transitions": event_transitions,
            "event_name": event_name}











