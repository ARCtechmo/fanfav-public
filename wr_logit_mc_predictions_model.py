
import pandas as pd
import matplotlib.pyplot as plt
from datetime import datetime

# Required libraries: fuzzywuzzy, fpdf
# Install via: pip install fuzzywuzzy python-Levenshtein fpdf

from fuzzywuzzy import process
from fpdf import FPDF

# === Utilities ===
def get_current_week():
    today = datetime.now()
    week = today.isocalendar().week
    return min(max(1, week - 35), 18)  # crude adjustment for NFL season

def get_year_range(current_year, current_week):
    return list(range(2017, current_year + (1 if current_week >= 1 else 0)))

# === Column group definitions ===
column_groups = {
    "fpts": ["fpts", "value_ratio_dk", "value_ratio_fd"],
    "touches_athleticism": ["targets", "receptions", "receiving_yards", "receiving_yards_after_catch"],
    "efficiency": ["catch_percentage", "target_share", "receiving_air_yards"],
    "separation": ["avg_cushion", "avg_separation"],
    "zscore_fpts": ["fpts_zscore", "value_ratio_dk_zscore", "value_ratio_fd_zscore"],
    "rolling_avgs": ["fpts_3wk_avg", "receptions_3wk_avg", "targets_3wk_avg"],
}

# === DASHBOARD ===
def run_player_dashboard_summary(logit_df, mc_dict):
    print("\n=== Player Performance Dashboard ===")
    print("Type 'exit' at any prompt to cancel.\n")
    current_year = datetime.now().year
    current_week = get_current_week()
    years = get_year_range(current_year, current_week)
    default_season = years[-1] if 1 <= current_week <= 18 else years[-1]
    default_week = current_week if 1 <= current_week <= 18 else 18

    player_input = input("Enter player name: ").strip().lower()
    if player_input == "exit":
        return
    all_names = logit_df['name'].dropna().unique()
    best_match, score = process.extractOne(player_input, all_names)
    if score < 80:
        print(f"❌ No good match found. Closest was '{best_match}' (score: {score})")
        return
    matched_name = best_match
    print(f"🔍 Best match: {matched_name} (score: {score})")

    season_input = input(f"Enter season (default: {default_season}): ").strip()
    if season_input == "exit":
        return
    season = int(season_input) if season_input.isdigit() else default_season

    week_input = input(f"Enter week (default: {default_week}): ").strip()
    if week_input == "exit":
        return
    week = int(week_input) if week_input.isdigit() else default_week

    logit_row = logit_df[(logit_df['name'] == matched_name) & (logit_df['season'] == season) & (logit_df['week'] == week)]
    if logit_row.empty:
        print("❌ No logistic prediction found for that player and week.")
        return
    logit_row = logit_row.iloc[0]
    mc_summary = {}
    for key, df in mc_dict.items():
        df_player = df[(df['name'].str.lower() == matched_name.lower()) & (df['season'] == season)]
        mc_summary[key] = df_player.iloc[0] if not df_player.empty else None

    print("\n📊 === Player Dashboard Summary ===")
    print(f"Player: {matched_name} | Week: {week} | Season: {season}")
    print(f"DK Salary: ${int(logit_row['dk_salary'])}")
    print(f"Actual FPTS (Week {week}): {logit_row.get('fpts', '—')}")

    print("\n🔢 Logistic Regression Predictions:")
    def classify(prob, threshold=0.5):
        if prob >= 0.85: return f"{prob:.2f} 🔵 High"
        if prob >= threshold: return f"{prob:.2f} 🟡 Medium"
        return f"{prob:.2f} 🔴 Low"
    print(f" - P(Hit DK Value):     {classify(logit_row['pred_prob_value'])} — Predicted: {'✅' if logit_row['pred_class_value'] else '❌'}")
    print(f" - P(FPTS ≥ 10):        {classify(logit_row['pred_prob_fpts10'])} — Predicted: {'✅' if logit_row['pred_class_fpts10'] else '❌'}")
    print(f" - P(Elite Tier 85%):   {classify(logit_row['pred_prob_85pct'])} — Predicted: {'✅' if logit_row['pred_class_85pct'] else '❌'}")

    print("\n🔮 Monte Carlo Forecasts (Rest of Season):")
    for key in mc_dict.keys():
        mc_row = mc_summary[key]
        label = key.replace("monte_carlo_", "").upper()
        if mc_row is not None:
            print(f"\n--- {label} ---")
            print(f" Avg Hits:         {mc_row['avg_hits']:.2f}")
            print(f" Min–Max Hits:     {mc_row['min_hits']} – {mc_row['max_hits']}")
            print(f" Std Dev:          {mc_row['std_hits']:.2f}")
            print(f" P(Hit All Weeks): {mc_row['p_hit_all_weeks']:.2f}")
            print(f" P(Hit ≥ Half):    {mc_row['p_hit_half_or_more']:.2f}")
        else:
            print(f"\n--- {label} ---\nNo Monte Carlo data available.")

    print("\n✅ Summary Complete.\n")

# === LOOKUP TOOL ===
def run_prediction_lookup_ui_menu(logit_df, mc_dict):
    print("\n=== Logit + Monte Carlo Prediction Lookup ===")
    print("Type 'exit' at any prompt to quit.\n")
    while True:
        name_input = input("Enter player name: ").strip().lower()
        if name_input == "exit":
            break
        all_names = logit_df['name'].dropna().unique()
        best_match, score = process.extractOne(name_input, all_names)
        if score < 80:
            print(f"❌ No good match found. Closest was '{best_match}' (score: {score}).")
            continue
        matched_name = best_match
        print(f"🔍 Using best match: {matched_name} (score: {score})")
        season_input = input("Enter season (e.g., 2024): ").strip()
        if season_input == "exit":
            break
        if not season_input.isdigit():
            print("⚠️ Invalid season.")
            continue
        season_input = int(season_input)
        mode_input = input("Select mode ('logit', 'mc', or 'all'): ").strip().lower()
        if mode_input == "exit":
            break
        if mode_input not in ["logit", "mc", "all"]:
            print("⚠️ Invalid mode.")
            continue

        player_logit = logit_df[(logit_df['name'] == matched_name) & (logit_df['season'] == season_input)]
        player_mc = {key: df[(df['name'].str.lower() == matched_name.lower()) & (df['season'] == season_input)] for key, df in mc_dict.items()}

        if player_logit.empty and all(df.empty for df in player_mc.values()):
            print("❌ No matching records found.\n")
            continue

        if mode_input in ["logit", "all"] and not player_logit.empty:
            print("\n--- Logistic Regression Prediction ---")
            print(player_logit)
        if mode_input in ["mc", "all"]:
            print("\n🔮 Monte Carlo Forecasts ---")
            for key, df in player_mc.items():
                if not df.empty:
                    print(f"\n📊 {key.replace('_', ' ').title()}")
                    print(df)
                else:
                    print(f"⚠️ No data for {key}.")
        print("\n✓ Lookup complete.\n")

# === MENU ===
def run_main_nfl_model_tools_menu(logit_df, mc_dict):
    while True:
        print("\n=== Main NFL Model Tools Menu ===")
        print("1. 🧠 Player Performance Dashboard")
        print("2. 🔍 Lookup Predictions (Logit + Monte Carlo)")
        print("0. ❌ Exit")
        choice = input("Enter your choice: ").strip()
        if choice == "1":
            run_player_dashboard_summary(logit_df, mc_dict)
        elif choice == "2":
            run_prediction_lookup_ui_menu(logit_df, mc_dict)
        elif choice == "0":
            print("👋 Exiting. See you next time!")
            break
        else:
            print("⚠️ Invalid option. Enter 0, 1, or 2.")
