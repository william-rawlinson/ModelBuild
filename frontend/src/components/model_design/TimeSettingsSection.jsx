import Section from "../ui/Section";
import Button from "../ui/Button";
import { Field, FieldRow, TextInput, Select } from "../ui/Field";
import { TIME_UNITS } from "./utils";

export default function TimeSettingsSection({ form, setForm}) {
  const setTimeHorizonValue = (value) => {
    if (value === "") {
      setForm((prev) => ({
        ...prev,
        time_horizon: { ...prev.time_horizon, value: "" },
      }));
      return;
    }

    const n = Number(value);
    if (!Number.isInteger(n) || n < 0) return;

    setForm((prev) => ({
      ...prev,
      time_horizon: { ...prev.time_horizon, value: n },
    }));
  };

  const setCycleLengthValue = (value) => {
    if (value === "") {
      setForm((prev) => ({
        ...prev,
        cycle_length: { ...prev.cycle_length, value: "" },
      }));
      return;
    }

    const n = Number(value);
    if (!Number.isFinite(n) || n <= 0) return;

    setForm((prev) => ({
      ...prev,
      cycle_length: { ...prev.cycle_length, value: n },
    }));
  };

  return (
    <Section title="Time settings" description="PLACEHOLDER TEXT">
      <div className="grid grid-cols-1 gap-6 md:grid-cols-2">
        <div className="rounded-2xl border bg-slate-50 p-5">
          <Field label="Time horizon" hint="PLACEHOLDER TEXT">
            <FieldRow>
              <TextInput
                inputMode="numeric"
                value={form.time_horizon.value}
                onChange={(e) => setTimeHorizonValue(e.target.value)}
                placeholder="20"
              />
              <Select
                value={form.time_horizon.unit}
                onChange={(e) =>
                  setForm((prev) => ({
                    ...prev,
                    time_horizon: { ...prev.time_horizon, unit: e.target.value },
                  }))
                }
              >
                {TIME_UNITS.map((u) => (
                  <option key={u.value} value={u.value}>
                    {u.label}
                  </option>
                ))}
              </Select>
            </FieldRow>
          </Field>
        </div>

        <div className="rounded-2xl border bg-slate-50 p-5">
          <Field label="Cycle length" hint="PLACEHOLDER TEXT">
            <FieldRow>
              <TextInput
                inputMode="decimal"
                value={form.cycle_length.value}
                onChange={(e) => setCycleLengthValue(e.target.value)}
                placeholder="1"
              />
              <Select
                value={form.cycle_length.unit}
                onChange={(e) =>
                  setForm((prev) => ({
                    ...prev,
                    cycle_length: { ...prev.cycle_length, unit: e.target.value },
                  }))
                }
              >
                {TIME_UNITS.map((u) => (
                  <option key={u.value} value={u.value}>
                    {u.label}
                  </option>
                ))}
              </Select>
            </FieldRow>
          </Field>
        </div>
      </div>
    </Section>
  );
}
