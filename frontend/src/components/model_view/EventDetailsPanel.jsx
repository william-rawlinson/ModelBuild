import Card from "../ui/Card";
import Button from "../ui/Button";
import Section from "../ui/Section";

export default function EventDetailsPanel({ event, onClose }) {
  if (!event) {
    return (
      <Card className="w-full">
        <div className="text-2xl font-bold text-slate-900">Event details</div>
        <div className="mt-3 text-slate-600">
          Click an event tile in the diagram to see details here.
        </div>
      </Card>
    );
  }

  return (
    <Card className="w-full">
      <div className="flex items-start justify-between gap-4">
        <div className="space-y-1">
          <div className="text-2xl font-bold text-slate-900">{event.label}</div>
          <div className="text-sm text-slate-500">
            Type: <span className="font-semibold">{event.type}</span>
          </div>
        </div>

        <Button type="button" variant="secondary" onClick={onClose}>
          Close
        </Button>
      </div>

      <div className="mt-8 space-y-8">
        <Section title="Coverage" description="Where this event applies.">
          <pre className="overflow-auto rounded-2xl bg-slate-900 p-5 text-sm text-slate-100">
{JSON.stringify(event.applies_to ?? event.transition ?? {}, null, 2)}
          </pre>
        </Section>

        <Section title="Implementation" description="How this is represented in the model.">
          <div className="rounded-2xl border bg-slate-50 p-5 space-y-2">
            <div className="text-slate-900">
              <span className="font-semibold">Code ref:</span>{" "}
              <span className="font-mono">{event.code_ref ?? "—"}</span>
            </div>
            <div className="text-slate-900">
              <span className="font-semibold">Spec used:</span>{" "}
              {event.spec_used ? "Yes" : "No"}
            </div>
            <div className="text-slate-900">
              <span className="font-semibold">QC status:</span>{" "}
              {event.qc_status ?? "—"}
            </div>
          </div>
        </Section>

        <Section title="Assumptions" description="Notes and assumptions applied.">
          <div className="rounded-2xl border bg-slate-50 p-5">
            {event.assumptions?.length ? (
              <ul className="list-disc pl-6 space-y-2 text-slate-900">
                {event.assumptions.map((a, i) => (
                  <li key={i}>{a}</li>
                ))}
              </ul>
            ) : (
              <div className="text-slate-600">No assumptions recorded.</div>
            )}
          </div>
        </Section>
      </div>
    </Card>
  );
}
