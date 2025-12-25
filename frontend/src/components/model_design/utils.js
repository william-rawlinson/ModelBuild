export function normalizeName(s) {
  return s.trim().replace(/\s+/g, " ");
}

export const TIME_UNITS = [
  { value: "days", label: "Days" },
  { value: "weeks", label: "Weeks" },
  { value: "months", label: "Months" },
  { value: "years", label: "Years" },
];
