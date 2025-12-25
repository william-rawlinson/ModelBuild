import React from "react";
import MetricCell from "./MetricCell";

export default function ResultsPivotTable({ columns, rows, measure }) {
  return (
    <div className="overflow-x-auto border border-gray-200 rounded-2xl">
      <table className="min-w-[900px] w-full text-sm">
        <thead className="bg-gray-50 sticky top-0">
          {/* Header row 1: groups */}
          <tr className="text-left text-gray-600">
            {/* Pinned label column */}
            <th
              rowSpan={2}
              className="py-3 px-3 border-b border-gray-200 sticky left-0 bg-gray-50 z-10"
            >
              Item
            </th>

            {/* Group headers */}
            {(() => {
              // columns excluding label
              const cols = columns.filter((c) => c.key !== "label");

              // group contiguous columns by groupLabel (keeps order)
              const groups = [];
              for (const c of cols) {
                const g = c.groupLabel || "";
                const last = groups[groups.length - 1];
                if (last && last.groupLabel === g) last.columns.push(c);
                else groups.push({ groupLabel: g, columns: [c] });
              }

              return groups.map((g) => (
                <th
                  key={g.groupLabel}
                  colSpan={g.columns.length}
                  className="py-3 px-3 border-b border-gray-200 text-center"
                >
                  {g.groupLabel}
                </th>
              ));
            })()}
          </tr>

          {/* Header row 2: sub labels */}
          <tr className="text-left text-gray-600">
            {columns
              .filter((c) => c.key !== "label")
              .map((col) => (
                <th
                  key={col.key}
                  className={[
                    "py-3 px-3 border-b border-gray-200",
                    col.align === "right" ? "text-right" : "text-left",
                  ].join(" ")}
                >
                  {col.subLabel || col.label || ""}
                </th>
              ))}
          </tr>
        </thead>
        <tbody>
          {rows.map((r) => (
            <tr key={r.id} className="border-b border-gray-100 hover:bg-gray-50">
              {columns.map((col) => {
                if (col.key === "label") {
                  return (
                    <td
                      key={col.key}
                      className="py-2 px-3 font-medium sticky left-0 bg-white z-10"
                    >
                      {r.label}
                    </td>
                  );
                }

                const v = r.values?.[col.key];
                return (
                  <td
                    key={col.key}
                    className={["py-2 px-3", col.align === "right" ? "text-right" : ""].join(" ")}
                  >
                    <MetricCell value={v} kind={col.kind || measure} />
                  </td>
                );
              })}
            </tr>
          ))}

          {rows.length === 0 && (
            <tr>
              <td colSpan={columns.length} className="py-10 text-center text-gray-500">
                No rows match your filters.
              </td>
            </tr>
          )}
        </tbody>
      </table>
    </div>
  );
}
