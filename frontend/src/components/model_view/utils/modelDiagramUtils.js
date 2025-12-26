// src/components/model_view/utils/modelDiagramUtils.js

// ---- impact ordering (for tile sorting) ----
export const IMPACT_ORDER = {
  transition: 0,
  cost: 1,
  utility: 2,
  disutility: 3,
  other: 9,
};

export function impactRank(ev) {
  const t = ev?.metadata?.impact_type ?? "other";
  return IMPACT_ORDER[t] ?? IMPACT_ORDER.other;
}

// ---- event helpers ----
export function buildEventsByName(event_data) {
  return new Map((event_data ?? []).map((e) => [e.event_name, e]));
}

/**
 * Returns: { [stateName]: string[] } mapping state -> ordered event_name list
 * Only includes states present in ordered_state_names.
 * Filters out events with metadata.enabled === false.
 */
export function computeStateEventTiles({ ordered_state_names, event_data }) {
  const byState = {};
  for (const s of ordered_state_names ?? []) byState[s] = [];

  for (const ev of event_data ?? []) {
    const md = ev?.metadata ?? {};
    if (md.enabled === false) continue;

    for (const s of md.applies_to_states ?? []) {
      if (!byState[s]) continue; // only include states we are actually rendering
      byState[s].push(ev.event_name);
    }
  }

  const eventsByName = buildEventsByName(event_data);

  for (const s of Object.keys(byState)) {
    byState[s].sort((a, b) => {
      const ea = eventsByName.get(a);
      const eb = eventsByName.get(b);

      const ra = impactRank(ea);
      const rb = impactRank(eb);
      if (ra !== rb) return ra - rb;

      // stable tie-breakers
      const pa = ea?.path ?? "";
      const pb = eb?.path ?? "";
      if (pa !== pb) return pa.localeCompare(pb);

      return a.localeCompare(b);
    });
  }

  return byState;
}

// ---- transitions helpers ----
/**
 * transitionsDict shape:
 *   { [fromState: string]: string[] }  // list of to-states
 *
 * Returns edges:
 *   { from, to, key, isLoop }
 */
export function transitionsDictToEdges(transitionsDict) {
  const edges = [];
  for (const [from, tos] of Object.entries(transitionsDict ?? {})) {
    for (const to of tos ?? []) {
      edges.push({
        from,
        to,
        key: `${from}→${to}`,
        isLoop: from === to,
      });
    }
  }
  return edges;
}
