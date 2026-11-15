import openpyxl
from datetime import datetime
import os

class ExcelManager:
    def __init__(self, file_path="CricketData.xlsx"):
        self.file_path = file_path
        self.ensure_excel_structure()

    def ensure_excel_structure(self):
        if not os.path.exists(self.file_path):
            wb = openpyxl.Workbook()
            ws_players = wb.active
            ws_players.title = "PlayerList"
            ws_players.append(["Team A Name", "Team Name", "Player Name (Team A)", "Team B Name", "Player Name (Team B)", "", "", "Team A Logo", "Team B Logo"])
            
            ws_stats = wb.create_sheet("PlayerStats")
            ws_stats.append(["Player Name", "Matches", "Runs", "SR", "50s", "100s", "", "", "Team Logo"])
            
            ws_5w = wb.create_sheet("BOWLER5FER")
            ws_5w.append(["Date", "Bowler Name", "Overs", "Wickets", "Runs", "Maidens", "Economy"])
            
            wb.save(self.file_path)

    def get_team_players(self, team_col):
        wb = openpyxl.load_workbook(self.file_path)
        ws = wb["PlayerList"]
        players = []
        for row in ws.iter_rows(min_row=2, min_col=team_col, max_col=team_col, values_only=True):
            if row[0]:
                players.append(str(row[0]).strip())
        return players

    def get_logos(self):
        wb = openpyxl.load_workbook(self.file_path)
        ws = wb["PlayerList"]
        logo_a = ws["H2"].value or ""
        logo_b = ws["I2"].value or ""
        return logo_a, logo_b

    def get_player_stats(self, player_name):
        wb = openpyxl.load_workbook(self.file_path)
        ws = wb["PlayerStats"]
        for row in ws.iter_rows(min_row=2, values_only=True):
            if row[0] and str(row[0]).strip().lower() == player_name.strip().lower():
                return {
                    "matches": row[1] or 0,
                    "runs": row[2] or 0,
                    "sr": row[3] or 0.0,
                    "50s": row[4] or 0,
                    "100s": row[5] or 0
                }
        return {"matches": 0, "runs": 0, "sr": 0.0, "50s": 0, "100s": 0}

    def save_5fer(self, bowler_name, overs, wkts, runs, maidens, eco):
        wb = openpyxl.load_workbook(self.file_path)
        ws = wb["BOWLER5FER"]
        now_str = datetime.now().strftime("%d-%m-%Y %H:%M:%S")
        ws.append([now_str, bowler_name, str(overs), int(wkts), int(runs), int(maidens), float(eco)])
        wb.save(self.file_path)
