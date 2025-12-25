import React from "react";
import MetricCell from "./MetricCell";
import { formatCostGBP, formatNumber } from "./resultsFormatters";

function ICERCell({ value }) {
  if (value === null || value === undefined) return <span className="text-gray-400">—</span>;
  const n = Number(value);
  if (Number.isNaN(n)) return <span className="text-gray-400">—</span>;
  // £ per QALY
  return <span>{formatCostGBP(n, 0)}</span>;
}

export default function ResultsSummaryStrip({ summary }) {
  const { arms, icerRows } = summary;

  return (
    <div className="grid gap-3">
      <div className="overflow-x-auto">
        <table className="min-w-[700px] w-full text-sm">
          <thead>
            <tr className="text-left text-gray-600">
              <th className="py-2 pr-3">Treatment</th>
              <th className="py-2 pr-3 text-right">Total cost</th>
              <th className="py-2 pr-3 text-right">Total QALY</th>
              <th className="py-2 pr-3 text-right">Total time spent</th>
            </tr>
          </thead>
          <tbody>
            {arms.map((a) => (
              <tr key={a.treatment} className="border-t border-gray-100">
                <td className="py-2 pr-3 font-medium">{a.treatment}</td>
                <td className="py-2 pr-3 text-right"><MetricCell value={a.cost} kind="cost" mutedIfZero={false} /></td>
                <td className="py-2 pr-3 text-right"><MetricCell value={a.qaly} kind="qaly" mutedIfZero={false} /></td>
                <td className="py-2 pr-3 text-right"><MetricCell value={a.time_spent} kind="time_spent" mutedIfZero={false} /></td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      {icerRows?.length > 0 && (
        <div className="overflow-x-auto">
          <table className="min-w-[700px] w-full text-sm">
            <thead>
              <tr className="text-left text-gray-600">
                <th className="py-2 pr-3">Comparator</th>
                <th className="py-2 pr-3 text-right">Δ cost</th>
                <th className="py-2 pr-3 text-right">Δ QALY</th>
                <th className="py-2 pr-3 text-right">ICER</th>
              </tr>
            </thead>
            <tbody>
              {icerRows.map((r) => (
                <tr key={r.comparator} className="border-t border-gray-100">
                  <td className="py-2 pr-3 font-medium">{r.comparator}</td>
                  <td className="py-2 pr-3 text-right">{formatCostGBP(r.delta_cost, 2)}</td>
                  <td className="py-2 pr-3 text-right">{formatNumber(r.delta_qaly, 3)}</td>
                  <td className="py-2 pr-3 text-right"><ICERCell value={r.icer} /></td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </div>
  );
}
