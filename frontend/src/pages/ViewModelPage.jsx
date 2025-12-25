import { useState } from "react";
import ResultsTableCard from "../components/results_table/ResultsTableCard";
import ModelDiagram from "../components/model_view/ModelDiagram";
import EventDetailsPanel from "../components/model_view/EventDetailsPanel";
import { dummyModelView } from "../components/model_view/dummyModelView";

export default function ViewModelPage() {
  const [selectedEvent, setSelectedEvent] = useState(null);

  return (
    <div className="space-y-6">
        <ResultsTableCard />
      <div className="space-y-1">
        <div className="text-3xl font-bold text-slate-900">View model</div>
        <div className="text-slate-600">
          Dummy diagram (states, transitions, and events). Click an event to view details.
        </div>
      </div>

      <div className="space-y-6">

        <ModelDiagram
          model={dummyModelView}
          onSelectEvent={(ev) => setSelectedEvent(ev)}
        />

        <EventDetailsPanel
          event={selectedEvent}
          onClose={() => setSelectedEvent(null)}
        />
      </div>
    </div>
  );
}
