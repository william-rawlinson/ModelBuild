// src/utils/calculate.js
export function calculateCombinations(settings) {
  let total = 1;

  for (const setting of settings) {
    const unlockedOptions = setting.options.filter(opt => !opt.locked).length;
    if (unlockedOptions === 0) return 0; // No feasible combination
    total *= unlockedOptions;
  }

  return total;
}
