# ---
# jupyter:
#   jupytext:
#     text_representation:
#       extension: .py
#       format_name: percent
#       format_version: '1.3'
#       jupytext_version: 1.17.0
#   kernelspec:
#     display_name: Python 3 (ipykernel)
#     language: python
#     name: python3
# ---

# %% [markdown]
# # Model reporting
#
# Here we check the reporting of a given model.

# %% [markdown]
# ## Imports

# %%
import textwrap
from pathlib import Path

import pandas as pd
from gcages.cmip7_scenariomip.pre_processing import (
    get_required_model_region_index_input,
    get_required_world_index_input,
)
from gcages.completeness import get_missing_levels
from pandas_openscm.io import load_timeseries_csv

from constants import INDEX_COLUMS, RUN_ID, SCENARIO_INPUT_PATH

# %% [markdown]
# ## Set up

# %%
output_dir = Path(RUN_ID)
output_dir.mkdir(exist_ok=True, parents=True)
output_dir

# %%
pd.set_option("display.max_colwidth", None)

# %% [markdown]
# ## Load data

# %% [markdown]
# ### Scenarios

# %%
model_raw = load_timeseries_csv(
    SCENARIO_INPUT_PATH, index_columns=INDEX_COLUMS, out_column_type=int
)

if model_raw.empty:
    raise AssertionError

model_raw

# %%
model_l = model_raw.pix.unique("model")
if len(model_l) > 1:
    msg = f"This notebook is built to work on one model at a time. Received: {model_l}"
    raise AssertionError(msg)

model = model_l[0]
model

# %% [markdown]
# ## Check completeness

# %% [markdown]
# Extract the model data, keeping:
#
# - only reported timesteps
# - only data from 2015 onwards (we don't care about data before this)
# - only data up to 2100 (while reporting is still weird for data post 2100)

# %%
model_df = model_raw.loc[:, 2015:2100].dropna(how="all", axis="columns")
if model_df.empty:
    raise AssertionError
# model_df

# %% [markdown]
# ### Figure out the model-specific regions

# %%
model_regions = [
    r for r in model_df.pix.unique("region") if r.startswith(model.split(" ")[0])
]
if not model_regions:
    raise AssertionError
# model_regions

# %%
missing_world = get_missing_levels(
    model_df.index, get_required_world_index_input(), unit_col="unit"
)
if missing_world.empty:
    print("Nothing missing at the World level")

else:
    missing_world_df = missing_world.to_frame(index=False)
    missing_world_df.to_csv(output_dir / "missing-world.csv", index=False)

    print("The following timeseries are missing at the World level")
    display(missing_world_df)  # noqa: F821

# %%
model_region_missing = get_missing_levels(
    model_df.index,
    get_required_model_region_index_input(model_regions),
    unit_col="unit",
)

if model_region_missing.empty:
    print("Nothing missing at the regional level")

else:
    model_region_missing_df = model_region_missing.to_frame(index=False)
    model_region_missing_df.to_csv(output_dir / "missing-model-region.csv", index=False)

    print("The following timeseries are missing at the model region level")
    display(model_region_missing_df)  # noqa: F821

# %%
if not model_region_missing.empty:
    model_region_missing_variables = model_region_missing_df["variable"].unique()
    all_regions_missing_the_same = (
        model_region_missing_df.groupby("region")["variable"]
        .apply(lambda x: set(x) == set(model_region_missing_variables))
        .all()
    )

    # Slightly slow way to do this, but ok
    missing_by_region = model_region_missing_df.groupby("region")["variable"].apply(
        lambda x: x.values
    )
    missing_in_all_regions = set(missing_by_region.iloc[0])
    for mr in missing_by_region:
        missing_in_all_regions = missing_in_all_regions.intersection(set(mr))

    print("Missing in all regions")
    print("======================")
    print()
    print(textwrap.indent("\n".join(sorted(missing_in_all_regions)), prefix="- "))
    print()

    if all_regions_missing_the_same:
        print("All regions are missing the same variables")

    else:
        print("Missing for specific regions")
        print("============================")
        for region, mr in missing_by_region.items():
            region_missing_specific = set(mr) - missing_in_all_regions
            print()
            print(region)
            if region_missing_specific:
                print(
                    textwrap.indent(
                        "\n".join(sorted(region_missing_specific)), prefix="- "
                    )
                )
            else:
                print("* Nothing missing beyond what is missing in all regions")
