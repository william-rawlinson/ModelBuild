import React from "react";
import { formatMetric, isEffectivelyZero } from "./resultsFormatters";

export default function MetricCell({ value, kind, mutedIfZero = true }) {
  const zero = mutedIfZero && isEffectivelyZero(value);
  return (
    <span className={zero ? "text-gray-400" : ""}>
      {zero ? "—" : formatMetric(value, kind)}
    </span>
  );
}
