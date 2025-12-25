export const dummyModelView = {
  meta: {
    model_id: "dummy-model-001",
    name: "Example oncology Markov model",
    cycle_length: { value: 1, unit: "months" },
    time_horizon: { value: 20, unit: "years" },
    treatments: ["treatment_a", "treatment_b"],
  },

  // 1) Health states (boxes)
  states: [
    { id: "pfs", label: "PFS", layout: { x: 80, y: 120 } },
    { id: "pps", label: "PPS", layout: { x: 420, y: 120 } },
    { id: "dead", label: "Death", layout: { x: 740, y: 120 } },
  ],

  // 2) Directed edges between states (arrows)
  transitions: [
    { id: "pfs_to_pps", from: "pfs", to: "pps", event_id: "evt_pfs_to_pps" },
    { id: "pfs_to_dead", from: "pfs", to: "dead", event_id: "evt_pfs_to_dead" },
    { id: "pps_to_dead", from: "pps", to: "dead", event_id: "evt_pps_to_dead" },
  ],

  // 3) Events are defined once (click panel uses this)
  events: [
    {
      id: "evt_tx_costs",
      label: "Treatment costs",
      type: "cost",
      applies_to: { treatments: ["treatment_a", "treatment_b"], states: ["pfs", "pps"] },
      qc_status: "needs_qc", // later filter
      spec_used: true,
      assumptions: ["Costs applied per cycle while on treatment"],
      code_ref: "drug_cost_simple_v1",
      details: {
        currency: "GBP",
        discount_rate: 0.035,
      },
    },
    {
      id: "evt_state_utility_pfs",
      label: "Health state utility",
      type: "utility",
      applies_to: { states: ["pfs"], treatments: "all" },
      qc_status: "ok",
      spec_used: false,
      assumptions: ["Used baseline utility from published trial"],
      code_ref: "state_utility_v1",
    },

    // transition events (these can also be rendered as tiles inside the state)
    {
      id: "evt_pfs_to_pps",
      label: "PFS → PPS transition",
      type: "transition",
      transition: { from: "pfs", to: "pps" },
      qc_status: "ok",
      spec_used: true,
      assumptions: ["RR applied to baseline hazard"],
      code_ref: "transition_rr_v1",
    },
    {
      id: "evt_pfs_to_dead",
      label: "PFS → Death transition",
      type: "transition",
      transition: { from: "pfs", to: "dead" },
      qc_status: "needs_qc",
      spec_used: true,
      assumptions: ["Background mortality + excess mortality"],
      code_ref: "transition_mortality_v2",
    },
    {
      id: "evt_pps_to_dead",
      label: "PPS → Death transition",
      type: "transition",
      transition: { from: "pps", to: "dead" },
      qc_status: "ok",
      spec_used: true,
      assumptions: ["Higher mortality in PPS"],
      code_ref: "transition_mortality_v2",
    },
  ],

  // 4) Which event tiles appear inside which state box
  // (By id, so you can reorder/ filter without duplicating event objects.)
  state_event_tiles: {
    pfs: [
      "evt_tx_costs",
      "evt_pfs_to_pps",
      "evt_pfs_to_dead",
      "evt_state_utility_pfs",
    ],
    pps: ["evt_tx_costs", "evt_pps_to_dead"],
    dead: [], // often no events; could include terminal cost, etc.
  },
};
