import { useState } from "react";
import Section from "../ui/Section";
import Button from "../ui/Button";
import Chip from "../ui/Chip";
import { Field, FieldRow, TextInput } from "../ui/Field";
import { normalizeName } from "./utils";

export default function HealthStatesSection({ form, setForm }) {
  const [newState, setNewState] = useState("");

  const addHealthState = () => {
    const candidate = normalizeName(newState);
    if (!candidate) return;

    setForm((prev) => {
      const exists = prev.health_states.some(
        (s) => s.toLowerCase() === candidate.toLowerCase()
      );
      if (exists) return prev;

      return { ...prev, health_states: [...prev.health_states, candidate] };
    });

    setNewState("");
  };

  const removeHealthState = (stateToRemove) => {
    setForm((prev) => ({
      ...prev,
      health_states: prev.health_states.filter((s) => s !== stateToRemove),
    }));
  };

  const onKeyDown = (e) => {
    if (e.key === "Enter") {
      e.preventDefault();
      addHealthState();
    }
  };

  const right = (
    <div className="text-sm text-slate-500">
      {form.health_states.length} state{form.health_states.length === 1 ? "" : "s"}
    </div>
  );

  return (
    <Section title="Health states" description="PLACEHOLDER TEXT" right={right}>
      <Field>
        <FieldRow className="flex-col md:flex-row md:items-center">
          <TextInput
            value={newState}
            onChange={(e) => setNewState(e.target.value)}
            onKeyDown={onKeyDown}
            placeholder='e.g. "Stable", "Progressed", "Death"'
          />
          <Button
            type="button"
            onClick={addHealthState}
            disabled={!normalizeName(newState)}
            className="w-full md:w-auto"
          >
            Add
          </Button>
        </FieldRow>
      </Field>

      <div className="flex flex-wrap gap-2">
        {form.health_states.map((s) => (
          <Chip key={s} onRemove={() => removeHealthState(s)}>
            {s}
          </Chip>
        ))}
      </div>

      <div className="text-sm text-slate-500">PLACEHOLDER TEXT</div>
    </Section>
  );
}
