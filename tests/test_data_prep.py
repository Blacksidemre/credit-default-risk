import pandas as pd

from src.data_prep import add_features, clean_data


def test_feature_engineering_creates_required_columns():
    row = {
        "LIMIT_BAL": 100000, "SEX": 2, "EDUCATION": 5, "MARRIAGE": 0, "AGE": 35,
        "PAY_0": 0, "PAY_2": 0, "PAY_3": 0, "PAY_4": 0, "PAY_5": 0, "PAY_6": 0,
        **{f"BILL_AMT{i}": 1000 for i in range(1, 7)},
        **{f"PAY_AMT{i}": 100 for i in range(1, 7)},
    }
    df = clean_data(pd.DataFrame([row]), require_target=False)
    out = add_features(df)
    assert out.loc[0, "PAY_SUM"] == 600
    assert out.loc[0, "BILL_SUM"] == 6000
    assert out.loc[0, "EDUCATION"] == 4
    assert out.loc[0, "MARRIAGE"] == 3
    assert str(out.loc[0, "AGE_BIN"]) == "31-40"
