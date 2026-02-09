import pandas as pd
import os
import unicodedata

def normalize_name(name):
    """Turns 'Mbappé' or ' Kylian ' into 'mbappe' or 'kylian'"""
    if not isinstance(name, str): 
        return ""
    # Remove accents, convert to lowercase, and remove extra spaces
    normalized = ''.join(c for c in unicodedata.normalize('NFD', name)
                        if unicodedata.category(c) != 'Mn').lower().strip()
    return normalized

class LaLigaDataManager:
    def __init__(self, player_path, match_path):
        self.player_path = player_path
        self.match_path = match_path

    def get_cleaned_players(self):
        print(f"--- Loading Player Data: {self.player_path} ---")
        try:
            if self.player_path.endswith('.xlsx'):
                df = pd.read_excel(self.player_path, skiprows=1, engine='openpyxl')
            else:
                df = pd.read_csv(self.player_path, skiprows=1, encoding='latin1')
        except Exception as e:
            print(f"ERROR LOADING FILE: {e}")
            return pd.DataFrame()

        # Clean Rows: Remove header repetitions and empty player rows
        df = df[df['Player'] != 'Player'].dropna(subset=['Player'])
        
        # Create the search column for the radar chart comparison
        df['search_name'] = df['Player'].apply(normalize_name)

        # Flexible Renaming (handles .1, _1, or _Per90 variations from FBRef)
        new_cols = {}
        for col in df.columns:
            if 'Gls' in col and ('.1' in col or '_1' in col): new_cols[col] = 'Gls_Per90'
            if 'Ast' in col and ('.1' in col or '_1' in col): new_cols[col] = 'Ast_Per90'
            if col == 'G+A': new_cols[col] = 'G_plus_A'
            if 'G+A' in col and ('.1' in col or '_1' in col): new_cols[col] = 'G_plus_A_Per90'
            # Look for Possession column if it's named something like 'Poss' or 'Poss_percentage'
            if 'Poss' in col: new_cols[col] = 'Poss'
        
        df = df.rename(columns=new_cols)

        # Convert numbers: Vital for Recharts to render correctly
        # We added 'Poss' to this list to ensure the heatmap and match comparison work
        numeric = ['Gls', 'Ast', 'Min', 'Gls_Per90', 'Ast_Per90', 'MP', 'Starts', 'Poss']
        for col in numeric:
            if col in df.columns:
                df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0)
        
        print(f"✅ Data Engine Ready. {len(df)} players loaded.")
        return df

    def get_cleaned_matches(self):
        """Loads match data from CSV and standardizes date formats."""
        try:
            df = pd.read_csv(self.match_path)
            # handle common Date format variations
            df['Date'] = pd.to_datetime(df['Date'], dayfirst=True, errors='coerce')
            return df
        except Exception as e:
            print(f"ERROR LOADING MATCHES: {e}")
            return pd.DataFrame()