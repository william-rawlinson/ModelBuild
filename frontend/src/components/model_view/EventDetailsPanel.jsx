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

  const md = event.metadata ?? {};
  const impactType = md.impact_type ?? "—";
  const description = md.description ?? "";
  const assumptions = md.assumptions ?? [];
  const enabled = md.enabled ?? true;

  const treatments = md.applies_to_treatments ?? [];
  const states = md.applies_to_states ?? [];

  const codeText = event.final_code ?? event.code ?? "";

  return (
    <Card className="w-full">
      {/* Header */}
      <div className="flex items-start justify-between gap-4">
        <div className="space-y-1">
          <div className="text-2xl font-bold text-slate-900">
            {event.event_name}
          </div>
          <div className="text-sm text-slate-500">
            Type: <span className="font-semibold">{impactType}</span>
            <span className="mx-2">·</span>
            Enabled: <span className="font-semibold">{enabled ? "Yes" : "No"}</span>
          </div>
        </div>

        <Button type="button" variant="secondary" onClick={onClose}>
          Close
        </Button>
      </div>

      <div className="mt-8 space-y-8">
        {/* Description first */}
        <Section title="Description">
          {description ? (
            <div className="text-slate-700">{description}</div>
          ) : (
            <div className="text-slate-500">No description provided.</div>
          )}
        </Section>

        {/* Assumptions next */}
        <Section title="Assumptions">
          {assumptions.length ? (
            <ul className="list-disc pl-6 space-y-2 text-slate-900">
              {assumptions.map((a, i) => (
                <li key={i}>{a}</li>
              ))}
            </ul>
          ) : (
            <div className="text-slate-500">No assumptions recorded.</div>
          )}
        </Section>

        {/* Coverage formatted */}
        <Section title="Coverage" description="Where this event applies.">
          <div className="grid grid-cols-1 gap-6 sm:grid-cols-2">
            <div>
              <div className="mb-2 text-sm font-semibold text-slate-900">
                Treatments
              </div>
              {treatments.length ? (
                <ul className="space-y-1">
                  {treatments.map((t) => (
                    <li
                      key={t}
                      className="rounded-lg border bg-slate-50 px-3 py-1 text-sm text-slate-800"
                    >
                      {t}
                    </li>
                  ))}
                </ul>
              ) : (
                <div className="text-sm text-slate-500">
                  No treatments specified.
                </div>
              )}
            </div>

            <div>
              <div className="mb-2 text-sm font-semibold text-slate-900">
                Health states
              </div>
              {states.length ? (
                <ul className="space-y-1">
                  {states.map((s) => (
                    <li
                      key={s}
                      className="rounded-lg border bg-slate-50 px-3 py-1 text-sm text-slate-800"
                    >
                      {s}
                    </li>
                  ))}
                </ul>
              ) : (
                <div className="text-sm text-slate-500">
                  No states specified.
                </div>
              )}
            </div>
          </div>
        </Section>

        {/* Code at the bottom */}
        <Section title="Code" description="Generated implementation for this event.">
          {codeText ? (
            <pre className="overflow-auto rounded-2xl bg-slate-900 p-5 text-sm text-slate-100">
{codeText}
            </pre>
          ) : (
            <div className="text-sm text-slate-500">No code available.</div>
          )}
        </Section>
      </div>
    </Card>
  );
}



