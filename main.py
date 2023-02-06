#!/usr/bin/env python3
import os.path
from collections import Counter
from sys import argv

import pandas as pd

if not os.path.isfile("table.csv"):
    #
    # Read official wordlist
    #
    df = pd.read_csv("La.csv")

    #
    # Calculate relevance scores using this formula:
    # score = sum of unique letter frequencies x number of words the letter
    # appears in
    #
    wordlist = df["WORD"].tolist()
    letter_frequencies = Counter("".join(wordlist))
    letter_counts = {it: 0 for it in letter_frequencies.keys()}
    for i in range(len(df["WORD"])):
        for it in set(df["WORD"].iloc[i]):
            letter_counts[it] += 1
    df["SCORE"] = 0
    for i in range(len(df["WORD"])):
        df["SCORE"].iloc[i] = sum(
            [
                letter_frequencies[it] * letter_counts[it]
                for it in set(df["WORD"].iloc[i])
            ]
        )
    df = df.sort_values(by="SCORE", ascending=False)
    df.to_csv("table.csv", index=False)

#
# Read words
#
df = pd.read_csv("table.csv")

#
# Read parameters
#
if len(argv) > 1:
    excluded_letters = "|".join(list(argv[1]))
    included_letters = "".join(list(argv[2]))
    included_letters = r"^{}".format(
        "".join("(?=.*{})".format(l) for l in included_letters)
    )
    excluded_partial_matches = argv[3]
    if "@" in excluded_partial_matches:
        excluded_partial_matches = excluded_partial_matches.split("@")
    else:
        excluded_partial_matches = [excluded_partial_matches]
    partial_match = argv[4]

    #
    # Filter for Excluded, Included and Partial Matches
    #
    df = df[df["WORD"].str.contains(excluded_letters) == False]
    df = df[df["WORD"].str.contains(included_letters) == True]
    for excluded_partial_match in excluded_partial_matches:
        for i in range(len(excluded_partial_match)):
            if excluded_partial_match[i] != ".":
                mask = "....."
                mask = mask[0:i] + excluded_partial_match[i] + mask[i + 1 :]
                df = df[df["WORD"].str.contains(mask) == False]
    df = df[df["WORD"].str.contains(partial_match) == True]

#
# Select highest ranking words and print the selection
#
df["SCORE"] /= float(max(df["SCORE"]))
df = df.sort_values(by=["SCORE"], ascending=False)
df = df.head(7)[["WORD", "SCORE"]]
print(df.to_string(index=False))
