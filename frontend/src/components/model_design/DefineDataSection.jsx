import { useRef, useState } from "react";
import Section from "../ui/Section";
import Button from "../ui/Button";
import { Field } from "../ui/Field";

const DISTRIBUTIONS = [
  { value: "", label: "—" },
  { value: "deterministic", label: "Deterministic" },
  { value: "normal", label: "Normal" },
  { value: "lognormal", label: "Lognormal" },
  { value: "beta", label: "Beta" },
  { value: "gamma", label: "Gamma" },
  { value: "uniform", label: "Uniform" },
  { value: "triangular", label: "Triangular" },
];

function normalizeText(s) {
  return (s ?? "").trim().replace(/\s+/g, " ");
}

function validateExcel(file) {
  if (!file) return "No file selected.";
  const name = file.name?.toLowerCase() ?? "";
  const ok = name.endsWith(".xlsx") || name.endsWith(".xlsm");
  if (!ok) return "Please upload an Excel file (.xlsx or .xlsm).";
  return null;
}

export default function DefineDataSection({
  form,
  setForm,
  uploadUrl = "http://localhost:8000/upload-model/data-sheet",
}) {
  const fileInputRef = useRef(null);
  const [isUploading, setIsUploading] = useState(false);
  const [errorText, setErrorText] = useState(null);
  const [infoText, setInfoText] = useState(null);

  const dataPoints = form.data_points ?? [];

  const setDataPoints = (next) => {
    setForm((prev) => ({ ...prev, data_points: next }));
  };

  const addRow = () => {
    setDataPoints([
      ...dataPoints,
      {
        description: "",
        base_case_value: "",
        distribution: "",
        standard_error: "",
      },
    ]);
  };

  const deleteRow = (idx) => {
    setDataPoints(dataPoints.filter((_, i) => i !== idx));
  };

  const updateCell = (idx, key, value) => {
    setDataPoints(
      dataPoints.map((row, i) => (i === idx ? { ...row, [key]: value } : row))
    );
  };

  const triggerFilePicker = () => {
    setErrorText(null);
    setInfoText(null);
    fileInputRef.current?.click();
  };

  const appendUploadedRows = (incomingRows) => {
    // de-dupe by description (case-insensitive), but only if description present
    const existingKeys = new Set(
      dataPoints
        .map((r) => normalizeText(r.description).toLowerCase())
        .filter(Boolean)
    );

    const cleaned = (incomingRows ?? [])
      .map((r) => ({
        description: normalizeText(r.description),
        base_case_value:
          r.base_case_value ?? r.baseCaseValue ?? r.base ?? r.value ?? "",
        distribution: r.distribution ?? "",
        standard_error: r.standard_error ?? r.standardError ?? r.se ?? "",
      }))
      .filter((r) => r.description.length > 0);

    const toAdd = [];
    for (const r of cleaned) {
      const k = r.description.toLowerCase();
      if (existingKeys.has(k)) continue;
      existingKeys.add(k);
      toAdd.push(r);
    }

    if (toAdd.length === 0) return 0;

    setDataPoints([...dataPoints, ...toAdd]);
    return toAdd.length;
  };

  const onFileSelected = async (e) => {
    const file = e.target.files?.[0];
    e.target.value = ""; // allow same file re-select

    setErrorText(null);
    setInfoText(null);

    const validationError = validateExcel(file);
    if (validationError) {
      setErrorText(validationError);
      return;
    }

    setIsUploading(true);
    try {
      const fd = new FormData();
      fd.append("file", file);

      const res = await fetch(uploadUrl, { method: "POST", body: fd });
      if (!res.ok) {
        const text = await res.text();
        throw new Error(text || `Upload failed (${res.status})`);
      }

      const data = await res.json();

      // Expect backend to return: { datapoints: [...] }
      const incoming = data?.datapoints ?? data?.data_points ?? data?.rows ?? [];
      if (!Array.isArray(incoming) || incoming.length === 0) {
        setErrorText("No datapoints found in the uploaded file.");
        return;
      }

      const addedCount = appendUploadedRows(incoming);
      if (addedCount === 0) {
        setInfoText("Upload succeeded, but no new datapoints were added (duplicates).");
      } else {
        setInfoText(`Added ${addedCount} datapoint${addedCount === 1 ? "" : "s"} from Excel.`);
      }
    } catch (err) {
      setErrorText(err?.message || "Upload failed.");
    } finally {
      setIsUploading(false);
    }
  };

  return (
    <Section
      title="Define data"
      description="Add datapoints manually and/or upload a Data sheet"
      right={
        <div className="text-sm text-slate-500">
          {dataPoints.length} row{dataPoints.length === 1 ? "" : "s"}
        </div>
      }
    >
      <div className="rounded-2xl border bg-slate-50 p-5 space-y-4">
        {/* Actions */}
        <div className="flex flex-col gap-3 md:flex-row md:items-center md:justify-between">
          <div className="flex flex-col gap-2 md:flex-row md:items-center">
            <Button type="button" variant="secondary" onClick={addRow}>
              + Add datapoint
            </Button>

            <input
              ref={fileInputRef}
              type="file"
              accept=".xlsx,.xlsm"
              className="hidden"
              onChange={onFileSelected}
            />

            <Button
              type="button"
              variant="secondary"
              onClick={triggerFilePicker}
              disabled={isUploading}
            >
              {isUploading ? "Uploading..." : "Upload Data sheet (.xlsx/.xlsm)"}
            </Button>
          </div>

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

        {/* Table */}
        <div className="overflow-auto rounded-2xl border bg-white">
          <table className="min-w-full border-collapse">
            <thead className="bg-slate-100">
              <tr>
                <th className="text-left px-4 py-3 text-sm font-semibold text-slate-700 w-[45%]">
                  Datapoint description
                </th>
                <th className="text-left px-4 py-3 text-sm font-semibold text-slate-700 w-[18%]">
                  Base case value
                </th>
                <th className="text-left px-4 py-3 text-sm font-semibold text-slate-700 w-[20%]">
                  Distribution
                </th>
                <th className="text-left px-4 py-3 text-sm font-semibold text-slate-700 w-[17%]">
                  Standard error
                </th>
                <th className="px-3 py-3 w-[1%]" />
              </tr>
            </thead>

            <tbody>
              {dataPoints.length === 0 ? (
                <tr>
                  <td className="px-4 py-6 text-slate-500" colSpan={5}>
                    No datapoints yet. Click “Add datapoint” or upload an Excel file.
                  </td>
                </tr>
              ) : (
                dataPoints.map((row, idx) => (
                  <tr key={idx} className="border-t">
                    <td className="px-4 py-3 align-top">
                      <Field>
                        <input
                          value={row.description ?? ""}
                          onChange={(e) => updateCell(idx, "description", e.target.value)}
                          placeholder="e.g. PFS→PPS transition probability (per cycle)"
                          className="w-full rounded-xl border bg-white px-3 py-2 text-base outline-none focus:ring-2"
                        />
                      </Field>
                    </td>

                    <td className="px-4 py-3 align-top">
                      <input
                        value={row.base_case_value ?? ""}
                        onChange={(e) => updateCell(idx, "base_case_value", e.target.value)}
                        placeholder="e.g. 0.12"
                        inputMode="decimal"
                        className="w-full rounded-xl border bg-white px-3 py-2 text-base outline-none focus:ring-2"
                      />
                    </td>

                    <td className="px-4 py-3 align-top">
                      <select
                        value={row.distribution ?? ""}
                        onChange={(e) => updateCell(idx, "distribution", e.target.value)}
                        className="w-full h-[42px] rounded-xl border bg-white px-3 py-0 text-base outline-none focus:ring-2">
                        {DISTRIBUTIONS.map((d) => (
                          <option key={d.value} value={d.value}>
                            {d.label}
                          </option>
                        ))}
                      </select>
                    </td>

                    <td className="px-4 py-3 align-top">
                      <input
                        value={row.standard_error ?? ""}
                        onChange={(e) => updateCell(idx, "standard_error", e.target.value)}
                        placeholder="e.g. 0.03"
                        inputMode="decimal"
                        className="w-full rounded-xl border bg-white px-3 py-2 text-base outline-none focus:ring-2"
                      />
                    </td>

                    <td className="px-3 py-3 align-top">
                      <button
                        type="button"
                        onClick={() => deleteRow(idx)}
                        className="rounded-xl px-3 py-2 text-slate-500 hover:bg-slate-100 hover:text-slate-900"
                        aria-label="Delete row"
                        title="Delete row"
                      >
                        ✕
                      </button>
                    </td>
                  </tr>
                ))
              )}
            </tbody>
          </table>
        </div>

        <div className="text-sm text-slate-500">
          Tip: keep descriptions unique — duplicates from Excel are ignored by description.
        </div>
      </div>
    </Section>
  );
}
