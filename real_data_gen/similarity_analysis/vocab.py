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
all_phase2 = pd.read_json("../triplets/phase2.json").T

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
common_projects = {
    ("Jsoup", "jsoup"): (),
    ("Lang", "commons-lang3-3.12.0-src"): (),
    ("Math", "commons-numbers-1.0-src"): (),
    ("Time", "joda-time"): (),
    ("Collections", "commons-collections4-4.4-src"): (),
    ("Time", "joda-time"): (),
}

# Driver Code
print("calculating similarity...")
for project in tqdm(common_projects):
    with pd.option_context("mode.chained_assignment", None):
        project_triplets = pd.read_json(f"../triplets/project_json/triplets_{project[1]}.json").T
        project_phase2 = all_phase2[all_phase2["project"] == project[0]]
        project_triplets.drop_duplicates(subset=["C"], inplace=True)
        project_phase2.drop_duplicates(subset=["C"], inplace=True)

        project_phase2["similarity"] = project_phase2.apply(
            lambda row: max_similar(project_triplets, row["C"]), axis=1
        )
        project_phase2[["sim_score", "triplets_index"]] = pd.DataFrame(
            project_phase2["similarity"].tolist(), index=project_phase2.index
        )
        project_phase2.index.rename("phase2_index", inplace=True)
        project_phase2.drop(columns=["similarity"], inplace=True)
        project_phase2.sort_values(by=["sim_score"], ascending=False, inplace=True)

        common_projects[project] = (project_phase2, project_triplets)

# Saving the results
for project in common_projects:
    common_projects[project][0][["sim_score", "triplets_index"]].to_csv(
        f"./similarity_{project[0]}.csv"
    )
