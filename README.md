# Predictive Intelligence Engine

A machine-learning system for probabilistic outcome prediction using historical data, statistical feature engineering, and ensemble learning.

> **Current application:** International football match prediction.

## Overview

The project builds a predictive pipeline from historical international match data. It engineers pre-match features and trains a Random Forest classifier to estimate match outcomes.

Current target classes:

- **1** — Home win
- **0** — Draw
- **-1** — Away win

## Current Features

- Recent team form from previous matches
- Average goals scored in recent matches
- Average goals conceded in recent matches
- Neutral-venue indicator
- Tournament context using one-hot encoding
- **Pre-match Elo ratings** calculated chronologically from previous results

## Model

The current model uses a `RandomForestClassifier` from scikit-learn with 100 decision trees.

### Accuracy Progress

| Version | Change | Accuracy |
|---|---|---:|
| V1 | Baseline feature set | **50.67%** |
| V2.1 | Historical feature handling fixes | **52.34%** |
| V2.2 | Added chronological pre-match Elo ratings | **54.64%** |

The **54.64% result is an intermediate benchmark from a random train/test split**, not the final evaluation of the system. A time-based evaluation is planned to test performance more realistically on future matches.

## Elo Rating System

The V2.2 pipeline maintains a separate Elo rating for each team while processing matches chronologically.

- Teams start at **1500 Elo**.
- The Elo value recorded for each match is the team's **pre-match** rating.
- Expected results are calculated using the standard Elo expected-score formula.
- Ratings are updated after each match using **K = 20**.
- Draws are represented using an actual score of **0.5** for both teams.

This prevents the match being predicted from influencing its own Elo feature.

## Tech Stack

- Python
- Pandas
- scikit-learn

## Roadmap

- [ ] Improve model evaluation with time-aware testing
- [ ] Improve recent-form features with weighting, streaks, and goal difference
- [ ] Add head-to-head features
- [ ] Add win/draw/loss probability predictions
- [ ] Compare multiple model architectures
- [ ] Build a user-facing prediction interface
- [ ] Deploy the application

## Project Status

**Version 2 — Feature engineering and model development**

The system is actively being developed. The current focus is improving the quality of pre-match features and establishing a robust time-based evaluation methodology before moving toward probability outputs and a user-facing interface.
