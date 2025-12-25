DUMMY_MODEL_SPEC_1 = """Decision Problem
Decision problem statement
The aim of the analysis is to investigate whether VBT (anterior vertebral body tethering) is cost-effective as a first-choice surgical treatment option for pediatric patients with moderate to severe idiopathic scoiliosis who have failed nonoperative management, from a US perspective. The analysis should compare VBT to spinal fusion from the perspective of the US integrated healthcare delivery system (IDS).
Time horizon, cycle length, and discounting
15-year time-horizon, 3-month cycle length. Annual discounting of costs and effects of 3%.
Treatment strategies
Intervention: VBT, comparator: spinal fusion.
Health states
Patients enter the model in the spinal fusion or VBT index procedure health state. Devise health states based on the transitions described. 
Transition probabilities
Patients enter the model in the index spinal fusion or VBT index procedure health state depending on treatment arm. From this state, patients transition to the postoperative health states. The postoperative VBT health state represents patients who have had an index VBT operation. In the postoperative VBT health state patients who received VBT can experience VBT revision or an index fusion procedure. Once a patient has experienced an index fusion procedure they move to the postoperative index fusion health state. From here, they may experience up to two total revisions (modelled by two further fusion revision health states, with specific post operative states following these). If a patient in the postoperative state for the second fusion revision requires a further revision, they move to the absorbing ineligible fusion state. 
Costs
Index procedure costs
See provided data. For first index procedures, should be upon entry to the model. 
Revision procedure costs
See provided data



Utilities
Health state utilities
See provided data."""


DUMMY_MODEL_SPEC_2 = """Decision Problem
Decision problem statement
A cost-utility Markov analysis from a UK NHS and personal social services perspective. The population entering the model is people who have been using benzodiazepine for over 3 months and are unable to quit their usage by themselves.
Time horizon, cycle length, and discounting
Discounting of 3.5% for costs and effects. The model should use a cycle length of 1 year and a time horizon of 50 years. 
Treatment strategies
The intervention is CBT + TO (group cognitive behavioral therapy plus tapering off).  There are two comparators: TOA (tapering off alone) and UC (usual care – defined as the continuation of standard therapy with benzodiazepines with no attempt to reduce or discontinue it). 
Health states
The model should use seven health states. ‘Abstinent’, ‘on benzodiazepines’, ‘hip fracture acute’, ‘post-hip fracture’, ‘dementia 1st year’,  ‘dementia long-term’, and ‘Death’. ‘Dementia 1st year’ is a 1-year tunnel state for the upfront impact of dementia diagnosis. ‘hip-fracture acute’ is a 1-year tunnel state for the upfront impact of a hip fracture. 
Patients enter the model in the ‘abstinent’ or ‘on benzodiazepine’ states based on the effectiveness of the treatments, defined by cessation probabilities (e.g., cessation means a patient enters the model in the abstinent state, otherwise they enter the model in the on-benzodiazepine state). The TOA cessation probability is given, cessation probabilities should be calculated using the cessation risk ratios for the other treatments. 
Transition probabilities
Abstinent patients have a risk of relapse (transition to ‘on benzodiazepines’) during the first two years. Afterwards they cannot relapse. Patients in the ‘on-benzodiazepines’ state cannot become abstinent. Relapse rates during the first two years differ between treatments (see provided datapoints).
Abstinent patients or patients on benzodiazepines can experience hip fracture or dementia, if this happens, they immediately stop taking benzodiazepines (if they were) and cannot relapse. All patients that experience a hip fracture pass through the hip fracture acute health state, and then remain in the post-hip fracture state for the rest of the model time horizon (an absorbing state). All patients that experience dementia pass through the dementia 1st year health state, and then remain in the dementia long-term state for the rest of the model time horizon (an absorbing state). 
Hip fracture annual probabilities are provided for women and men by age-group.
Patients can transition to the death state (an absorbing state) from any health state. Baseline mortality should be determined using the provided lifetable data. Relative effects are provided for the dementia and hip fracture health states, which have higher mortality. 
Costs
Falls and hip fracture costs
Falls can occur in any health state. A fall rate per person per year is provided for men and women over 65, as well as age-specific incident rate ratios. For patients under 65, make appropriate assumptions based on the data. Data to calculate fall costs based on the probability of different fall consequences is provided. Assume hip fractures can only be the consequence of a fall, so the number of hip fractures in each cycle should be subtracted from the number of falls to avoid double counting.
An annual hip fracture cost is provided for the acute state and post hip-fracture state.
Intervention and comparator costs
The cost for each treatment should be applied once in the first model cycle (as treatment ends at the start of the model). Usual care is assumed to have no cost. The cost of CBT + TO should be the sum of the cost of CBT and the cost of TO provided.
Benzodiazepines costs
The cost of benzodiazepines should be calculated as a weighted average based on the provided daily mg, cost per mg, and proportion taking datapoints.
Dementia costs
Separate annual costs are provided for each classification of dementia (mild, moderate, sever) and for each of the first year (Dementia 1st year) and subsequent years (Dementia long term). 
Age-dependent annual costs for the health states should be calculated as a weighted average over mild, moderate, and severe dementia, based on the proportion falling into each classification within each age category.
Utilities

Health state utilities
The same baseline health state utility is used for all health states aside from the dementia health states. In the first 2 cycles, treatment dependent baseline utilities are used. In subsequent cycles, all patients (in whatever treatment arm) have the UC (usual care) baseline utility.
For the dementia health states, age-dependent baseline utility should be calculated based on the caregiver-proxy utilities as a weighted average over mild, moderate, and severe dementia, based on the proportion falling into each classification within each age category. 
Baseline utilities for every health state should be adjusted by age. To do this, use the Ara and Brazier algorithm provided below, where ‘male’ is 1 for males and 0 for females. First, calculate the ratio of the baseline utility for a health state to the UK general population utility (at the model’s starting age). Then, the age-dependent utilities for that health state can be calculated by multiplying that same ratio against the UK general population utilities for other ages. 
UK general population utility = 0.9508566 + 0.0212126*male - 0.0002587*age - 0.0000332*ageˆ2

Falls and hip fracture disutility
The incidence of falls is dealt with in the ‘fall and hip fracture costs’ section. Some of the fall consequences are associated with a one-cycle disutility.
Hip fracture disutilities should be modelled based on health state membership. Data has been provided for an annual disutility in the acute hip fracture state, and a permanent recurring annual disutility for the post-hip fracture state.
"""

