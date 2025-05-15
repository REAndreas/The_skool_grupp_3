from pathlib import Path 
import pandas as pd


data_path = Path(__file__).parent / "data"

df = pd.read_excel(data_path / "ek_1_utbet_statliga_medel_utbomr.xlsx")
