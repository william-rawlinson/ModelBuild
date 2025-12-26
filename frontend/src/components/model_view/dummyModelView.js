// src/components/model_view/dummyModelView.js

export const dummyModelView = {
  schema_version: 1,
  snapshot_id: null,
  display_name: "Working model",
  created_at: "2025-12-26T20:42:13.257519+00:00",
  parent_snapshot_id: null,
  notes: null,

  model_description:
    "Decision Problem\nDecision problem statement\nThe aim of the analysis is to investigate whether VBT (anterior vertebral body tethering) is cost-effective as a first-choice surgical treatment option for pediatric patients with moderate to severe idiopathic scoiliosis who have failed nonoperative management, from a US perspective. The analysis should compare VBT to spinal fusion from the perspective of the US integrated healthcare delivery system (IDS).\nTime horizon, cycle length, and discounting\n15-year time-horizon, 3-month cycle length. Annual discounting of costs and effects of 3%.\nTreatment strategies\nIntervention: VBT, comparator: spinal fusion.\nHealth states\nPatients enter the model in the spinal fusion or VBT index procedure health state. Devise health states based on the transitions described. \nTransition probabilities\nPatients enter the model in the index spinal fusion or VBT index procedure health state depending on treatment arm. From this state, patients transition to the postoperative health states. The postoperative VBT health state represents patients who have had an index VBT operation. In the postoperative VBT health state patients who received VBT can experience VBT revision or an index fusion procedure. Once a patient has experienced an index fusion procedure they move to the postoperative index fusion health state. From here, they may experience up to two total revisions (modelled by two further fusion revision health states, with specific post operative states following these). If a patient in the postoperative state for the second fusion revision requires a further revision, they move to the absorbing ineligible fusion state. \nCosts\nIndex procedure costs\nSee provided data. For first index procedures, should be upon entry to the model. \nRevision procedure costs\nSee provided data\n\n\n\nUtilities\nHealth state utilities\nSee provided data.",

  health_states: [
    "VBT_Index",
    "PostVBT__tunnel_0",
    "PostVBT__long_term",
    "VBT_Revision",
    "PostVBT_Revision__tunnel_0",
    "PostVBT_Revision__long_term",
    "Fusion_Index",
    "PostFusion_Index__tunnel_0",
    "PostFusion_Index__long_term",
    "Fusion_Revision1",
    "PostFusion_Revision1__tunnel_0",
    "PostFusion_Revision1__long_term",
    "Fusion_Revision2",
    "PostFusion_Revision2__tunnel_0",
    "PostFusion_Revision2__long_term",
    "Ineligible_Fusion",
    "Death",
  ],

  treatments: ["VBT", "Fusion"],

  cycle_length_years: 3,
  time_horizon_years: 15,
  disc_rate_cost_annual: 0.05,
  disc_rate_qaly_annual: 0.05,

  initial_occupancy: {
    VBT: {
      VBT_Index: 1.0,
      PostVBT__tunnel_0: 0.0,
      PostVBT__long_term: 0.0,
      VBT_Revision: 0.0,
      PostVBT_Revision__tunnel_0: 0.0,
      PostVBT_Revision__long_term: 0.0,
      Fusion_Index: 0.0,
      PostFusion_Index__tunnel_0: 0.0,
      PostFusion_Index__long_term: 0.0,
      Fusion_Revision1: 0.0,
      PostFusion_Revision1__tunnel_0: 0.0,
      PostFusion_Revision1__long_term: 0.0,
      Fusion_Revision2: 0.0,
      PostFusion_Revision2__tunnel_0: 0.0,
      PostFusion_Revision2__long_term: 0.0,
      Ineligible_Fusion: 0.0,
      Death: 0.0,
    },
    Fusion: {
      VBT_Index: 0.0,
      PostVBT__tunnel_0: 0.0,
      PostVBT__long_term: 0.0,
      VBT_Revision: 0.0,
      PostVBT_Revision__tunnel_0: 0.0,
      PostVBT_Revision__long_term: 0.0,
      Fusion_Index: 1.0,
      PostFusion_Index__tunnel_0: 0.0,
      PostFusion_Index__long_term: 0.0,
      Fusion_Revision1: 0.0,
      PostFusion_Revision1__tunnel_0: 0.0,
      PostFusion_Revision1__long_term: 0.0,
      Fusion_Revision2: 0.0,
      PostFusion_Revision2__tunnel_0: 0.0,
      PostFusion_Revision2__long_term: 0.0,
      Ineligible_Fusion: 0.0,
      Death: 0.0,
    },
  },

  parameters_rich: {
    vbt_revision_prob_2yr: {
      value: 0.0602,
      description: "2-year probability of VBT revision",
      distribution: null,
      standard_error: null,
    },
    fusion_revision_prob_first_quarter: {
      value: 0.0169,
      description:
        "Quarterly probability of spinal fusion revision (first quarter after prior spinal fusion or spinal fusion revision)",
      distribution: null,
      standard_error: null,
    },
    fusion_revision_prob_subsequent: {
      value: 0.0022,
      description:
        "Quarterly probability of spinal fusion revision (more than one quarter since prior spinal fusion or spinal fusion revision)",
      distribution: null,
      standard_error: null,
    },
    vbt_to_fusion_prob_first_quarter: {
      value: 0.0118,
      description:
        "Quarterly probability of index spinal fusion for VBT patients (first quarter after VBT index)",
      distribution: null,
      standard_error: null,
    },
    vbt_to_fusion_prob_subsequent: {
      value: 0.0019,
      description:
        "Quarterly probability of index spinal fusion for VBT patients (more than one quarter after VBT index)",
      distribution: null,
      standard_error: null,
    },
    preop_utility: {
      value: 0.783,
      description: "Preoperative VBT and spinal fusion utility",
      distribution: null,
      standard_error: null,
    },
    postop_vbt_utility: {
      value: 0.925,
      description: "Postoperative VBT utility",
      distribution: null,
      standard_error: null,
    },
    postop_fusion_utility: {
      value: 0.875,
      description: "Postoperative spinal fusion utility",
      distribution: null,
      standard_error: null,
    },
    non_device_procedure_cost: {
      value: 28616.0,
      description: "Non-device cost all procedures (index and revision)",
      distribution: null,
      standard_error: null,
    },
    fusion_device_cost: {
      value: 17200.0,
      description: "Fusion device cost",
      distribution: null,
      standard_error: null,
    },
    vbt_index_device_cost: {
      value: 50615.0,
      description: "Index VBT device cost",
      distribution: null,
      standard_error: null,
    },
    vbt_revision_device_cost: {
      value: 8804.0,
      description: "VBT revision device cost",
      distribution: null,
      standard_error: null,
    },
    background_mortality_rate_quarterly: {
      value: 0.0001,
      description:
        "Quarterly background mortality rate for pediatric scoliosis patients",
      distribution: "beta",
      standard_error: 5e-05,
    },
    vbt_revision_prob_quarterly: {
      value: 0.0077,
      description: "Quarterly probability of VBT revision",
      distribution: "beta",
      standard_error: 0.0015,
    },
    apply_index_costs_in_cycle: {
      value: 0,
      description:
        "The cycle in which to apply index procedure costs (typically cycle 0)",
      distribution: null,
      standard_error: null,
    },
    fusion_revision_device_cost: {
      value: 17200.0,
      description:
        "Fusion revision device cost (assumed same as index fusion device cost)",
      distribution: null,
      standard_error: null,
    },
    procedure_utility: {
      value: 0.5,
      description:
        "Utility during procedure states (VBT_Revision, Fusion_Revision1, Fusion_Revision2)",
      distribution: "beta",
      standard_error: 0.05,
    },
    ineligible_fusion_utility: {
      value: 0.7,
      description: "Utility for patients in the ineligible fusion state",
      distribution: "beta",
      standard_error: 0.05,
    },
  },

  // NOTE: The frontend ModelDiagram currently expects:
  // - transition_matrix_data at the top level, with .metadata.transitions/.metadata.state_diagram
  // - event_data at the top level
  // This dummy payload includes both:
  transition_matrix_data: {
    path: "code/transition_matrix.py",
    code: `# transition_matrix.py (dummy)
import numpy as np
def build_transition_matrix(ctx):
    states = ctx["health_states"]
    n = len(states)
    P = np.zeros((n, n))
    for i in range(n):
        P[i, i] = 1.0
    return P
`,
    metadata: {
      description:
        "This transition matrix models the progression of pediatric scoliosis patients through treatment pathways for VBT and spinal fusion. Patients enter the model in either VBT_Index or Fusion_Index states based on treatment arm. From VBT_Index, patients move to a post-operative tunnel state (first quarter) and then to a long-term state, with possibilities of VBT revision or conversion to fusion. Patients who undergo fusion (either initially or after VBT) can experience up to two fusion revisions before becoming ineligible for further revisions. Each state has a small probability of transitioning to Death. Tunnel states (representing the first quarter after procedures) have higher revision probabilities than long-term states.",
      assumptions: [
        "Background mortality is constant across all health states and age groups",
        "VBT revision probability is constant over time (converted from 2-year to quarterly probability)",
        "Patients can have at most two fusion revisions before becoming ineligible",
        "Transition probabilities are independent of patient characteristics",
        "Patients who have had VBT revision cannot have another VBT revision (they can only transition to fusion)",
        "All procedure states (Index and Revision) are temporary one-cycle states",
      ],
      transitions: {
        VBT_Index: ["PostVBT__tunnel_0", "Death"],
        PostVBT__tunnel_0: [
          "VBT_Revision",
          "Fusion_Index",
          "PostVBT__long_term",
          "Death",
        ],
        PostVBT__long_term: [
          "VBT_Revision",
          "Fusion_Index",
          "PostVBT__long_term",
          "Death",
        ],
        VBT_Revision: ["PostVBT_Revision__tunnel_0", "Death"],
        PostVBT_Revision__tunnel_0: [
          "Fusion_Index",
          "PostVBT_Revision__long_term",
          "Death",
        ],
        PostVBT_Revision__long_term: [
          "Fusion_Index",
          "PostVBT_Revision__long_term",
          "Death",
        ],
        Fusion_Index: ["PostFusion_Index__tunnel_0", "Death"],
        PostFusion_Index__tunnel_0: [
          "Fusion_Revision1",
          "PostFusion_Index__long_term",
          "Death",
        ],
        PostFusion_Index__long_term: [
          "Fusion_Revision1",
          "PostFusion_Index__long_term",
          "Death",
        ],
        Fusion_Revision1: ["PostFusion_Revision1__tunnel_0", "Death"],
        PostFusion_Revision1__tunnel_0: [
          "Fusion_Revision2",
          "PostFusion_Revision1__long_term",
          "Death",
        ],
        PostFusion_Revision1__long_term: [
          "Fusion_Revision2",
          "PostFusion_Revision1__long_term",
          "Death",
        ],
        Fusion_Revision2: ["PostFusion_Revision2__tunnel_0", "Death"],
        PostFusion_Revision2__tunnel_0: [
          "Ineligible_Fusion",
          "PostFusion_Revision2__long_term",
          "Death",
        ],
        PostFusion_Revision2__long_term: [
          "Ineligible_Fusion",
          "PostFusion_Revision2__long_term",
          "Death",
        ],
        Ineligible_Fusion: ["Ineligible_Fusion", "Death"],
        Death: ["Death"],
      },
      state_diagram: [
        ["VBT_Index", "Fusion_Index", "PostVBT__tunnel_0", "PostFusion_Index__tunnel_0"],
        ["PostVBT__long_term", "PostFusion_Index__long_term"],
        ["VBT_Revision", "Fusion_Revision1"],
        ["PostVBT_Revision__tunnel_0", "PostFusion_Revision1__tunnel_0"],
        ["PostVBT_Revision__long_term", "PostFusion_Revision1__long_term"],
        ["Fusion_Revision2"],
        ["PostFusion_Revision2__tunnel_0"],
        ["PostFusion_Revision2__long_term"],
        ["Ineligible_Fusion"],
        ["Death"],
      ],
    },
  },

  event_data: [
    {
      event_name: "Index Procedure Costs",
      path: "code/events/001_index_procedure_costs.py",
      code: `def get_impact(ctx):
    # dummy placeholder
    return {"cost": 0.0, "qaly": 0.0}
`,
      metadata: {
        description:
          "Applies the initial procedure costs when patients enter the model in either the VBT Index Procedure or Fusion Index Procedure health states. For VBT, this includes the VBT device cost ($50,615) plus non-device procedure costs ($28,616). For fusion, this includes the fusion device cost ($17,200) plus non-device procedure costs ($28,616). These costs are applied only once at the beginning of the model (cycle 0).",
        assumptions:
          ["Index procedure costs are applied as occupancy costs in cycle 0 only. The costs are applied to patients in the respective index procedure states, regardless of subsequent transitions."],
        applies_to_treatments: ["VBT", "Fusion"],
        applies_to_states: ["VBT_Index", "Fusion_Index"],
        impact_type: "cost",
        enabled: true,
      },
    },
    {
      event_name: "VBT Revision Procedure Costs",
      path: "code/events/002_vbt_revision_procedure_costs.py",
      code: `def get_impact(ctx):
    # dummy placeholder
    return {"cost": 0.0, "qaly": 0.0}
`,
      metadata: {
        description:
          "Applies costs when patients undergo a VBT revision procedure after initial VBT surgery. The total cost of $37,420 includes the VBT revision device cost ($8,804) plus non-device procedure costs ($28,616). These costs are applied whenever a patient transitions from a postoperative VBT state to the VBT revision state.",
        assumptions:
          ["The same non-device procedure cost applies to revision procedures as to index procedures. Costs are applied as flow impacts to capture the one-time cost of the revision procedure at the time it occurs."],
        applies_to_treatments: ["VBT"],
        applies_to_states: ["PostVBT__tunnel_0", "PostVBT__long_term", "VBT_Revision"],
        impact_type: "cost",
        enabled: true,
      },
    },
    {
      event_name: "Fusion Index Procedure Costs (after VBT)",
      path: "code/events/003_fusion_index_procedure_costs_after_vbt.py",
      code: `def get_impact(ctx):
    # dummy placeholder
    return {"cost": 0.0, "qaly": 0.0}
`,
      metadata: {
        description:
          "Applies costs when patients who initially received VBT treatment later require a spinal fusion procedure. The total cost of $45,816 includes the fusion device cost ($17,200) plus non-device procedure costs ($28,616). These costs are applied whenever a patient transitions from any postoperative VBT state to the Fusion Index Procedure state.",
        assumptions:
          ["The same fusion device and non-device procedure costs apply regardless of whether the fusion is an initial procedure or follows a VBT procedure. Costs are applied as flow impacts to capture the one-time cost of the fusion procedure at the time it occurs."],
        applies_to_treatments: ["VBT"],
        applies_to_states: [
          "PostVBT__tunnel_0",
          "PostVBT__long_term",
          "PostVBT_Revision__tunnel_0",
          "PostVBT_Revision__long_term",
          "Fusion_Index",
        ],
        impact_type: "cost",
        enabled: true,
      },
    },
    {
      event_name: "First Fusion Revision Procedure Costs",
      path: "code/events/004_first_fusion_revision_procedure_costs.py",
      code: `def get_impact(ctx):
    # dummy placeholder
    return {"cost": 0.0, "qaly": 0.0}
`,
      metadata: {
        description:
          "Applies costs when patients who have undergone a spinal fusion procedure require a first revision of that fusion. The total cost of $45,816 includes the fusion revision device cost ($17,200) plus non-device procedure costs ($28,616). These costs are applied whenever a patient transitions from a postoperative fusion index state to the first fusion revision state.",
        assumptions:
          ["The fusion revision device cost is assumed to be the same as the index fusion device cost. Costs are applied as flow impacts to capture the one-time cost of the revision procedure at the time it occurs."],
        applies_to_treatments: ["VBT", "Fusion"],
        applies_to_states: [
          "PostFusion_Index__tunnel_0",
          "PostFusion_Index__long_term",
          "Fusion_Revision1",
        ],
        impact_type: "cost",
        enabled: true,
      },
    },
    {
      event_name: "Second Fusion Revision Procedure Costs",
      path: "code/events/005_second_fusion_revision_procedure_costs.py",
      code: `def get_impact(ctx):
    # dummy placeholder
    return {"cost": 0.0, "qaly": 0.0}
`,
      metadata: {
        description:
          "Applies costs when patients who have already undergone one fusion revision procedure require a second revision of their fusion. The total cost of $45,816 includes the fusion revision device cost ($17,200) plus non-device procedure costs ($28,616). These costs are applied whenever a patient transitions from a postoperative first fusion revision state to the second fusion revision state.",
        assumptions:
          ["The fusion revision device cost for the second fusion revision is assumed to be the same as for the first fusion revision. Costs are applied as flow impacts to capture the one-time cost of the revision procedure at the time it occurs."],
        applies_to_treatments: ["VBT", "Fusion"],
        applies_to_states: [
          "PostFusion_Revision1__tunnel_0",
          "PostFusion_Revision1__long_term",
          "Fusion_Revision2",
        ],
        impact_type: "cost",
        enabled: true,
      },
    },
    {
      event_name: "Health State Utilities",
      path: "code/events/006_health_state_utilities.py",
      code: `def get_impact(ctx):
    # dummy placeholder
    return {"cost": 0.0, "qaly": 0.0}
`,
      metadata: {
        description:
          "Applies health-related quality of life utility values for each health state a patient occupies during a cycle. Uses preoperative utility (0.783) for index procedure states, postoperative VBT utility (0.925) for all postoperative VBT states, postoperative fusion utility (0.875) for all postoperative fusion states, procedure utility (0.5) during revision procedures, and ineligible fusion utility (0.7) for the ineligible fusion state. Death has a utility of 0. All utilities are multiplied by the cycle length to convert to QALYs.",
        assumptions:
          ["Patients in procedure states have lower utility (0.5) to reflect discomfort and recovery from surgery. Patients in the ineligible fusion state have lower utility (0.7) than standard postoperative fusion patients to reflect complications that led to ineligibility for further revisions. The same utility values apply regardless of treatment arm or cycle."],
        applies_to_treatments: ["VBT", "Fusion"],
        applies_to_states: [
          "VBT_Index",
          "PostVBT__tunnel_0",
          "PostVBT__long_term",
          "VBT_Revision",
          "PostVBT_Revision__tunnel_0",
          "PostVBT_Revision__long_term",
          "Fusion_Index",
          "PostFusion_Index__tunnel_0",
          "PostFusion_Index__long_term",
          "Fusion_Revision1",
          "PostFusion_Revision1__tunnel_0",
          "PostFusion_Revision1__long_term",
          "Fusion_Revision2",
          "PostFusion_Revision2__tunnel_0",
          "PostFusion_Revision2__long_term",
          "Ineligible_Fusion",
          "Death",
        ],
        impact_type: "qaly",
        enabled: true,
      },
    },
    {
      event_name: "Procedure Disutility",
      path: "code/events/007_procedure_disutility.py",
      code: `def get_impact(ctx):
    # dummy placeholder
    return {"cost": 0.0, "qaly": 0.0}
`,
      metadata: {
        description:
          "This is a placeholder event that represents the temporary reduction in quality of life associated with surgery and immediate recovery. However, it applies no additional impacts because the procedure disutility is already captured in the Health State Utilities event through the procedure_utility parameter (0.5).",
        assumptions:
          ["The temporary disutility during procedures is fully captured by the procedure_utility parameter in the Health State Utilities event. Implementing additional disutilities here would result in double counting."],
        applies_to_treatments: [],
        applies_to_states: [],
        impact_type: "qaly",
        enabled: true,
      },
    },
    {
      event_name: "Background Mortality",
      path: "code/events/008_background_mortality.py",
      code: `def get_impact(ctx):
    # dummy placeholder
    return {"cost": 0.0, "qaly": 0.0}
`,
      metadata: {
        description:
          "Applies the background mortality rate (0.0001 per quarter) across all health states, representing the probability of death from causes unrelated to scoliosis or its treatment. This event sets up the flow impacts for transitions to the Death state, though it doesn't apply any direct cost or QALY impacts.",
        assumptions:
          ["Background mortality is constant across all health states (no increased mortality risk in any particular state). Background mortality is constant over time (no age-dependent increase in mortality). Background mortality is the same for both treatment arms."],
        applies_to_treatments: ["VBT", "Fusion"],
        applies_to_states: [
          "VBT_Index",
          "PostVBT__tunnel_0",
          "PostVBT__long_term",
          "VBT_Revision",
          "PostVBT_Revision__tunnel_0",
          "PostVBT_Revision__long_term",
          "Fusion_Index",
          "PostFusion_Index__tunnel_0",
          "PostFusion_Index__long_term",
          "Fusion_Revision1",
          "PostFusion_Revision1__tunnel_0",
          "PostFusion_Revision1__long_term",
          "Fusion_Revision2",
          "PostFusion_Revision2__tunnel_0",
          "PostFusion_Revision2__long_term",
          "Ineligible_Fusion",
        ],
        impact_type: "both",
        enabled: true,
      },
    },
  ],
};
