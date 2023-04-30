# Note that this takes about 7.5 minutes to run on my machine
import pandas as pd
from difflib import SequenceMatcher
from tqdm import tqdm


def similar(a, b):
    return round(SequenceMatcher(None, a, b).ratio(), 4)


def max_similar(df, b):
    df_temp = df.copy()

    df_temp["similarity"] = df_temp.apply(lambda row: similar(row["C"], b), axis=1)
    max_idx = df_temp["similarity"].idxmax()
    max_val = df_temp.loc[max_idx, "similarity"]
    return (max_val, max_idx)


# Reading the data; Triplets already split by project
print("reading data...")
all_phase2 = pd.read_json("../triplets/phase2.json", orient="index")

# Project Lists
phase2_projects = [
    "Chart",
    "Cli",
    "Closure",
    "Codec",
    "Collections",
    "Compress",
    "Csv",
    "Gson",
    "JacksonCore",
    "JacksonDatabind",
    "JacksonXml",
    "Jsoup",
    "JxPath",
    "Lang",
    "Math",
    "Mockito",
    "Time",
]

triplets_projects = [
    "commons-imaging-1.0-alpha3-src",
    "spark",
    "commons-lang3-3.12.0-src",
    "http-request",
    "commons-geometry-1.0-src",
    "springside4",
    "commons-jexl3-3.2.1-src",
    "joda-time",
    "async-http-client",
    "JSON-java",
    "bcel-6.5.0-src",
    "commons-weaver-2.0-src",
    "commons-numbers-1.0-src",
    "commons-collections4-4.4-src",
    "jsoup",
    "commons-jcs3-3.1-src",
    "commons-validator-1.7",
    "commons-net-3.8.0",
    "commons-beanutils-1.9.4",
    "commons-pool2-2.11.1-src",
    "commons-rng-1.4-src",
    "commons-configuration2-2.8.0-src",
    "commons-vfs-2.9.0",
    "scribejava",
    "commons-dbutils-1.7",
]

# Common Elements based on my eye-balling
common_projects_df = pd.DataFrame(
    {
        "phase2": ["Jsoup", "Lang", "Math", "Time", "Collections"],
        "triplets": [
            "jsoup",
            "commons-lang3-3.12.0-src",
            "commons-numbers-1.0-src",
            "joda-time",
            "commons-collections4-4.4-src",
        ],
    }
)

# Driver Code
print("calculating similarity...")
for i in tqdm(range(len(common_projects_df))):
    phase2_name = common_projects_df.loc[i, "phase2"]
    triplets_name = common_projects_df.loc[i, "triplets"]
    with pd.option_context("mode.chained_assignment", None):
        triplets_df = pd.read_json(
            f"../triplets/project_json/triplets_{triplets_name}.json", orient="index"
        )
        phase2_df = all_phase2[all_phase2["project"] == phase2_name]
        triplets_df.drop_duplicates(subset=["C"], inplace=True)
        phase2_df.drop_duplicates(subset=["C"], inplace=True)

        common_projects_df.loc[i, "triplets_unique_count"] = len(triplets_df)
        common_projects_df.loc[i, "phase2_unique_count"] = len(phase2_df)

        phase2_df["similarity"] = phase2_df.apply(
            lambda row: max_similar(triplets_df, row["C"]), axis=1
        )
        phase2_df[["sim_score", "triplets_index"]] = pd.DataFrame(
            phase2_df["similarity"].tolist(), index=phase2_df.index
        )
        phase2_df.index.rename("phase2_index", inplace=True)
        phase2_df.drop(columns=["similarity"], inplace=True)
        phase2_df.sort_values(by=["sim_score"], ascending=False, inplace=True)

        phase2_df[["sim_score", "triplets_index"]].to_csv(
            f"./similarity_{phase2_name}.csv"
        )

common_projects_df = common_projects_df.astype(
    {"triplets_unique_count": "int32", "phase2_unique_count": "int32"}
)
common_projects_df.to_csv("./similarity_unique_mut.csv", index=False)
