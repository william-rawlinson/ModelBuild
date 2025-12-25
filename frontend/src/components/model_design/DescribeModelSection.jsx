// src/components/model_design/DescribeModelSection.jsx
import { useRef, useState } from "react";
import Section from "../ui/Section";
import Button from "../ui/Button";
import { Field } from "../ui/Field";

export default function DescribeModelSection({
  form,
  setForm,
  uploadUrl = "http://localhost:8000/upload-model/spec",
}) {
  const fileInputRef = useRef(null);

  const [isUploading, setIsUploading] = useState(false);
  const [errorText, setErrorText] = useState(null);
  const [infoText, setInfoText] = useState(null);

  const description = form.model_description ?? "";

  const setDescription = (text) => {
    setForm((prev) => ({ ...prev, model_description: text }));
  };

  const appendDescription = (textToAppend) => {
    const existing = form.model_description ?? "";
    const incoming = textToAppend ?? "";

    if (!incoming.trim()) return;

    const divider =
      existing.length === 0
        ? ""
        : "\n\n---\nImported from model specification (.docx)\n---\n\n";

    setForm((prev) => ({
      ...prev,
      model_description: `${existing}${divider}${incoming}`.trim(),
    }));
  };

  const validateDocx = (file) => {
    if (!file) return "No file selected.";
    const nameOk = file.name?.toLowerCase().endsWith(".docx");
    const mimeOk =
      file.type ===
        "application/vnd.openxmlformats-officedocument.wordprocessingml.document" ||
      file.type === ""; // browsers sometimes omit mime
    if (!nameOk && !mimeOk) return "Please upload a .docx Word document.";
    return null;
  };

  const triggerFilePicker = () => {
    setErrorText(null);
    setInfoText(null);
    fileInputRef.current?.click();
  };

  const onFileSelected = async (e) => {
    const file = e.target.files?.[0];
    // allow selecting the same file twice
    e.target.value = "";

    setErrorText(null);
    setInfoText(null);

    const validationError = validateDocx(file);
    if (validationError) {
      setErrorText(validationError);
      return;
    }

    setIsUploading(true);

    try {
      const formData = new FormData();
      formData.append("file", file);

      const res = await fetch(uploadUrl, {
        method: "POST",
        body: formData,
      });

      if (!res.ok) {
          let msg = `Upload failed (${res.status})`;
          try {
            const errJson = await res.json();
            msg = errJson?.detail || msg;
          } catch {
            const errText = await res.text();
            if (errText) msg = errText;
          }
          throw new Error(msg);
        }


      const data = await res.json();
      const extracted = data?.extracted_text ?? data?.text ?? "";

      const warnings = data?.warnings || [];
        if (warnings.length) {
          setInfoText(`Imported. Note: ${warnings[0]}`);
        } else {
          setInfoText("Specification imported and appended to the description.");
        }

      if (!extracted || extracted.trim().length === 0) {
        setErrorText("Uploaded file contained no extractable text.");
        return;
      }

      appendDescription(extracted);
      setInfoText("Specification imported and appended to the description.");
    } catch (err) {
      setErrorText(err?.message || "Upload failed.");
    } finally {
      setIsUploading(false);
    }
  };

  return (
    <Section
      title="Describe model"
      description="Write a short narrative of the decision problem, or upload a .docx specification and we’ll append the extracted text here."
      right={
        <div className="text-sm text-slate-500">
          {description.length.toLocaleString()} chars
        </div>
      }
    >
      <div className="rounded-2xl border bg-slate-50 p-5 space-y-4">
        <Field label="Model description" hint="This will be used to guide scenario generation and model defaults.">
          <textarea
            value={description}
            onChange={(e) => setDescription(e.target.value)}
            rows={10}
            placeholder="Describe the indication, population, comparators, perspective, key assumptions, and any special modelling requirements…"
            className="w-full rounded-xl border bg-white px-4 py-3 text-lg outline-none focus:ring-2 resize-y"
          />
        </Field>

        <div className="flex flex-col gap-3 md:flex-row md:items-center md:justify-between">
          <div className="flex flex-col gap-2 md:flex-row md:items-center">
            <input
              ref={fileInputRef}
              type="file"
              accept=".docx,application/vnd.openxmlformats-officedocument.wordprocessingml.document"
              className="hidden"
              onChange={onFileSelected}
            />

            <Button
              type="button"
              variant="secondary"
              onClick={triggerFilePicker}
              disabled={isUploading}
              className="w-full md:w-auto"
            >
              {isUploading ? "Uploading..." : "Upload model specification (.docx)"}
            </Button>

            <div className="text-sm text-slate-500">
              The extracted text will be <span className="font-semibold">appended</span> (not replaced).
            </div>
          </div>

          {/* Status */}
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
          </div>
        </div>
      </div>
    </Section>
  );
}
