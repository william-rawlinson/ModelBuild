export function formatNumber(value, dp = 3) {
  if (value === null || value === undefined) return "—";
  if (Number.isNaN(value)) return "—";
  return Number(value).toFixed(dp);
}

export function formatCostGBP(value, dp = 2) {
  if (value === null || value === undefined) return "—";
  const n = Number(value);
  if (Number.isNaN(n)) return "—";
  const abs = Math.abs(n);
  // simple GBP formatting without Intl for now (you can upgrade later)
  const sign = n < 0 ? "-" : "";
  const whole = Math.floor(abs).toString().replace(/\B(?=(\d{3})+(?!\d))/g, ",");
  const frac = (abs - Math.floor(abs)).toFixed(dp).slice(1);
  return `${sign}£${whole}${frac}`;
}

export function formatMetric(value, kind) {
  if (value === null || value === undefined) return "—";
  const n = Number(value);
  if (Number.isNaN(n)) return "—";

  if (kind === "cost") return formatCostGBP(n);
  if (kind === "qaly") return formatNumber(n, 3);
  if (kind === "time_spent") return formatNumber(n, 3); // years
  return String(value);
}

export function isEffectivelyZero(value, tol = 1e-12) {
  if (value === null || value === undefined) return true;
  const n = Number(value);
  if (Number.isNaN(n)) return true;
  return Math.abs(n) <= tol;
}
