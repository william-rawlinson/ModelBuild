// src/components/model_design/SettingsSection.jsx
import Section from "../ui/Section";
import { Field, FieldRow, TextInput } from "../ui/Field";

function roundTo(x, dp = 6) {
  const p = 10 ** dp;
  return Math.round(x * p) / p;
}

function toCleanString(x, dp = 6) {
  const s = Number(x).toFixed(dp);
  return s.replace(/0+$/, "").replace(/\.$/, "");
}

function clamp(num, min, max) {
  if (Number.isNaN(num)) return min;
  return Math.min(max, Math.max(min, num));
}

function toPercentString(decimal) {
  if (decimal === null || decimal === undefined || decimal === "") return "";
  const n = Number(decimal);
  if (Number.isNaN(n)) return "";
  const pct = roundTo(n * 100, 6);
  return toCleanString(pct, 6);
}

function percentStringToDecimal(str) {
  if (str === "") return "";
  const n = Number(str);
  if (Number.isNaN(n)) return "";
  return roundTo(n / 100, 6);
}

// ---- time unit conversions -> years ----
// Note: months/years vary in reality; for modelling we use common HE convention.
const UNIT_TO_YEARS = {
  days: 1 / 365,
  weeks: 1 / 52,
  months: 1 / 12,
  years: 1,
};

const TIME_UNITS = ["days", "weeks", "months", "years"];

function toYears(value, unit) {
  if (value === "" || value === null || value === undefined) return "";
  const n = Number(value);
  if (Number.isNaN(n)) return "";
  const factor = UNIT_TO_YEARS[unit] ?? 1;
  return roundTo(n * factor, 8); // a bit more precision before downstream rounding
}

function SelectUnit({ value, onChange }) {
  return (
    <select
      value={value}
      onChange={onChange}
      className="h-11 rounded-xl border bg-white px-3 text-slate-900 shadow-sm focus:outline-none focus:ring-2 focus:ring-indigo-500"
    >
      {TIME_UNITS.map((u) => (
        <option key={u} value={u}>
          {u}
        </option>
      ))}
    </select>
  );
}

export default function SettingsSection({ form, setForm }) {
  const discountCostPct = toPercentString(form.disc_rate_cost_annual);
  const discountQalyPct = toPercentString(form.disc_rate_qaly_annual);

  const updateDiscountCost = (raw) => {
    const dec = percentStringToDecimal(raw);
    if (dec === "") {
      setForm((prev) => ({ ...prev, disc_rate_cost_annual: "" }));
      return;
    }
    setForm((prev) => ({ ...prev, disc_rate_cost_annual: clamp(dec, 0, 1) }));
  };

  const updateDiscountQaly = (raw) => {
    const dec = percentStringToDecimal(raw);
    if (dec === "") {
      setForm((prev) => ({ ...prev, disc_rate_qaly_annual: "" }));
      return;
    }
    setForm((prev) => ({ ...prev, disc_rate_qaly_annual: clamp(dec, 0, 1) }));
  };

  const updateWTP = (raw) => {
    if (raw === "") {
      setForm((prev) => ({ ...prev, wtp_threshold: "" }));
      return;
    }
    const n = Number(raw);
    if (Number.isNaN(n)) return;
    setForm((prev) => ({ ...prev, wtp_threshold: Math.max(0, n) }));
  };

  // ---- Time horizon / cycle length setters that also write *_years ----
  const updateTimeHorizonValue = (raw) => {
    if (raw === "") {
      setForm((prev) => ({
        ...prev,
        time_horizon: { ...prev.time_horizon, value: "" },
        time_horizon_years: "",
      }));
      return;
    }
    const n = Number(raw);
    if (Number.isNaN(n)) return;
    setForm((prev) => {
      const nextTH = { ...prev.time_horizon, value: n };
      return {
        ...prev,
        time_horizon: nextTH,
        time_horizon_years: toYears(nextTH.value, nextTH.unit),
      };
    });
  };

  const updateTimeHorizonUnit = (unit) => {
    setForm((prev) => {
      const nextTH = { ...prev.time_horizon, unit };
      return {
        ...prev,
        time_horizon: nextTH,
        time_horizon_years: toYears(nextTH.value, nextTH.unit),
      };
    });
  };

  const updateCycleLengthValue = (raw) => {
    if (raw === "") {
      setForm((prev) => ({
        ...prev,
        cycle_length: { ...prev.cycle_length, value: "" },
        cycle_length_years: "",
      }));
      return;
    }
    const n = Number(raw);
    if (Number.isNaN(n)) return;
    setForm((prev) => {
      const nextCL = { ...prev.cycle_length, value: n };
      return {
        ...prev,
        cycle_length: nextCL,
        cycle_length_years: toYears(nextCL.value, nextCL.unit),
      };
    });
  };

  const updateCycleLengthUnit = (unit) => {
    setForm((prev) => {
      const nextCL = { ...prev.cycle_length, unit };
      return {
        ...prev,
        cycle_length: nextCL,
        cycle_length_years: toYears(nextCL.value, nextCL.unit),
      };
    });
  };

  const right = (
    <div className="text-sm text-slate-500">
      Time + discounting + WTP
    </div>
  );

  return (
    <Section
      title="Settings"
      description="Set time settings, discount rates, and the willingness-to-pay threshold."
      right={right}
    >
      <div className="grid grid-cols-1 gap-6 lg:grid-cols-3">
        {/* Time horizon */}
        <div className="rounded-2xl border bg-slate-50 p-5 space-y-3">
          <Field
            label="Time horizon"
            hint="Total modelled duration (e.g. 20 years)."
          >
            <FieldRow className="flex-col md:flex-row md:items-center gap-3">
              <TextInput
                inputMode="decimal"
                value={form.time_horizon?.value === "" ? "" : String(form.time_horizon?.value ?? "")}
                onChange={(e) => updateTimeHorizonValue(e.target.value)}
                placeholder="e.g. 20"
              />
              <SelectUnit
                value={form.time_horizon?.unit ?? "years"}
                onChange={(e) => updateTimeHorizonUnit(e.target.value)}
              />
            </FieldRow>
          </Field>

          <div className="text-sm text-slate-600">
            Sending:{" "}
            <span className="font-mono">
              {form.time_horizon_years === "" || form.time_horizon_years === undefined
                ? "—"
                : toCleanString(form.time_horizon_years, 6)}
            </span>{" "}
            years
          </div>
        </div>

        {/* Cycle length */}
        <div className="rounded-2xl border bg-slate-50 p-5 space-y-3">
          <Field
            label="Cycle length"
            hint="Length of one cycle (e.g. 3 months)."
          >
            <FieldRow className="flex-col md:flex-row md:items-center gap-3">
              <TextInput
                inputMode="decimal"
                value={form.cycle_length?.value === "" ? "" : String(form.cycle_length?.value ?? "")}
                onChange={(e) => updateCycleLengthValue(e.target.value)}
                placeholder="e.g. 3"
              />
              <SelectUnit
                value={form.cycle_length?.unit ?? "months"}
                onChange={(e) => updateCycleLengthUnit(e.target.value)}
              />
            </FieldRow>
          </Field>

          <div className="text-sm text-slate-600">
            Sending:{" "}
            <span className="font-mono">
              {form.cycle_length_years === "" || form.cycle_length_years === undefined
                ? "—"
                : toCleanString(form.cycle_length_years, 8)}
            </span>{" "}
            years
          </div>
        </div>

        {/* WTP threshold */}
        <div className="rounded-2xl border bg-slate-50 p-5 space-y-3">
          <Field
            label="Willingness-to-pay threshold"
            hint="Used to interpret cost-effectiveness (e.g. £20,000 per QALY)."
          >
            <FieldRow className="flex-col md:flex-row md:items-center">
              <div className="relative w-full">
                <TextInput
                  inputMode="numeric"
                  value={form.wtp_threshold === "" ? "" : String(form.wtp_threshold)}
                  onChange={(e) => updateWTP(e.target.value)}
                  placeholder="e.g. 20000"
                />
                <div className="pointer-events-none absolute inset-y-0 left-3 flex items-center text-slate-400">
                  £
                </div>
              </div>
            </FieldRow>
          </Field>
        </div>
      </div>

      <div className="grid grid-cols-1 gap-6 lg:grid-cols-2 mt-6">
        {/* Discount rate (costs) */}
        <div className="rounded-2xl border bg-slate-50 p-5 space-y-3">
          <Field
            label="Discount rate (costs)"
            hint="Annual discount rate for costs (as a percent)."
          >
            <FieldRow className="flex-col md:flex-row md:items-center">
              <div className="relative w-full">
                <TextInput
                  inputMode="decimal"
                  value={discountCostPct}
                  onChange={(e) => updateDiscountCost(e.target.value)}
                  placeholder="e.g. 3.5"
                />
                <div className="pointer-events-none absolute inset-y-0 right-3 flex items-center text-slate-400">
                  %
                </div>
              </div>
            </FieldRow>
          </Field>
        </div>

        {/* Discount rate (QALYs) */}
        <div className="rounded-2xl border bg-slate-50 p-5 space-y-3">
          <Field
            label="Discount rate (QALYs)"
            hint="Annual discount rate for QALYs (as a percent)."
          >
            <FieldRow className="flex-col md:flex-row md:items-center">
              <div className="relative w-full">
                <TextInput
                  inputMode="decimal"
                  value={discountQalyPct}
                  onChange={(e) => updateDiscountQaly(e.target.value)}
                  placeholder="e.g. 3.5"
                />
                <div className="pointer-events-none absolute inset-y-0 right-3 flex items-center text-slate-400">
                  %
                </div>
              </div>
            </FieldRow>
          </Field>
        </div>
      </div>

      <div className="text-sm text-slate-500 mt-4">
        Tip: discount rates are entered as percentages but stored as decimals. Time units are converted to years for the backend.
      </div>
    </Section>
  );
}

