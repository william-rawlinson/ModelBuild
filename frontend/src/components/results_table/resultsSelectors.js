import { isEffectivelyZero } from "./resultsFormatters";

function getTreatments(results) {
  if (Array.isArray(results?.treatments) && results.treatments.length) return results.treatments;
  const keys = results?.per_treatment ? Object.keys(results.per_treatment) : [];
  return keys;
}

function getIntervention(results, treatments, discounting = "discounted") {
  return results?.icer?.[discounting]?.reference_treatment || treatments[0];
}

function getICER(results, comparator, discounting = "discounted") {
  const comps = results?.icer?.[discounting]?.comparisons || [];
  return comps.find((c) => c.comparator === comparator) || null;
}


function getTotals(results, treatment, discounting) {
  return results?.per_treatment?.[treatment]?.outcomes?.[discounting]?.totals || null;
}

function getTimeSpentTotals(results, treatment, discounting) {
  return results?.per_treatment?.[treatment]?.occupancy?.[discounting]?.totals || null;
}



function defaultSettings(results) {
  const treatments = getTreatments(results);
  const intervention = getIntervention(results, treatments);
  const comparators = treatments.filter((t) => t !== intervention);

    return {
      discounting: "discounted",
      measure: "cost_qaly",
      breakdown: "by_event",
      comparators,
      showDeltas: true,
    };
}

function buildColumns({ intervention, comparators, showDeltas, measure }) {
  const columns = [{ key: "label", label: "Item", align: "left", kind: "text" }];

  const arms = [intervention, ...comparators];

  const pushMetricCols = (baseKey, groupLabel) => {
    if (measure === "cost_qaly") {
      columns.push({
        key: `${baseKey}cost`,
        align: "right",
        kind: "cost",
        groupLabel,
        subLabel: "Cost",
      });
      columns.push({
        key: `${baseKey}qaly`,
        align: "right",
        kind: "qaly",
        groupLabel,
        subLabel: "QALY",
      });
    } else {
      // single-metric mode
      const sub =
        measure === "cost" ? "Cost" :
        measure === "qaly" ? "QALY" :
        measure === "time_spent" ? "Time" :
        measure;

      columns.push({
        key: `${baseKey}${measure}`,
        align: "right",
        kind: measure,
        groupLabel,
        subLabel: sub,
      });
    }
  };

  // Arm groups
  for (const arm of arms) {
    pushMetricCols(`arm:${arm}:`, arm);
  }

  // Delta groups
  if (showDeltas && comparators.length) {
      for (const c of comparators) {
        pushMetricCols(`delta:${c}:`, `Δ ${c}`);
      }
    }

  return columns;
}



function buildSummary(results, { intervention, comparators, discounting }) {
  const refTotals = getTotals(results, intervention, discounting);
  const refTS = getTimeSpentTotals(results, intervention, discounting);

  const arms = [intervention, ...comparators].map((t) => {
    const tot = getTotals(results, t, discounting);
    const ts = getTimeSpentTotals(results, t, discounting);

    return {
      treatment: t,
      cost: tot?.cost_total ?? null,
      qaly: tot?.qaly_total ?? null,
      time_spent: ts?.time_spent_total ?? null,
    };
  });

  const icerRows = comparators.map((c) => {
    const row = getICER(results, c, discounting);
    return {
      comparator: c,
      delta_cost: row?.delta_cost ?? null,
      delta_qaly: row?.delta_qaly ?? null,
      icer: row?.icer ?? null,
    };
  });

  return { arms, icerRows, refTotals, refTS };
}


function buildRows(results, settings, { intervention, comparators }) {
  const { discounting, measure, breakdown } = settings;

  const refTotals = getTotals(results, intervention, discounting);
  const refTS = getTimeSpentTotals(results, intervention, discounting);

  // Helpers to fetch values for a row in a given arm
  function valueFor(treatment, row, metric) {
    const tot = getTotals(results, treatment, discounting);
    const ts = getTimeSpentTotals(results, treatment, discounting);

    if (breakdown === "by_state") {
      const state = row.state;
      if (metric === "cost") return tot?.cost_by_state?.[state] ?? 0;
      if (metric === "qaly") return tot?.qaly_by_state?.[state] ?? 0;
      if (metric === "time_spent") return ts?.time_spent_by_state?.[state] ?? 0;
    }

    if (breakdown === "by_event") {
      const event = row.event;
      if (metric === "cost") return tot?.cost_by_event?.[event] ?? 0;
      if (metric === "qaly") return tot?.qaly_by_event?.[event] ?? 0;
      return 0; // no event breakdown for time_spent
    }

    if (breakdown === "by_state_event") {
      const { state, event } = row;
      if (metric === "cost") return tot?.cost_by_state_event?.[state]?.[event] ?? 0;
      if (metric === "qaly") return tot?.qaly_by_state_event?.[state]?.[event] ?? 0;
      return 0;
    }

    return 0;
  }

  // Define row universe from reference arm (stable)
  let rowDefs = [];

  if (breakdown === "by_state") {
    const states = Object.keys(
      refTotals?.cost_by_state || refTotals?.qaly_by_state || refTS?.time_spent_by_state || {}
    );
    rowDefs = states.map((s) => ({ id: `state:${s}`, label: s, state: s }));
  } else if (breakdown === "by_event") {
    if (measure === "time_spent") {
      const states = Object.keys(refTS?.time_spent_by_state || {});
      rowDefs = states.map((s) => ({ id: `state:${s}`, label: s, state: s }));
    } else {
      // union across cost+qaly if combined
      const costEvents = Object.keys(refTotals?.cost_by_event || {});
      const qalyEvents = Object.keys(refTotals?.qaly_by_event || {});
      const events = Array.from(new Set([...costEvents, ...qalyEvents]));
      rowDefs = events.map((e) => ({ id: `event:${e}`, label: e, event: e }));
    }
  } else if (breakdown === "by_state_event") {
    if (measure === "time_spent") {
      const states = Object.keys(refTS?.time_spent_by_state || {});
      rowDefs = states.map((s) => ({ id: `state:${s}`, label: s, state: s }));
    } else {
      // union across cost+qaly maps if combined
      const costMap = refTotals?.cost_by_state_event || {};
      const qalyMap = refTotals?.qaly_by_state_event || {};

      const states = Array.from(new Set([...Object.keys(costMap), ...Object.keys(qalyMap)]));
      const pairs = [];
      for (const state of states) {
        const evs = new Set([
          ...Object.keys(costMap?.[state] || {}),
          ...Object.keys(qalyMap?.[state] || {}),
        ]);
        for (const event of evs) pairs.push({ state, event });
      }

      rowDefs = pairs.map(({ state, event }) => ({
        id: `se:${state}|${event}`,
        label: `${state} · ${event}`,
        state,
        event,
      }));
    }
  }

  const rows = rowDefs.map((row) => {
    const values = {};

    const metrics = measure === "cost_qaly" ? ["cost", "qaly"] : [measure];

    // intervention
    for (const m of metrics) values[`arm:${intervention}:${m}`] = valueFor(intervention, row, m);

    // comparators + deltas
    for (const c of comparators) {
      for (const m of metrics) {
        const v = valueFor(c, row, m);
        const ref = values[`arm:${intervention}:${m}`];
        values[`arm:${c}:${m}`] = v;
        values[`delta:${c}:${m}`] = v - ref;
      }
    }

    return { ...row, values };
  });

  return rows;
}


function applySort(rows, settings, intervention) {
  const { comparators, showDeltas, measure } = settings;
  const metrics = measure === "cost_qaly" ? ["cost", "qaly"] : [measure];

  // Default behaviour:
  // - if deltas on: sort by largest absolute delta across selected comparators (and across metrics if cost_qaly)
  // - else: sort A→Z
  if (showDeltas && comparators.length) {
    return [...rows].sort((a, b) => {
      const aMax = Math.max(
        ...comparators.flatMap((c) => metrics.map((m) => Math.abs(a.values?.[`delta:${c}:${m}`] || 0)))
      );
      const bMax = Math.max(
        ...comparators.flatMap((c) => metrics.map((m) => Math.abs(b.values?.[`delta:${c}:${m}`] || 0)))
      );
      return bMax - aMax;
    });
  }

  return [...rows].sort((a, b) => (a.label || "").localeCompare(b.label || ""));
}


export function buildResultsViewModel(results, settingsOverride = null) {
  const treatments = getTreatments(results);
  const intervention = getIntervention(results, treatments);

  const defaults = defaultSettings(results);
  const settings = { ...defaults, ...(settingsOverride || {}) };

  // Ensure comparators exist and exclude intervention
  settings.comparators = (settings.comparators || [])
    .filter((t) => t !== intervention)
    .filter((t) => treatments.includes(t));

  const columns = buildColumns({
    intervention,
    comparators: settings.comparators,
    showDeltas: settings.showDeltas,
    measure: settings.measure,
  });

  const summary = buildSummary(results, {
    intervention,
    comparators: settings.comparators,
    discounting: settings.discounting,
  });

  let rows = buildRows(results, settings, { intervention, comparators: settings.comparators });
  rows = applySort(rows, settings, intervention);

  return {
    treatments,
    intervention,
    settings,
    options: {
      comparators: treatments.filter((t) => t !== intervention),
    },
    columns,
    rows,
    summary,
  };
}

