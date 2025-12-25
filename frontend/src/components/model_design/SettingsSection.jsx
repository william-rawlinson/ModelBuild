// src/components/model_design/SettingsSection.jsx
import Section from "../ui/Section";
import { Field, FieldRow, TextInput } from "../ui/Field";

function roundTo(x, dp = 6) {
  const p = 10 ** dp;
  return Math.round(x * p) / p;
}

function toCleanString(x, dp = 6) {
  // Avoid scientific notation + remove trailing zeros
  const s = Number(x).toFixed(dp);
  return s.replace(/0+$/, "").replace(/\.$/, "");
}


function fmtDecimal(x, dp = 4) {
  if (x === "" || x === null || x === undefined) return "—";
  const n = Number(x);
  if (Number.isNaN(n)) return "—";
  return n.toFixed(dp).replace(/0+$/, "").replace(/\.$/, "");
}

function clamp(num, min, max) {
  if (Number.isNaN(num)) return min;
  return Math.min(max, Math.max(min, num));
}

function toPercentString(decimal) {
  if (decimal === null || decimal === undefined || decimal === "") return "";
  const n = Number(decimal);
  if (Number.isNaN(n)) return "";

  // critical: round AFTER multiplying to avoid 3.5000000000000004
  const pct = roundTo(n * 100, 6);
  return toCleanString(pct, 6);
}

function percentStringToDecimal(str) {
  if (str === "") return "";
  const n = Number(str);
  if (Number.isNaN(n)) return "";
  return roundTo(n / 100, 6);
}

export default function SettingsSection({ form, setForm }) {
  const discountCostPct = toPercentString(form.discount_rate_cost);
  const discountQalyPct = toPercentString(form.discount_rate_qaly);

  const updateDiscountCost = (raw) => {
    const dec = percentStringToDecimal(raw);
    if (dec === "") {
      setForm((prev) => ({ ...prev, discount_rate_cost: "" }));
      return;
    }
    setForm((prev) => ({ ...prev, discount_rate_cost: clamp(dec, 0, 1) }));
  };

  const updateDiscountQaly = (raw) => {
    const dec = percentStringToDecimal(raw);
    if (dec === "") {
      setForm((prev) => ({ ...prev, discount_rate_qaly: "" }));
      return;
    }
    setForm((prev) => ({ ...prev, discount_rate_qaly: clamp(dec, 0, 1) }));
  };

  const updateWTP = (raw) => {
    if (raw === "") {
      setForm((prev) => ({ ...prev, wtp_threshold: "" }));
      return;
    }
    const n = Number(raw);
    if (Number.isNaN(n)) return; // ignore junk
    setForm((prev) => ({ ...prev, wtp_threshold: Math.max(0, n) }));
  };

  const right = (
    <div className="text-sm text-slate-500">
      Annual discounting + WTP threshold
    </div>
  );

  return (
    <Section
      title="Settings"
      description="Set discount rates and the willingness-to-pay threshold used for ICER interpretation."
      right={right}
    >
      <div className="grid grid-cols-1 gap-6 lg:grid-cols-3">
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
                {/* add padding-left if your TextInput doesn't already */}
              </div>
            </FieldRow>
          </Field>
        </div>
      </div>

      <div className="text-sm text-slate-500">
        Tip: keep discount rates between 0–100%
      </div>
    </Section>
  );
}
