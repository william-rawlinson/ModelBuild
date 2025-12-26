// ModelDesignForm.jsx
import { useMemo, useState } from "react";
import Card from "./ui/Card";

import InterventionsComparatorsSection from "./model_design/InterventionsComparatorsSection";
import DescribeModelSection from "./model_design/DescribeModelSection";
import DefineDataSection from "./model_design/DefineDataSection";
import GenerateModelSection from "./model_design/GenerateModelSection";
import SettingsSection from "./model_design/SettingsSection"; // <-- add

export default function ModelDesignForm() {
  const [form, setForm] = useState({
  intervention: "Treatment A",
  comparators: ["Treatment B"],
  model_description: "",
  data_points: [],

  disc_rate_cost_annual: 0.035,
  disc_rate_qaly_annual: 0.035,
  wtp_threshold: 30000,

  // raw inputs (needed for the unit toggles)
  time_horizon: { value: 20, unit: "years" },
  cycle_length: { value: 1, unit: "years" },

  // derived values sent to backend
  time_horizon_years: 20,
  cycle_length_years: 1,
  });

  const payloadPreview = useMemo(() => JSON.stringify(form, null, 2), [form]);

  const canProceed =
    !!form.intervention &&
    form.comparators.length >= 1 &&
    form.model_description?.trim().length > 0;

  const handleSubmit = (e) => {
    e.preventDefault();
    console.log("Model design payload:", form);
  };

  return (
    <Card className="w-full">
      <div className="space-y-2">
        <h1 className="text-4xl font-bold text-slate-900">Design your model</h1>
        <p className="text-lg text-slate-600">PLACEHOLDER TEXT</p>
      </div>

      <form onSubmit={handleSubmit} className="mt-10 space-y-10">
        <InterventionsComparatorsSection form={form} setForm={setForm} />
        <SettingsSection form={form} setForm={setForm} />
        <DescribeModelSection form={form} setForm={setForm} />
        <DefineDataSection form={form} setForm={setForm} />
        <GenerateModelSection
          form={form}
          canProceed={canProceed}
          generateUrl="http://localhost:8000/generate-model"
          processName="generate_model"
        />
      </form>
    </Card>
  );
}




