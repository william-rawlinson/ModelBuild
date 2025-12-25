In terms of what should come from the front end

- Intervention - needs to be ignored in datapoints -> parameters
- Comparators - needs to be ignored in datapoints -> parameters
- WTP threshold - needs to be ignored in datapoints -> parameters
- Discounting rates (ANNUAL) - needs to be ignored in datapoints -> parameters

These may need to be modified / may not be immediately obvious
- Time horizon
- Cycle length
- Health states

How will time horizon and cycle length work?
-   User may provide them in available parameters / model spec
-   Need to look at them, decide if they are ok
  - If OK, can keep those parameters
  - If not OK or missing, need to change the parameters / add them
- What about keeping track of unit? 

Run markov requires
- N cycles
- Discount rates annual (that's ok can get through front end)
- Needs to be able to convert cycle length to years and time horizon
needs to have an associated unit

Options - always define cycle length in terms of years, keep as a fraction?
+ ask for it to be named cycle_length_years, and time_horizon_years



