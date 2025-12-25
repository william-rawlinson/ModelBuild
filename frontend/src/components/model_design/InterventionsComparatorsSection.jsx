import { useState } from "react";
import Section from "../ui/Section";
import Button from "../ui/Button";
import Chip from "../ui/Chip";
import { Field, FieldRow, TextInput } from "../ui/Field";
import { normalizeName } from "./utils";

export default function InterventionsComparatorsSection({ form, setForm }) {
  const [newIntervention, setNewIntervention] = useState("");
  const [newComparator, setNewComparator] = useState("");

  const armCount = 1 + form.comparators.length;

  const setInterventionFromInput = () => {
    const candidate = normalizeName(newIntervention);
    if (!candidate) return;

    setForm((prev) => ({ ...prev, intervention: candidate }));
    setNewIntervention("");
  };

  const addComparator = () => {
    const candidate = normalizeName(newComparator);
    if (!candidate) return;

    setForm((prev) => {
      const all = [prev.intervention, ...prev.comparators].filter(Boolean);
      const exists = all.some((x) => x.toLowerCase() === candidate.toLowerCase());
      if (exists) return prev;
      return { ...prev, comparators: [...prev.comparators, candidate] };
    });

    setNewComparator("");
  };

  const removeComparator = (name) => {
    setForm((prev) => ({
      ...prev,
      comparators: prev.comparators.filter((c) => c !== name),
    }));
  };

  const onInterventionKeyDown = (e) => {
    if (e.key === "Enter") {
      e.preventDefault();
      setInterventionFromInput();
    }
  };

  const onComparatorKeyDown = (e) => {
    if (e.key === "Enter") {
      e.preventDefault();
      addComparator();
    }
  };

  const right = (
    <div className="text-sm text-slate-500">
      {armCount} arm{armCount === 1 ? "" : "s"}
    </div>
  );

  return (
    <Section
      title="Interventions and comparators"
      description="Define the primary intervention and at least one comparator."
      right={right}
    >
      <div className="grid grid-cols-1 gap-6 lg:grid-cols-2">
        {/* Intervention */}
        <div className="rounded-2xl border bg-slate-50 p-5 space-y-3">
          <Field
            label="Intervention"
            hint="This is the primary strategy you’re evaluating."
          >
            <FieldRow className="flex-col md:flex-row md:items-center">
              <TextInput
                value={newIntervention}
                onChange={(e) => setNewIntervention(e.target.value)}
                onKeyDown={onInterventionKeyDown}
                placeholder='e.g. "Treatment A"'
              />
              <Button
                type="button"
                onClick={setInterventionFromInput}
                disabled={!normalizeName(newIntervention)}
                className="w-full md:w-auto"
              >
                Set
              </Button>
            </FieldRow>
          </Field>

          <div className="flex flex-wrap gap-2">
            <span className="inline-flex items-center gap-2 rounded-full border bg-indigo-50 px-4 py-2 text-lg">
              <span className="text-indigo-900 font-semibold">
                {form.intervention || "—"}
              </span>
            </span>
          </div>
        </div>

        {/* Comparators */}
        <div className="rounded-2xl border bg-slate-50 p-5 space-y-3">
          <Field
            label="Comparators"
            hint="Add one or more comparators to compare against the intervention."
          >
            <FieldRow className="flex-col md:flex-row md:items-center">
              <TextInput
                value={newComparator}
                onChange={(e) => setNewComparator(e.target.value)}
                onKeyDown={onComparatorKeyDown}
                placeholder='e.g. "Standard of care"'
              />
              <Button
                type="button"
                onClick={addComparator}
                disabled={!normalizeName(newComparator)}
                className="w-full md:w-auto"
              >
                Add
              </Button>
            </FieldRow>
          </Field>

          <div className="flex flex-wrap gap-2">
            {form.comparators.map((c) => (
              <Chip key={c} onRemove={() => removeComparator(c)}>
                {c}
              </Chip>
            ))}
          </div>

          <div className="text-sm text-slate-500">
            Tip: keep names consistent (these become keys in your model spec).
          </div>
        </div>
      </div>
    </Section>
  );
}
