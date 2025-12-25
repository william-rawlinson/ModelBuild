import React, { useMemo, useState } from "react";
import dummyResults from "../../data/dummy_results.json";

import ResultsFiltersBar from "./ResultsFiltersBar";
import ResultsSummaryStrip from "./ResultsSummaryStrip";
import ResultsPivotTable from "./ResultsPivotTable";
import { buildResultsViewModel } from "./resultsSelectors";

// If you have these style primitives, use them:
// import { contentCardClass, componentHeadingClass } from "../utils/styles";

export default function ResultsTableCard({ results = dummyResults }) {
  const [settings, setSettings] = useState(null); // null => selectors will apply defaults

  const vm = useMemo(() => buildResultsViewModel(results, settings), [results, settings]);

  return (
    <div className="w-full border border-gray-200 rounded-2xl p-5 bg-white shadow-sm">
      <div className="flex items-center justify-between gap-4 mb-4">
        <div>
          <div className="text-2xl font-bold text-gray-900">Results</div>
          <div className="text-sm text-gray-600">
            Comparing <span className="font-semibold">{vm.intervention}</span> vs{" "}
            {vm.settings.comparators.length ? vm.settings.comparators.join(", ") : "no comparators selected"}
          </div>
        </div>
      </div>

      <div className="mb-5">
        <ResultsFiltersBar
          settings={vm.settings}
          options={vm.options}
          onSettingsChange={setSettings}
        />
      </div>

      <div className="mb-5">
        <ResultsSummaryStrip summary={vm.summary} />
      </div>

      <ResultsPivotTable columns={vm.columns} rows={vm.rows} measure={vm.settings.measure} />
    </div>
  );
}
