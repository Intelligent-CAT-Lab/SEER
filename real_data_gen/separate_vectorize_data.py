import os
import pandas as pd
from tqdm import tqdm
import sys

from json_to_h5 import json_to_h5

if __name__ == "__main__":
    comment_types = ["no_comments", "comments", "added_comments"]
    # Expect this to take ~15 minutes to run
    for comment_type in tqdm(comment_types, desc="comment versions"):

        json_to_h5(
            type="test",
            fold=0,
            model="JointEmbedder",
            comment_type=comment_type,
        )
        
