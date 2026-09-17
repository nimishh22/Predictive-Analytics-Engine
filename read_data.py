from pathlib import Path

import pandas as pd

from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score

DATA_FILE = Path(__file__).resolve().parent / "results.csv"
df = pd.read_csv(DATA_FILE)
important = [
    'FIFA World Cup',
    'FIFA World Cup qualification',
    'UEFA Euro',
    'UEFA Euro qualification',
    'Copa América',
    'AFC Asian Cup',
    'African Cup of Nations',
    'Confederations Cup',
    'Friendly'
]

df_filtered = df[df["tournament"].isin(important)].copy()
df_filtered["date"] = pd.to_datetime(df_filtered["date"])
df_filtered = df_filtered[df_filtered["date"].dt.year >= 2014]
df_filtered = df_filtered.sort_values("date")
#print(df_filtered.shape)
#print(df_filtered.head(10))
#print(df_filtered["tournament"].value_counts())

def get_result(row):
    if row["home_score"] > row["away_score"]:
        return 1
    elif row['home_score'] < row["away_score"]:
        return -1
    else:
        return 0
    
df_filtered["result"] = df_filtered.apply(get_result, axis=1)
#print(df_filtered[["home_team", "away_team", "home_score", "away_score", "result"]].head(10))


def get_recent_form(team, match_date):
    match_date = pd.to_datetime(match_date)
    team_matches = df_filtered[
        (
            (df_filtered["home_team"] == team)
            | (df_filtered["away_team"] == team)
        )
        & (df_filtered["date"] < match_date)
    ]
   
    recent_matches = team_matches.tail(10)
    n = len(recent_matches)
    
    if n == 0:
         return 0.5
    points = 0


    for _, row in recent_matches.iterrows():
        if row["home_team"] ==  team:
            team_score = row["home_score"]
            opponent_score = row["away_score"]
        else:
            team_score = row["away_score"]
            opponent_score = row["home_score"]

        if team_score > opponent_score:
            points += 3
        elif team_score == opponent_score:
            points += 1
    return points / (n*3)

home_forms = []
away_forms = []

for _, row in  df_filtered.iterrows():
    home_form = get_recent_form(
        row["home_team"] , 
        row["date"] 
    )
    away_form = get_recent_form(
        row["away_team"] ,
        row["date"]
    ) 

    home_forms.append(home_form)
    away_forms.append(away_form)

df_filtered["home_form"] = home_forms
df_filtered["away_form"] = away_forms

#print (df_filtered.iloc[3000:3010])

def average_goals_scored(team, match_date):
    match_date = pd.to_datetime(match_date)

    team_matches = df_filtered[
        (
            (df_filtered["home_team"] == team)
            | (df_filtered["away_team"] == team)
        )
        & (df_filtered["date"] < match_date)
    ]
    recent_matches = team_matches.tail(10)
    n = len(recent_matches)
    if n == 0:
            return 0.0
    
    total_goals = 0

    for _, row in recent_matches.iterrows():
        if row["home_team"] == team:
            team_goals = row["home_score"]
        else:
            team_goals = row["away_score"]

        total_goals += team_goals

    return total_goals / n

#print(average_goals_scored("Argentina", "2026-4-7"))

def average_goals_conceded(team,match_date):
    match_date = pd.to_datetime(match_date)

    team_matches = df_filtered[

        (
            (df_filtered["home_team"] == team)
            | (df_filtered["away_team"] == team)
        )
        &(df_filtered["date"] < match_date)
    ]
    recent_matches = team_matches.tail(10)
    n = len(recent_matches)
    if n == 0:
        return 0.0
    
    total_goals = 0

    for _, row in recent_matches.iterrows():
        if row["home_team"] == team:
            goals_conceded = row["away_score"]
        else:
            goals_conceded = row["home_score"]

        total_goals += goals_conceded
    return total_goals / n

#print(average_goals_conceded("Brazil", "2022-11-20"))

 # Create average goals features

home_goals_scored = []
away_goals_scored = []

home_goals_conceded = []
away_goals_conceded = []

for _, row in df_filtered.iterrows():

    home_goals_scored.append(
        average_goals_scored(
            row["home_team"],
            row["date"]
        )
    )

    away_goals_scored.append(
        average_goals_scored(
            row["away_team"],
            row["date"]
        )
    )

    home_goals_conceded.append(
        average_goals_conceded(
            row["home_team"],
            row["date"]
        )
    )

    away_goals_conceded.append(
        average_goals_conceded(
            row["away_team"],
            row["date"]
        )
    )

elo_ratings = {}
home_elos = []
away_elos = []

def expected_score(team_rating, opponent_rating):
    return 1 / ( 1 + 10 ** ((opponent_rating - team_rating) / 400))

def update_rating(rating, expected, actual):
    k = 20
    return rating + k * (actual - expected)


for _, row in df_filtered.iterrows():
    home_team = row["home_team"]
    away_team = row["away_team"]

    if home_team not in elo_ratings:
            elo_ratings[home_team] = 1500

    if away_team not in elo_ratings:
            elo_ratings[away_team] = 1500

    home_elo = elo_ratings[home_team]
    away_elo = elo_ratings[away_team]
    home_elos.append(home_elo)
    away_elos.append(away_elo)

    home_expected = expected_score(home_elo, away_elo)
    away_expected = expected_score(away_elo, home_elo)

    result = row["result"]
    if result == 1:
            home_actual = 1
            away_actual = 0
    elif result == 0:
            home_actual = 0.5
            away_actual = 0.5
    else:
            home_actual = 0
            away_actual = 1

    new_home_elo = update_rating(
     home_elo,
     home_expected,
     home_actual,
)

    new_away_elo = update_rating(
     away_elo,
     away_expected,
     away_actual,
)

    elo_ratings[home_team] = new_home_elo
    elo_ratings[away_team] = new_away_elo


df_filtered["home_elo"] = home_elos
df_filtered["away_elo"] = away_elos

df_filtered["home_avg_goals_scored"] = home_goals_scored
df_filtered["away_avg_goals_scored"] = away_goals_scored

df_filtered["home_avg_goals_conceded"] = home_goals_conceded
df_filtered["away_avg_goals_conceded"] = away_goals_conceded

tournament_dummies = pd.get_dummies(df_filtered["tournament"], dtype=int)
df_filtered = pd.concat([df_filtered, tournament_dummies], axis=1)
df_filtered = df_filtered.drop(columns=["tournament"])


features = [
    "home_form",
    "away_form",
    "home_avg_goals_scored",
    "away_avg_goals_scored",
    "home_avg_goals_conceded",
    "away_avg_goals_conceded",
    "neutral",
    "AFC Asian Cup",
    "African Cup of Nations",
    "Confederations Cup",
    "Copa América",
    "FIFA World Cup",
    "FIFA World Cup qualification",
    "Friendly",
    "UEFA Euro",
    "UEFA Euro qualification",
    "home_elo",
    "away_elo"
]
print(df_filtered.columns.to_list())
X = df_filtered[features]

y = df_filtered["result"]

print(X.head())
print(y.head())

X_train, X_test, y_train, y_test = train_test_split(
    X,
    y,
    test_size=0.2,
    random_state=42
)
model = RandomForestClassifier(
    n_estimators=100,
    random_state=42
)
model.fit(X_train, y_train)
predictions = model.predict(X_test)
accuracy = accuracy_score(y_test, predictions)
print(f"Accuracy: {accuracy:.2%}") 
