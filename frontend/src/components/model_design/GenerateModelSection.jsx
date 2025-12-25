import { useEffect, useRef, useState } from "react";
import Section from "../ui/Section";
import Button from "../ui/Button";
import ProcessLogDisplay from "../ProcessLogDisplay";
import useProcessLog from "../../hooks/useProcessLog"; // adjust if your paths differ

export default function GenerateModelSection({
  form,
  canProceed,
  generateUrl = "http://localhost:8000/generate-model/",
  processName = "generate_model",
}) {
  const { progressMessages, isRunning, clear } = useProcessLog({ processName });
  const topMessageRef = useRef(null);

  const [errorText, setErrorText] = useState(null);
  const [infoText, setInfoText] = useState(null);

  useEffect(() => {
    if (topMessageRef.current) {
      topMessageRef.current.scrollIntoView({ behavior: "smooth", block: "start" });
    }
  }, [progressMessages]);

  const handleGenerate = async () => {
    setErrorText(null);
    setInfoText(null);
    clear();

    try {
      const res = await fetch(generateUrl, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(form),
      });

      if (!res.ok) {
        let msg = `Generate failed (${res.status})`;
        try {
          const errJson = await res.json();
          msg = errJson?.detail || msg;
        } catch {
          const errText = await res.text();
          if (errText) msg = errText;
        }
        throw new Error(msg);
      }

      setInfoText("Generation started…");
    } catch (err) {
      setErrorText(err?.message || "Generate failed.");
    }
  };

  return (
    <Section
      title="Generate model"
      description="When ready, generate the model from your design inputs."
      right={
        <div className="text-sm text-slate-500">
          {isRunning ? "Running…" : "Ready"}
        </div>
      }
    >
      <div className="rounded-2xl border bg-slate-50 p-5 space-y-4">
        <div className="flex flex-col gap-3 md:flex-row md:items-center md:justify-between">
          <Button
            type="button"
            onClick={handleGenerate}
            disabled={!canProceed || isRunning}
            className="w-full md:w-auto"
          >
            {isRunning ? "Generating..." : "Generate model"}
          </Button>

          <div className="text-sm">
            {infoText && (
              <span className="inline-flex items-center rounded-full border bg-emerald-50 px-3 py-1 text-emerald-700">
                {infoText}
              </span>
            )}
            {errorText && (
              <span className="inline-flex items-center rounded-full border bg-rose-50 px-3 py-1 text-rose-700">
                {errorText}
              </span>
            )}
            {!canProceed && !isRunning && !errorText && (
              <span className="inline-flex items-center rounded-full border bg-slate-100 px-3 py-1 text-slate-700">
                Fill in required fields to enable generation
              </span>
            )}
          </div>
        </div>

        <ProcessLogDisplay
          progressMessages={progressMessages}
          isRunning={isRunning}
          topMessageRef={topMessageRef}
          completionText="✅ Model generation completed!"
        />
      </div>
    </Section>
  );
}
