import { useMemo, useState } from "react";
import Card from "./ui/Card";

import InterventionsComparatorsSection from "./model_design/InterventionsComparatorsSection";
import HealthStatesSection from "./model_design/HealthStatesSection";
import TimeSettingsSection from "./model_design/TimeSettingsSection";
import DescribeModelSection from "./model_design/DescribeModelSection";
import DefineDataSection from "./model_design/DefineDataSection";
import GenerateModelSection from "./model_design/GenerateModelSection";


export default function ModelDesignForm() {
  const [form, setForm] = useState({
    intervention: "Treatment A",
    comparators: ["Treatment B"],
    health_states: ["PFS", "PPS", "Death"],
    time_horizon: { value: 20, unit: "years" },
    cycle_length: { value: 1, unit: "years" },
    model_description: "",
    data_points: [],
  });

  const payloadPreview = useMemo(() => JSON.stringify(form, null, 2), [form]);

  const canProceed =
      !!form.intervention &&
      form.comparators.length >= 1 &&
      form.health_states.length >= 2 &&
      form.time_horizon.value !== "" &&
      form.time_horizon.value > 0 &&
      form.cycle_length.value !== "" &&
      form.cycle_length.value > 0 &&
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
        <HealthStatesSection form={form} setForm={setForm} />
        <TimeSettingsSection form={form} setForm={setForm}/>
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



