# %%
import re
import pandas as pd
import matplotlib.pyplot as plt
from sodapy import Socrata
from datetime import datetime

# Create Socrata client
client = Socrata("data.pa.gov", None)
results = client.get("mcba-yywm", limit=50000)
application_in = pd.DataFrame.from_records(results)

# Show basic info
print(application_in.head())
print(f"Total rows pulled: {len(application_in)}")

# %%
# Separate invalid and valid data
invalid_data = application_in[application_in.isnull().any(axis=1)].copy()
application_in = application_in.dropna()

print(f"Valid rows: {len(application_in)}, Invalid rows: {len(invalid_data)}")

# %%
# Convert 'senate' column to snake_case
def to_snake_case(value):
    if isinstance(value, str):
        return re.sub(r'\W+', '_', value.strip().lower())
    return value

application_in['senate'] = application_in['senate'].apply(to_snake_case)

# %%
# Extract year of birth
application_in['yr_born'] = pd.to_datetime(
    application_in['dateofbirth'], errors='coerce'
).dt.year.astype('Int64')

# Reorder columns: move 'yr_born' right after 'dateofbirth'
cols = list(application_in.columns)
dob_index = cols.index('dateofbirth')
cols.insert(dob_index + 1, cols.pop(cols.index('yr_born')))
application_in = application_in[cols]

# %%
# Calculate age as of 2020 election day
application_in['dateofbirth'] = pd.to_datetime(
    application_in['dateofbirth'], errors='coerce'
)
election_day = datetime(2020, 11, 3)
application_in['age'] = (
    election_day.year - application_in['dateofbirth'].dt.year
).astype('Int64')

# Group by party
age_party_summary = application_in.groupby('party')['age'].agg(
    ['count', 'mean', 'median']
).sort_values(by='count', ascending=False)
print(age_party_summary)

# # %%
# # Plot age & party trends (top 5)
# top5 = application_in.groupby('party')['age'].agg(
#     ['count', 'mean', 'median']
# ).sort_values(by='count', ascending=False).head(5)

# fig, ax1 = plt.subplots(figsize=(10, 6))

# ax1.bar(top5.index, top5['count'], alpha=0.6, label='Count', color='skyblue')
# ax1.set_ylabel('Vote-by-Mail Requests', color='blue')
# ax1.tick_params(axis='y', labelcolor='blue')
# ax1.set_title(
#     'Top 5 Parties by Vote-by-Mail Requests\nwith Average and Median Age'
# )

# ax2 = ax1.twinx()
# ax2.plot(top5.index, top5['mean'], marker='o', color='green', label='Mean Age')
# ax2.plot(top5.index, top5['median'], marker='s', color='orange', label='Median Age')
# ax2.set_ylabel('Age', color='black')

# lines, labels = ax1.get_legend_handles_labels()
# lines2, labels2 = ax2.get_legend_handles_labels()
# ax2.legend(lines + lines2, labels + labels2, loc='upper left')

# plt.tight_layout()
# plt.show()

print("## Key Observations:\n")
print("1. Democratic (D) applicants made up the largest share of vote-by-mail requests (26,508), with a mean age of ~54.")
print("   • This suggests high engagement among middle-aged Democrats.\n")
print("2. Republican (R) applicants had the second highest count (9,687), with a higher average age (~61) than Democrats.")
print("   • Suggests older Republican voters used mail voting, possibly due to health/safety concerns.\n")
print("3. Non-affiliated (NF) voters had a substantial count (3,261) with a younger average age (~46).")
print("   • Indicates younger independents were also engaging in vote-by-mail, possibly due to flexibility or accessibility.\n")
print("4. Smaller parties (e.g., Green (GR), Libertarian (LN)) show lower volumes and generally younger median ages,")
print("   • which may reflect smaller, younger voter bases.")

# %%
# Calculate application-to-return latency
application_in['appissuedate'] = pd.to_datetime(
    application_in['appissuedate'], errors='coerce'
)
application_in['ballotreturneddate'] = pd.to_datetime(
    application_in['ballotreturneddate'], errors='coerce'
)
application_in['latency_days'] = (
    application_in['ballotreturneddate'] - application_in['appissuedate']
).dt.days

# Median latency by legislative district
median_latency_by_legislative = (
    application_in.groupby('legislative')['latency_days']
    .median()
    .dropna()
    .sort_index()
)

print(median_latency_by_legislative)

# %%
# Overall median latency
overall_median_latency = application_in['latency_days'].median()
print(f"Overall median latency: {overall_median_latency} days")

# %%
# Top congressional district
top_congressional = application_in['congressional'].value_counts().idxmax()
top_congressional_count = application_in['congressional'].value_counts().max()

print("The congressional district with the highest number of ballot requests is:")
print(f"{top_congressional} with {top_congressional_count} requests")