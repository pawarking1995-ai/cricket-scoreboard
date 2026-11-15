import sys
import os
import json
import copy
import pandas as pd
from datetime import datetime
from PyQt5.QtWidgets import (QApplication, QWidget, QLabel, QPushButton, 
                             QVBoxLayout, QHBoxLayout, QGridLayout, QLineEdit, 
                             QGroupBox, QComboBox, QScrollArea, QTableWidget, 
                             QTableWidgetItem, QHeaderView, QMessageBox, QFileDialog, QTabWidget, QInputDialog, QAbstractItemView)
from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtGui import QColor
import requests
from urllib.parse import quote

class SimpleCricketGUI(QWidget):
    def __init__(self):
        super().__init__()
        self.runs = 0
        self.wickets = 0
        self.overs = 0
        self.balls = 0
        self.extras = 0
        self.fours = 0
        self.sixes = 0
        self.squad_overlay_visible = False
        
        self.current_innings = 1
        self.first_innings_ended = False
        self.target_runs = 0
        self.match_ended = False

        self.is_super_over = False
        self.super_over_target = 0
        self.super_over_overlay_visible = False  

        self.t1_total_score = "0/0"
        self.t1_overs = "0.0"
        self.t1_extras = "0"
        self.fall_of_wickets_list = []

        self.logo_a_path = ""
        self.logo_b_path = ""

        self.striker_slot = 1  
        self.batting_stats_t1 = {}
        self.batting_stats_t2 = {}
        self.bowling_stats_t1 = {}
        self.bowling_stats_t2 = {}

        self.t1_bat_player_inputs = []
        self.t1_bowl_player_inputs = []
        self.t2_bat_player_inputs = []
        self.t2_bowl_player_inputs = []

        self.bat1_name = ""
        self.bat2_name = ""
        self.current_bowler_name = ""

        self.bat1_runs = 0
        self.bat1_balls = 0
        self.bat1_4s = 0
        self.bat1_6s = 0
        
        self.bat2_runs = 0
        self.bat2_balls = 0
        self.bat2_4s = 0
        self.bat2_6s = 0

        self.partnership_runs = 0
        self.partnership_balls = 0
        self.partnership_4s = 0
        self.partnership_6s = 0

        self.lw_player = ""
        self.lw_fielder = ""
        self.lw_bowler = ""
        self.lw_run = "0"
        self.lw_ball = "0"
        self.lw_outtype = ""
        
        self.bowler_balls = 0
        self.bowler_runs = 0
        self.bowler_wickets = 0
        self.bowler_maidens = 0
        self.over_runs_count = 0  
        
        self.last_bowler_name = ""
        self.over_completed_need_new_bowler = False
        self.this_over_balls = []

        self.team1_inputs = []
        self.team2_inputs = []

        self.points_table_data = {}
        self._points_second_innings_saved = False
        self._points_match_result_recorded = False
        self._undo_stack = []
        self._undo_limit = 50
        self.tournament_4s6s_data = {}
        self.tournament_4s6s_file = os.path.join(os.path.expanduser("~/Documents"), "tournament_4s6s_records.json")

        # Tournament Fours overlay counter (independent of individual match score).
        self.tournament_fours_count = 0
        self.tournament_fours_file = os.path.join(
            os.path.expanduser("~/Documents"), "tournament_fours_counter.json"
        )

        # Tournament Sixes overlay counter (independent of individual match score).
        self.tournament_sixes_count = 0
        self.tournament_sixes_file = os.path.join(
            os.path.expanduser("~/Documents"), "tournament_sixes_counter.json"
        )

        self.initUI()
        self.load_points_data_from_file()
        self.load_tournament_fours_counter()
        self.load_tournament_sixes_counter()

    def initUI(self):
        self.setWindowTitle("CRICKET SCOREBOARD MANAGER PRO - Detailed Auto-Save Excel")
        self.setGeometry(10, 10, 1480, 1000)

        main_master_layout = QVBoxLayout()

        self.main_tabs = QTabWidget()
        self.main_tabs.setStyleSheet("QTabBar::tab { font-size: 13px; font-weight: bold; padding: 8px 16px; background: #e0e0e0; color: #333; } QTabBar::tab:selected { background: #00bcd4; color: white; }")

        tab_live_scoring = QWidget()
        master_layout = QVBoxLayout()

        lay_header = QHBoxLayout()

        grp_1st_details = QGroupBox("1st Innings Details")
        grp_1st_details.setStyleSheet("QGroupBox { background-color: blue; color: white; font-weight: bold; border: 2px solid blue; }")
        lay_1st_details = QHBoxLayout()

        vbox_1st_tot = QVBoxLayout()
        vbox_1st_tot.addWidget(QLabel("<font color='white'><b>Total + WICKET</b></font>"))
        self.lbl_1st_score = QLineEdit("0/0")
        self.lbl_1st_score.setReadOnly(True)
        self.lbl_1st_score.setAlignment(Qt.AlignCenter)
        self.lbl_1st_score.setStyleSheet("background-color: white; color: black; font-size: 16px; font-weight: bold;")
        vbox_1st_tot.addWidget(self.lbl_1st_score)
        lay_1st_details.addLayout(vbox_1st_tot)

        vbox_1st_ov = QVBoxLayout()
        vbox_1st_ov.addWidget(QLabel("<font color='white'><b>OVER</b></font>"))
        self.lbl_1st_over = QLineEdit("0.0")
        self.lbl_1st_over.setReadOnly(True)
        self.lbl_1st_over.setAlignment(Qt.AlignCenter)
        self.lbl_1st_over.setStyleSheet("background-color: white; color: black; font-size: 16px; font-weight: bold;")
        vbox_1st_ov.addWidget(self.lbl_1st_over)
        lay_1st_details.addLayout(vbox_1st_ov)

        vbox_1st_ex = QVBoxLayout()
        vbox_1st_ex.addWidget(QLabel("<font color='white'><b>EXTRA</b></font>"))
        self.lbl_1st_extra = QLineEdit("0")
        self.lbl_1st_extra.setReadOnly(True)
        self.lbl_1st_extra.setAlignment(Qt.AlignCenter)
        self.lbl_1st_extra.setStyleSheet("background-color: white; color: black; font-size: 16px; font-weight: bold;")
        vbox_1st_ex.addWidget(self.lbl_1st_extra)
        lay_1st_details.addLayout(vbox_1st_ex)

        grp_1st_details.setLayout(lay_1st_details)
        lay_header.addWidget(grp_1st_details)

        grp_black_live = QGroupBox("Inning Details (LIVE)")
        grp_black_live.setStyleSheet("QGroupBox { background-color: black; color: white; font-weight: bold; border: 1px solid black; }")
        lay_black_live = QHBoxLayout()

        def make_black_field(label_text, default_val="0"):
            vbox = QVBoxLayout()
            lbl = QLabel(f"<font color='white'><b>{label_text}</b></font>")
            lbl.setAlignment(Qt.AlignCenter)
            vbox.addWidget(lbl)
            txt = QLineEdit(default_val)
            txt.setReadOnly(True)
            txt.setAlignment(Qt.AlignCenter)
            txt.setStyleSheet("background-color: white; color: black; font-size: 14px; font-weight: bold;")
            vbox.addWidget(txt)
            return vbox, txt

        v1, self.lbl_live_total = make_black_field("Total", "0")
        v2, self.lbl_live_wickets = make_black_field("Wickets", "0")
        v3, self.lbl_live_over = make_black_field("Over", "0.0")
        v4, self.lbl_live_crr = make_black_field("CRR", "0.00")
        v5, self.lbl_live_4s = make_black_field("4s", "0")
        v6, self.lbl_live_6s = make_black_field("6s", "0")
        v7, self.lbl_live_co = make_black_field("CO", "0.0")
        v8, self.lbl_live_extra = make_black_field("EXTRA", "0")

        for v in [v1, v2, v3, v4, v5, v6, v7, v8]:
            lay_black_live.addLayout(v)

        grp_black_live.setLayout(lay_black_live)
        lay_header.addWidget(grp_black_live)

        vbox_overs = QVBoxLayout()
        vbox_overs.addWidget(QLabel("<font color='red'><b>MATCH OVERS</b></font>"))
        self.txt_match_overs = QLineEdit("1")
        self.txt_match_overs.setAlignment(Qt.AlignCenter)
        self.txt_match_overs.setStyleSheet("background-color: white; color: red; font-size: 18px; font-weight: bold; border: 1px solid gray;")
        vbox_overs.addWidget(self.txt_match_overs)
        lay_header.addLayout(vbox_overs)

        grp_2nd_details = QGroupBox("2nd INNINGS DETAILS")
        grp_2nd_details.setStyleSheet("QGroupBox { background-color: black; color: white; font-weight: bold; border: 1px solid black; }")
        lay_2nd_details = QHBoxLayout()

        v21, self.lbl_2nd_total = make_black_field("TOTAL", "0/0")
        v22, self.lbl_2nd_over = make_black_field("OVER", "0.0")
        v23, self.lbl_2nd_rrr = make_black_field("RRR", "-")
        v24, self.lbl_2nd_need = make_black_field("NEED", "-")
        v25, self.lbl_2nd_from = make_black_field("FROM", "-")
        v26, self.lbl_2nd_extras = make_black_field("EXTRAS", "0")

        for v in [v21, v22, v23, v24, v25, v26]:
            lay_2nd_details.addLayout(v)

        grp_2nd_details.setLayout(lay_2nd_details)
        lay_header.addWidget(grp_2nd_details)

        master_layout.addLayout(lay_header)

        lay_stats_panels = QHBoxLayout()

        grp_lw = QGroupBox("LAST WICKETS")
        grp_lw.setStyleSheet("QGroupBox { background-color: #6c757d; color: white; font-weight: bold; font-size: 12px; border: 1px solid #5a6268; }")
        lay_lw_grid = QGridLayout()

        lay_lw_grid.addWidget(QLabel("<font color='white'><b>LASTWKTPlayer</b></font>"), 0, 0)
        lay_lw_grid.addWidget(QLabel("<font color='white'><b>FILDER</b></font>"), 0, 1)
        lay_lw_grid.addWidget(QLabel("<font color='white'><b>BOWLER</b></font>"), 0, 2)
        lay_lw_grid.addWidget(QLabel("<font color='white'><b>RUN</b></font>"), 0, 3)
        lay_lw_grid.addWidget(QLabel("<font color='white'><b>Ball</b></font>"), 0, 4)
        lay_lw_grid.addWidget(QLabel("<font color='white'><b>Out type</b></font>"), 0, 5)

        self.txt_lw_player = QLineEdit()
        self.txt_lw_fielder = QLineEdit()
        self.txt_lw_bowler = QLineEdit()
        self.txt_lw_run = QLineEdit("0")
        self.txt_lw_ball = QLineEdit("0")
        self.txt_lw_outtype = QLineEdit()

        for w_widget in [self.txt_lw_player, self.txt_lw_fielder, self.txt_lw_bowler, self.txt_lw_run, self.txt_lw_ball, self.txt_lw_outtype]:
            w_widget.setReadOnly(True)
            w_widget.setAlignment(Qt.AlignCenter)
            w_widget.setStyleSheet("background-color: white; color: black; font-weight: bold;")

        lay_lw_grid.addWidget(self.txt_lw_player, 1, 0)
        lay_lw_grid.addWidget(self.txt_lw_fielder, 1, 1)
        lay_lw_grid.addWidget(self.txt_lw_bowler, 1, 2)
        lay_lw_grid.addWidget(self.txt_lw_run, 1, 3)
        lay_lw_grid.addWidget(self.txt_lw_ball, 1, 4)
        lay_lw_grid.addWidget(self.txt_lw_outtype, 1, 5)

        grp_lw.setLayout(lay_lw_grid)
        lay_stats_panels.addWidget(grp_lw)

        grp_part = QGroupBox("PARTNERSHIP")
        grp_part.setStyleSheet("QGroupBox { background-color: #6c757d; color: white; font-weight: bold; font-size: 12px; border: 1px solid #5a6268; }")
        lay_part_grid = QGridLayout()

        lay_part_grid.addWidget(QLabel("<font color='white'><b>Batsman 1</b></font>"), 0, 0)
        lay_part_grid.addWidget(QLabel("<font color='white'><b>PARTNESHIP</b></font>"), 0, 1)
        lay_part_grid.addWidget(QLabel("<font color='white'><b>BALLS</b></font>"), 0, 2)
        lay_part_grid.addWidget(QLabel("<font color='white'><b>Batsman 2</b></font>"), 0, 3)
        lay_part_grid.addWidget(QLabel("<font color='white'><b>4S</b></font>"), 0, 4)
        lay_part_grid.addWidget(QLabel("<font color='white'><b>6S</b></font>"), 0, 5)

        self.txt_part_bat1 = QLineEdit()
        self.txt_part_runs = QLineEdit("0")
        self.txt_part_balls = QLineEdit("0")
        self.txt_part_bat2 = QLineEdit()
        self.txt_part_4s = QLineEdit("0")
        self.txt_part_6s = QLineEdit("0")

        for p_widget in [self.txt_part_bat1, self.txt_part_runs, self.txt_part_balls, self.txt_part_bat2, self.txt_part_4s, self.txt_part_6s]:
            p_widget.setReadOnly(True)
            p_widget.setAlignment(Qt.AlignCenter)
            p_widget.setStyleSheet("background-color: white; color: black; font-weight: bold;")

        lay_part_grid.addWidget(self.txt_part_bat1, 1, 0)
        lay_part_grid.addWidget(self.txt_part_runs, 1, 1)
        lay_part_grid.addWidget(self.txt_part_balls, 1, 2)
        lay_part_grid.addWidget(self.txt_part_bat2, 1, 3)
        lay_part_grid.addWidget(self.txt_part_4s, 1, 4)
        lay_part_grid.addWidget(self.txt_part_6s, 1, 5)

        grp_part.setLayout(lay_part_grid)
        lay_stats_panels.addWidget(grp_part)

        master_layout.addLayout(lay_stats_panels)

        main_scroll = QScrollArea()
        main_scroll.setWidgetResizable(True)
        main_scroll_widget = QWidget()
        left_layout = QVBoxLayout(main_scroll_widget)

        grp_teams = QGroupBox("Match Teams & Logo Setup")
        lay_teams = QGridLayout()

        lay_teams.addWidget(QLabel("Team A Name:"), 0, 0)
        self.txt_team1 = QLineEdit("AUS")
        self.txt_team1.setStyleSheet("font-size: 13px; font-weight: bold; padding: 3px;")
        lay_teams.addWidget(self.txt_team1, 0, 1)

        self.btn_logo_a = QPushButton("Browse Logo A")
        self.btn_logo_a.setStyleSheet("background-color: #6c757d; color: white; font-weight: bold; padding: 3px;")
        self.btn_logo_a.clicked.connect(self.browse_logo_a)
        lay_teams.addWidget(self.btn_logo_a, 0, 2)

        self.lbl_logo_a_name = QLabel("No Logo Selected")
        self.lbl_logo_a_name.setStyleSheet("font-size: 11px; color: gray;")
        lay_teams.addWidget(self.lbl_logo_a_name, 0, 3)

        lay_teams.addWidget(QLabel("Team B Name:"), 1, 0)
        self.txt_team2 = QLineEdit("PAK")
        self.txt_team2.setStyleSheet("font-size: 13px; font-weight: bold; padding: 3px;")
        lay_teams.addWidget(self.txt_team2, 1, 1)

        self.btn_logo_b = QPushButton("Browse Logo B")
        self.btn_logo_b.setStyleSheet("background-color: #6c757d; color: white; font-weight: bold; padding: 3px;")
        self.btn_logo_b.clicked.connect(self.browse_logo_b)
        lay_teams.addWidget(self.btn_logo_b, 1, 2)

        self.lbl_logo_b_name = QLabel("No Logo Selected")
        self.lbl_logo_b_name.setStyleSheet("font-size: 11px; color: gray;")
        lay_teams.addWidget(self.lbl_logo_b_name, 1, 3)

        grp_teams.setLayout(lay_teams)
        left_layout.addWidget(grp_teams)

        grp_toss = QGroupBox("Toss & Live Match Info Setup")
        lay_toss = QGridLayout()

        lay_toss.addWidget(QLabel("Toss Winner:"), 0, 0)
        self.cmb_toss_winner = QComboBox()
        self.cmb_toss_winner.setStyleSheet("font-size: 13px; padding: 2px;")
        lay_toss.addWidget(self.cmb_toss_winner, 0, 1)

        lay_toss.addWidget(QLabel("Decision:"), 0, 2)
        self.cmb_toss_choice = QComboBox()
        self.cmb_toss_choice.addItems(["BAT FIRST", "BOWL FIRST"])
        self.cmb_toss_choice.setStyleSheet("font-size: 13px; padding: 2px;")
        lay_toss.addWidget(self.cmb_toss_choice, 0, 3)

        lay_toss.addWidget(QLabel("Toss Banner Text:"), 1, 0)
        self.txt_toss_details = QLineEdit()
        self.txt_toss_details.setStyleSheet("font-size: 13px; font-weight: bold; color: green; padding: 3px;")
        lay_toss.addWidget(self.txt_toss_details, 1, 1, 1, 3)

        grp_toss.setLayout(lay_toss)
        left_layout.addWidget(grp_toss)

        grp_squad = QGroupBox("Team Playing XI Squad Setup (Click SELECT to Send to Batting/Bowling)")
        lay_squad_main = QVBoxLayout()
        lay_squad_cols = QHBoxLayout()

        self.grp_team1_squad = QGroupBox("AUS (Squad Lineup)")
        lay_team1_squad = QGridLayout()
        self.team1_inputs = []
        self.team1_select_btns = []
        for i in range(11):
            lbl = QLabel(f"P{i+1}:")
            txt = QLineEdit(f"Player A{i+1}")
            txt.setStyleSheet("font-size: 11px; padding: 2px;")
            btn_sel = QPushButton("SELECT")
            btn_sel.setStyleSheet("background-color: #28a745; color: white; font-size: 10px; font-weight: bold; padding: 2px;")
            btn_sel.clicked.connect(lambda checked, idx=i, team=1: self.on_player_select(team, idx))
            
            lay_team1_squad.addWidget(lbl, i, 0)
            lay_team1_squad.addWidget(txt, i, 1)
            lay_team1_squad.addWidget(btn_sel, i, 2)
            
            self.team1_inputs.append(txt)
            self.team1_select_btns.append(btn_sel)
        self.grp_team1_squad.setLayout(lay_team1_squad)
        lay_squad_cols.addWidget(self.grp_team1_squad)

        self.grp_team2_squad = QGroupBox("PAK (Squad Lineup)")
        lay_team2_squad = QGridLayout()
        self.team2_inputs = []
        self.team2_select_btns = []
        for i in range(11):
            lbl = QLabel(f"P{i+1}:")
            txt = QLineEdit(f"Player B{i+1}")
            txt.setStyleSheet("font-size: 11px; padding: 2px;")
            btn_sel = QPushButton("SELECT")
            btn_sel.setStyleSheet("background-color: #28a745; color: white; font-size: 10px; font-weight: bold; padding: 2px;")
            btn_sel.clicked.connect(lambda checked, idx=i, team=2: self.on_player_select(team, idx))
            
            lay_team2_squad.addWidget(lbl, i, 0)
            lay_team2_squad.addWidget(txt, i, 1)
            lay_team2_squad.addWidget(btn_sel, i, 2)
            
            self.team2_inputs.append(txt)
            self.team2_select_btns.append(btn_sel)
        self.grp_team2_squad.setLayout(lay_team2_squad)
        lay_squad_cols.addWidget(self.grp_team2_squad)

        lay_squad_main.addLayout(lay_squad_cols)

        self.btn_toggle_squad = QPushButton("TOGGLE SQUAD OVERLAY ON LIVE CAMERA (Input 3)")
        self.btn_toggle_squad.setStyleSheet("background-color: #0275d8; color: white; font-size: 12px; font-weight: bold; padding: 5px;")
        self.btn_toggle_squad.clicked.connect(self.toggle_squad_overlay)
        lay_squad_main.addWidget(self.btn_toggle_squad)

        grp_squad.setLayout(lay_squad_main)
        left_layout.addWidget(grp_squad)

        grp_wkt_details = QGroupBox("WICKET / RETIREMENT DETAILS CONTROL PANEL")
        grp_wkt_details.setStyleSheet("QGroupBox { background-color: #FFC0CB; font-weight: bold; border: 1px solid #D9534F; }")
        lay_wkt_grid = QGridLayout()

        lay_wkt_grid.addWidget(QLabel("<b>OUT BATSMAN</b>"), 0, 0)
        lay_wkt_grid.addWidget(QLabel("<b>FIELDER</b>"), 0, 1)
        lay_wkt_grid.addWidget(QLabel("<b>OUT TYPE / STATUS</b>"), 0, 2)
        lay_wkt_grid.addWidget(QLabel("<b>BOWLER</b>"), 0, 3)
        lay_wkt_grid.addWidget(QLabel("<b>RUN</b>"), 0, 4)
        lay_wkt_grid.addWidget(QLabel("<b>BALL</b>"), 0, 5)

        self.cmb_out_batsman = QComboBox()
        self.cmb_out_batsman.setStyleSheet("background-color: white; font-size: 12px; font-weight: bold;")
        self.cmb_out_batsman.currentIndexChanged.connect(self.update_wkt_preview_stats)
        lay_wkt_grid.addWidget(self.cmb_out_batsman, 1, 0)

        self.cmb_fielder = QComboBox()
        self.cmb_fielder.setStyleSheet("background-color: white; font-size: 12px; font-weight: bold;")
        lay_wkt_grid.addWidget(self.cmb_fielder, 1, 1)

        self.cmb_out_type = QComboBox()
        self.cmb_out_type.addItems(["BOWLED", "CAUGHT", "LBW", "RUN OUT", "STUMPED", "HIT WICKET", "RETIRED OUT", "RETIRED HURT"])
        self.cmb_out_type.setStyleSheet("background-color: white; font-size: 12px; font-weight: bold;")
        lay_wkt_grid.addWidget(self.cmb_out_type, 1, 2)

        self.txt_wkt_bowler = QLineEdit()
        self.txt_wkt_bowler.setReadOnly(True)
        self.txt_wkt_bowler.setStyleSheet("background-color: #EAEAEA; font-size: 12px; font-weight: bold;")
        lay_wkt_grid.addWidget(self.txt_wkt_bowler, 1, 3)

        self.txt_wkt_runs = QLineEdit("0")
        self.txt_wkt_runs.setReadOnly(True)
        self.txt_wkt_runs.setStyleSheet("background-color: #EAEAEA; font-size: 12px; font-weight: bold;")
        lay_wkt_grid.addWidget(self.txt_wkt_runs, 1, 4)

        self.txt_wkt_balls = QLineEdit("0")
        self.txt_wkt_balls.setReadOnly(True)
        self.txt_wkt_balls.setStyleSheet("background-color: #EAEAEA; font-size: 12px; font-weight: bold;")
        lay_wkt_grid.addWidget(self.txt_wkt_balls, 1, 5)

        self.btn_set_wkt = QPushButton("SET")
        self.btn_set_wkt.setStyleSheet("background-color: red; color: white; font-size: 16px; font-weight: bold; min-width: 60px; min-height: 35px;")
        self.btn_set_wkt.clicked.connect(self.submit_detailed_wicket)
        lay_wkt_grid.addWidget(self.btn_set_wkt, 0, 6, 2, 1)

        grp_wkt_details.setLayout(lay_wkt_grid)
        left_layout.addWidget(grp_wkt_details)

        self.grp_active = QGroupBox("1st Innings Active Players & Live Scorecard Stats")
        lay_active = QVBoxLayout()

        lay_dropdowns = QGridLayout()
        lay_dropdowns.addWidget(QLabel("<b>Batsman 1 (Striker):</b>"), 0, 0)
        self.lbl_bat1_disp = QLineEdit("None")
        self.lbl_bat1_disp.setReadOnly(True)
        self.lbl_bat1_disp.setStyleSheet("font-size: 12px; font-weight: bold; background: #fff;")
        lay_dropdowns.addWidget(self.lbl_bat1_disp, 0, 1)

        lay_dropdowns.addWidget(QLabel("<b>Batsman 2 (Non-Striker):</b>"), 0, 2)
        self.lbl_bat2_disp = QLineEdit("None")
        self.lbl_bat2_disp.setReadOnly(True)
        self.lbl_bat2_disp.setStyleSheet("font-size: 12px; font-weight: bold; background: #fff;")
        lay_dropdowns.addWidget(self.lbl_bat2_disp, 0, 3)

        self.btn_swap_strike = QPushButton("ROTATE STRIKE ( > )")
        self.btn_swap_strike.setStyleSheet("background-color: #5bc0de; color: white; font-size: 11px; font-weight: bold; padding: 4px;")
        self.btn_swap_strike.clicked.connect(self.swap_strike)
        lay_dropdowns.addWidget(self.btn_swap_strike, 0, 4)

        lay_dropdowns.addWidget(QLabel("<b>Current Bowler:</b>"), 1, 0)
        self.lbl_bowler_disp = QLineEdit("None")
        self.lbl_bowler_disp.setReadOnly(True)
        self.lbl_bowler_disp.setStyleSheet("font-size: 12px; font-weight: bold; color: maroon; background: #fff;")
        lay_dropdowns.addWidget(self.lbl_bowler_disp, 1, 1, 1, 3)

        lay_active.addLayout(lay_dropdowns)

        lay_tables = QHBoxLayout()
        self.tbl_batsmen = QTableWidget(2, 6)
        self.tbl_batsmen.setHorizontalHeaderLabels(["Batsman Name", "Runs (R)", "Balls (B)", "Fours (4s)", "Sixes (6s)", "Strike Rate (SR)"])
        self.tbl_batsmen.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.tbl_batsmen.setMaximumHeight(65)
        self.tbl_batsmen.setStyleSheet("font-size: 11px; font-weight: bold;")
        lay_tables.addWidget(self.tbl_batsmen, 60)

        self.tbl_bowler = QTableWidget(1, 5)
        self.tbl_bowler.setHorizontalHeaderLabels(["Bowler Name", "Overs (O)", "Maidens (M)", "Runs (R)", "Wickets (W)"])
        self.tbl_bowler.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.tbl_bowler.setMaximumHeight(65)
        self.tbl_bowler.setStyleSheet("font-size: 11px; font-weight: bold; color: maroon;")
        lay_tables.addWidget(self.tbl_bowler, 40)

        lay_active.addLayout(lay_tables)
        self.grp_active.setLayout(lay_active)
        left_layout.addWidget(self.grp_active)

        self.lbl_this_over = QLabel("THIS OVER: ", self)
        self.lbl_this_over.setAlignment(Qt.AlignCenter)
        self.lbl_this_over.setStyleSheet("font-size: 15px; font-weight: bold; color: darkgreen; background: #E8F8F5; border: 1px solid #A3E4D7; border-radius: 4px; padding: 3px;")
        left_layout.addWidget(self.lbl_this_over)

        self.lbl_teams = QLabel("AUS VS PAK")
        self.lbl_teams.setAlignment(Qt.AlignCenter)
        self.lbl_teams.setStyleSheet("font-size: 15px; font-weight: bold; color: #555;")
        left_layout.addWidget(self.lbl_teams)

        self.lbl_score = QLabel("0/0 (0.0)", self)
        self.lbl_score.setAlignment(Qt.AlignCenter)
        self.lbl_score.setStyleSheet("font-size: 28px; font-weight: bold; color: #0047AB; background: #EAEAEA; border-radius: 6px; padding: 2px;")
        left_layout.addWidget(self.lbl_score)

        undo_row = QHBoxLayout()
        self.btn_undo = QPushButton("↶ UNDO LAST ACTION")
        self.btn_undo.setEnabled(False)
        self.btn_undo.setStyleSheet(
            "QPushButton { background-color: #c62828; color: white; "
            "font-size: 13px; font-weight: bold; padding: 8px; border-radius: 4px; }"
            "QPushButton:disabled { background-color: #bdbdbd; color: #eeeeee; }"
            "QPushButton:hover:!disabled { background-color: #a31515; }"
        )
        self.btn_undo.clicked.connect(self.undo_last_action)
        undo_row.addWidget(self.btn_undo)
        left_layout.addLayout(undo_row)

        grp_runs = QGroupBox("Standard Runs")
        grid_runs = QGridLayout()
        run_options = [0, 1, 2, 3, 4, 6]
        for i, r in enumerate(run_options):
            btn = QPushButton(f"+ {r} Run")
            btn.setStyleSheet("font-size: 12px; font-weight: bold; padding: 4px;")
            btn.clicked.connect(lambda checked, run=r: self.add_runs(run))
            grid_runs.addWidget(btn, i // 3, i % 3)
        grp_runs.setLayout(grid_runs)
        left_layout.addWidget(grp_runs)

        grp_extras = QGroupBox("Extras Controls")
        lay_extras = QVBoxLayout()

        lay_lb_b = QHBoxLayout()
        lay_lb_b.addWidget(QLabel("<b>Leg Bye:</b>"))
        for r in [1, 2, 3, 4]:
            btn = QPushButton(f"LB {r}")
            btn.setStyleSheet("background-color: #e2e3e5; font-weight: bold; padding: 2px;")
            btn.clicked.connect(lambda checked, run=r: self.add_leg_bye(run))
            lay_lb_b.addWidget(btn)

        lay_lb_b.addWidget(QLabel("<b>Bye:</b>"))
        for r in [1, 2, 3, 4]:
            btn = QPushButton(f"B {r}")
            btn.setStyleSheet("background-color: #e2e3e5; font-weight: bold; padding: 2px;")
            btn.clicked.connect(lambda checked, run=r: self.add_bye(run))
            lay_lb_b.addWidget(btn)
        lay_extras.addLayout(lay_lb_b)

        lay_wd_nb = QHBoxLayout()
        lay_wd_nb.addWidget(QLabel("<b>Wide:</b>"))
        for r in [0, 1, 2, 3, 4]:
            btn = QPushButton(f"WD + {r}")
            btn.setStyleSheet("background-color: #fff3cd; color: #856404; font-weight: bold; padding: 2px;")
            btn.clicked.connect(lambda checked, run=r: self.add_wide(run))
            lay_wd_nb.addWidget(btn)

        lay_wd_nb.addWidget(QLabel("<b>No Ball:</b>"))
        for r in [0, 1, 2, 3, 4, 6]:
            btn = QPushButton(f"NB + {r}")
            btn.setStyleSheet("background-color: #f8d7da; color: #721c24; font-weight: bold; padding: 2px;")
            btn.clicked.connect(lambda checked, run=r: self.add_no_ball(run))
            lay_wd_nb.addWidget(btn)
        lay_extras.addLayout(lay_wd_nb)

        grp_extras.setLayout(lay_extras)
        left_layout.addWidget(grp_extras)

        lay_so = QHBoxLayout()
        self.btn_super_over = QPushButton("⚡ START SUPER OVER")
        self.btn_super_over.setStyleSheet("background-color: #ff9800; color: white; font-size: 13px; font-weight: bold; padding: 6px;")
        self.btn_super_over.clicked.connect(self.start_super_over)
        lay_so.addWidget(self.btn_super_over)
        left_layout.addLayout(lay_so)

        lay_bottom = QHBoxLayout()
        self.btn_end_inning = QPushButton("END INNING")
        self.btn_end_inning.setStyleSheet("background-color: #6f42c1; color: white; font-size: 13px; font-weight: bold; padding: 6px;")
        self.btn_end_inning.clicked.connect(self.end_first_innings)
        lay_bottom.addWidget(self.btn_end_inning)

        self.btn_end_match = QPushButton("🏁 END MATCH (WIN/LOSS & POINTS)")
        self.btn_end_match.setStyleSheet("background-color: #D9534F; color: white; font-size: 13px; font-weight: bold; padding: 6px;")
        self.btn_end_match.clicked.connect(self.handle_end_match_action)
        lay_bottom.addWidget(self.btn_end_match)

        btn_reset = QPushButton("RESET MATCH SCORE")
        btn_reset.setStyleSheet("background-color: #F0AD4E; color: white; font-size: 13px; font-weight: bold; padding: 6px;")
        btn_reset.clicked.connect(self.reset_score)
        lay_bottom.addWidget(btn_reset)
        
        left_layout.addLayout(lay_bottom)
        main_scroll.setWidget(main_scroll_widget)

        self.tab_side = QTabWidget()
        self.tab_side.setStyleSheet("QTabBar::tab { font-size: 12px; font-weight: bold; padding: 6px; }")

        tab_batting = QWidget()
        lay_tab_bat = QVBoxLayout()
        self.tbl_full_batting = QTableWidget(11, 8)
        self.tbl_full_batting.setHorizontalHeaderLabels(["PLAYER", "RUNS", "BALLS", "4s", "6s", "SR", "OUT BY", "DISMISSAL"])
        self.tbl_full_batting.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.tbl_full_batting.setStyleSheet("font-size: 11px;")
        lay_tab_bat.addWidget(self.tbl_full_batting)
        tab_batting.setLayout(lay_tab_bat)
        self.tab_side.addTab(tab_batting, "1st Innings")

        tab_bowling = QWidget()
        lay_tab_bowl = QVBoxLayout()
        self.tbl_full_bowling = QTableWidget(11, 6)
        self.tbl_full_bowling.setHorizontalHeaderLabels(["BOWLER", "O", "M", "R", "W", "ECO"])
        self.tbl_full_bowling.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.tbl_full_bowling.setStyleSheet("font-size: 11px;")
        lay_tab_bowl.addWidget(self.tbl_full_bowling)
        tab_bowling.setLayout(lay_tab_bowl)
        self.tab_side.addTab(tab_bowling, "T1 Bowling")

        tab_batting_t2 = QWidget()
        lay_tab_bat2 = QVBoxLayout()
        self.tbl_full_batting2 = QTableWidget(11, 8)
        self.tbl_full_batting2.setHorizontalHeaderLabels(["PLAYER", "RUNS", "BALLS", "4s", "6s", "SR", "OUT BY", "DISMISSAL"])
        self.tbl_full_batting2.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.tbl_full_batting2.setStyleSheet("font-size: 11px;")
        lay_tab_bat2.addWidget(self.tbl_full_batting2)
        tab_batting_t2.setLayout(lay_tab_bat2)
        self.tab_side.addTab(tab_batting_t2, "2nd Innings")

        tab_bowling_t2 = QWidget()
        lay_tab_bowl2 = QVBoxLayout()
        self.tbl_full_bowling2 = QTableWidget(11, 6)
        self.tbl_full_bowling2.setHorizontalHeaderLabels(["BOWLER", "O", "M", "R", "W", "ECO"])
        self.tbl_full_bowling2.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.tbl_full_bowling2.setStyleSheet("font-size: 11px;")
        lay_tab_bowl2.addWidget(self.tbl_full_bowling2)
        tab_bowling_t2.setLayout(lay_tab_bowl2)
        self.tab_side.addTab(tab_bowling_t2, "T2 Bowling")

        tab_summary = QWidget()
        lay_sum_main = QVBoxLayout()
        sum_scroll = QScrollArea()
        sum_scroll.setWidgetResizable(True)
        sum_scroll_widget = QWidget()
        lay_sum_content = QVBoxLayout(sum_scroll_widget)

        self.grp_sum_1st = QGroupBox("1st INNINGS")
        lay_sum_1st_v = QVBoxLayout()
        
        lay_s1_info = QHBoxLayout()
        lay_s1_info.addWidget(QLabel("TEAM"))
        self.txt_sum_t1_name = QLineEdit("TEAM A")
        self.txt_sum_t1_name.setReadOnly(True)
        lay_s1_info.addWidget(self.txt_sum_t1_name)
        lay_s1_info.addWidget(QLabel("SCORE"))
        self.txt_sum_t1_score = QLineEdit("0/0")
        self.txt_sum_t1_score.setReadOnly(True)
        lay_s1_info.addWidget(self.txt_sum_t1_score)
        lay_s1_info.addWidget(QLabel("OVERS"))
        self.txt_sum_t1_overs = QLineEdit("0.0")
        self.txt_sum_t1_overs.setReadOnly(True)
        lay_s1_info.addWidget(self.txt_sum_t1_overs)
        lay_s1_info.addWidget(QLabel("EXTRAS"))
        self.txt_sum_t1_extras = QLineEdit("0")
        self.txt_sum_t1_extras.setReadOnly(True)
        lay_s1_info.addWidget(self.txt_sum_t1_extras)
        lay_sum_1st_v.addLayout(lay_s1_info)

        lay_s1_stats = QHBoxLayout()
        vbox_s1_bat = QVBoxLayout()
        vbox_s1_bat.addWidget(QLabel("<b>ALL 11 A TEAM BATSMEN</b>"))
        self.tbl_sum_t1_bat = QTableWidget(11, 4)
        self.tbl_sum_t1_bat.setHorizontalHeaderLabels(["PLAYER", "R", "B", "SR"])
        self.tbl_sum_t1_bat.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.tbl_sum_t1_bat.setMaximumHeight(260)
        vbox_s1_bat.addWidget(self.tbl_sum_t1_bat)
        lay_s1_stats.addLayout(vbox_s1_bat)

        vbox_s1_bowl = QVBoxLayout()
        vbox_s1_bowl.addWidget(QLabel("<b>ALL 11 B TEAM BOWLERS</b>"))
        self.tbl_sum_t2_bowl = QTableWidget(11, 4)
        self.tbl_sum_t2_bowl.setHorizontalHeaderLabels(["PLAYER", "O", "R", "W"])
        self.tbl_sum_t2_bowl.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.tbl_sum_t2_bowl.setMaximumHeight(260)
        vbox_s1_bowl.addWidget(self.tbl_sum_t2_bowl)
        lay_s1_stats.addLayout(vbox_s1_bowl)

        lay_sum_1st_v.addLayout(lay_s1_stats)
        self.grp_sum_1st.setLayout(lay_sum_1st_v)
        lay_sum_content.addWidget(self.grp_sum_1st)

        self.grp_sum_2nd = QGroupBox("2nd INNINGS")
        lay_sum_2nd_v = QVBoxLayout()

        lay_s2_info = QHBoxLayout()
        lay_s2_info.addWidget(QLabel("TEAM"))
        self.txt_sum_t2_name = QLineEdit("TEAM B")
        self.txt_sum_t2_name.setReadOnly(True)
        lay_s2_info.addWidget(self.txt_sum_t2_name)
        lay_s2_info.addWidget(QLabel("SCORE"))
        self.txt_sum_t2_score = QLineEdit("0/0")
        self.txt_sum_t2_score.setReadOnly(True)
        lay_s2_info.addWidget(self.txt_sum_t2_score)
        lay_s2_info.addWidget(QLabel("OVERS"))
        self.txt_sum_t2_overs = QLineEdit("0.0")
        self.txt_sum_t2_overs.setReadOnly(True)
        lay_s2_info.addWidget(self.txt_sum_t2_overs)
        lay_s2_info.addWidget(QLabel("EXTRAS"))
        self.txt_sum_t2_extras = QLineEdit("0")
        self.txt_sum_t2_extras.setReadOnly(True)
        lay_s2_info.addWidget(self.txt_sum_t2_extras)
        lay_sum_2nd_v.addLayout(lay_s2_info)

        lay_s2_stats = QHBoxLayout()
        vbox_s2_bat = QVBoxLayout()
        vbox_s2_bat.addWidget(QLabel("<b>ALL 11 B TEAM BATSMEN</b>"))
        self.tbl_sum_t2_bat = QTableWidget(11, 4)
        self.tbl_sum_t2_bat.setHorizontalHeaderLabels(["PLAYER", "R", "B", "SR"])
        self.tbl_sum_t2_bat.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.tbl_sum_t2_bat.setMaximumHeight(260)
        vbox_s2_bat.addWidget(self.tbl_sum_t2_bat)
        lay_s2_stats.addLayout(vbox_s2_bat)

        vbox_s2_bowl = QVBoxLayout()
        vbox_s2_bowl.addWidget(QLabel("<b>ALL 11 A TEAM BOWLERS</b>"))
        self.tbl_sum_t1_bowl = QTableWidget(11, 4)
        self.tbl_sum_t1_bowl.setHorizontalHeaderLabels(["PLAYER", "O", "R", "W"])
        self.tbl_sum_t1_bowl.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.tbl_sum_t1_bowl.setMaximumHeight(260)
        vbox_s2_bowl.addWidget(self.tbl_sum_t1_bowl)
        lay_s2_stats.addLayout(vbox_s2_bowl)

        lay_sum_2nd_v.addLayout(lay_s2_stats)
        self.grp_sum_2nd.setLayout(lay_sum_2nd_v)
        lay_sum_content.addWidget(self.grp_sum_2nd)

        lay_res_row = QHBoxLayout()
        lay_res_row.addWidget(QLabel("<b>TARGET</b>"))
        self.txt_sum_target = QLineEdit("-")
        self.txt_sum_target.setReadOnly(True)
        lay_res_row.addWidget(self.txt_sum_target)

        lay_res_row.addWidget(QLabel("<b>NEED</b>"))
        self.txt_sum_need = QLineEdit("-")
        self.txt_sum_need.setReadOnly(True)
        lay_res_row.addWidget(self.txt_sum_need)

        lay_res_row.addWidget(QLabel("<b>RRR</b>"))
        self.txt_sum_rrr = QLineEdit("-")
        self.txt_sum_rrr.setReadOnly(True)
        lay_res_row.addWidget(self.txt_sum_rrr)
        lay_sum_content.addLayout(lay_res_row)

        lay_result_box = QHBoxLayout()
        lay_result_box.addWidget(QLabel("<b>RESULT</b>"))
        self.txt_sum_result = QLineEdit("MATCH IN PROGRESS")
        self.txt_sum_result.setReadOnly(True)
        self.txt_sum_result.setStyleSheet("font-weight: bold; color: blue; background-color: #E8F8F5;")
        lay_result_box.addWidget(self.txt_sum_result)
        lay_sum_content.addLayout(lay_result_box)

        lay_status_box = QHBoxLayout()
        lay_status_box.addWidget(QLabel("<b>STATUS</b>"))
        self.txt_sum_status = QLineEdit("LIVE")
        self.txt_sum_status.setReadOnly(True)
        self.txt_sum_status.setStyleSheet("font-weight: bold; color: green; background-color: #FCF3CF;")
        lay_status_box.addWidget(self.txt_sum_status)
        lay_sum_content.addLayout(lay_status_box)

        sum_scroll.setWidget(sum_scroll_widget)
        lay_sum_main.addWidget(sum_scroll)
        tab_summary.setLayout(lay_sum_main)
        self.tab_side.addTab(tab_summary, "Match Summary")

        body_layout = QHBoxLayout()
        body_layout.addWidget(main_scroll, 55)
        body_layout.addWidget(self.tab_side, 45)

        master_layout.addLayout(body_layout)
        tab_live_scoring.setLayout(master_layout)
        # Tournament Schedule and independent Re-Entry tabs
        tab_tournament_schedule = QWidget()
        lay_ts = QVBoxLayout()
        grp_ts = QGroupBox("🏆 TOURNAMENT SCHEDULE / KNOCKOUT BRACKET")
        lay_ts_inner = QVBoxLayout()
        self.tbl_tournament_schedule = QTableWidget(0, 7)
        self.tbl_tournament_schedule.setHorizontalHeaderLabels(["Round", "Match", "Date", "Time", "Team A", "Team B", "Winner"])
        self.tbl_tournament_schedule.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.tbl_tournament_schedule.setStyleSheet("font-size: 12px; font-weight: bold;")
        self.tbl_tournament_schedule.itemChanged.connect(lambda item: self.on_custom_tournament_cell_changed("schedule", item))
        self.tbl_tournament_schedule.cellPressed.connect(lambda row, col: self._prepare_tournament_cell_undo("schedule"))
        lay_ts_inner.addWidget(self.tbl_tournament_schedule)
        ts_buttons = QHBoxLayout()
        btn_create_ts = QPushButton("➕ ADD CUSTOM TOURNAMENT")
        btn_create_ts.clicked.connect(self.create_custom_tournament)
        ts_buttons.addWidget(btn_create_ts)
        btn_winner_ts = QPushButton("🏅 SET MATCH WINNER")
        btn_winner_ts.clicked.connect(lambda: self.set_tournament_match_winner("schedule"))
        ts_buttons.addWidget(btn_winner_ts)
        btn_reset_ts = QPushButton("🗑 RESET TOURNAMENT SCHEDULE")
        btn_reset_ts.setStyleSheet("background:#c62828;color:white;font-weight:bold;padding:8px;")
        btn_reset_ts.clicked.connect(self.reset_custom_tournament)
        ts_buttons.addWidget(btn_reset_ts)
        self.btn_undo_tournament_schedule = QPushButton("↶ UNDO")
        self.btn_undo_tournament_schedule.setStyleSheet("background:#455a64;color:white;font-weight:bold;padding:8px;")
        self.btn_undo_tournament_schedule.setEnabled(False)
        self.btn_undo_tournament_schedule.clicked.connect(lambda: self.undo_tournament_action("schedule"))
        ts_buttons.addWidget(self.btn_undo_tournament_schedule)
        lay_ts_inner.addLayout(ts_buttons)
        grp_ts.setLayout(lay_ts_inner)
        lay_ts.addWidget(grp_ts)
        tab_tournament_schedule.setLayout(lay_ts)
        self.main_tabs.addTab(tab_tournament_schedule, "🏆 Tournament Schedule")

        tab_reentry = QWidget()
        lay_re = QVBoxLayout()
        grp_re = QGroupBox("🔁 RE-ENTRY ROUND – FIRST ROUND LOSING TEAMS")
        lay_re_inner = QVBoxLayout()
        self.tbl_reentry = QTableWidget(0, 7)
        self.tbl_reentry.setHorizontalHeaderLabels(["Match", "Date", "Time", "Team A", "Team B", "Winner", "Status"])
        self.tbl_reentry.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.tbl_reentry.setStyleSheet("font-size: 12px; font-weight: bold;")
        self.tbl_reentry.itemChanged.connect(lambda item: self.on_custom_tournament_cell_changed("reentry", item))
        self.tbl_reentry.cellPressed.connect(lambda row, col: self._prepare_tournament_cell_undo("reentry"))
        lay_re_inner.addWidget(self.tbl_reentry)
        re_buttons = QHBoxLayout()
        btn_re_winner = QPushButton("🏅 SET RE-ENTRY WINNER")
        btn_re_winner.clicked.connect(lambda: self.set_tournament_match_winner("reentry"))
        re_buttons.addWidget(btn_re_winner)
        btn_re_reset = QPushButton("🗑 RESET RE-ENTRY")
        btn_re_reset.setStyleSheet("background:#c62828;color:white;font-weight:bold;padding:8px;")
        btn_re_reset.clicked.connect(self.reset_reentry_only)
        re_buttons.addWidget(btn_re_reset)
        self.btn_undo_reentry = QPushButton("↶ UNDO")
        self.btn_undo_reentry.setStyleSheet("background:#455a64;color:white;font-weight:bold;padding:8px;")
        self.btn_undo_reentry.setEnabled(False)
        self.btn_undo_reentry.clicked.connect(lambda: self.undo_tournament_action("reentry"))
        re_buttons.addWidget(self.btn_undo_reentry)
        lay_re_inner.addLayout(re_buttons)
        grp_re.setLayout(lay_re_inner)
        lay_re.addWidget(grp_re)
        tab_reentry.setLayout(lay_re)
        self.main_tabs.addTab(tab_reentry, "🔁 Re-Entry")

        # Independent Group Match Schedule tab (does not modify Tournament Schedule / Re-Entry)
        tab_group_schedule = QWidget()
        lay_gs = QVBoxLayout()
        grp_gs = QGroupBox("🏏 GROUP MATCH SCHEDULE – GROUP STAGE TO FINAL")
        lay_gs_inner = QVBoxLayout()
        gs_split = QHBoxLayout()
        self.tbl_group_schedule = QTableWidget(0, 9)
        self.tbl_group_schedule.setHorizontalHeaderLabels(["Group", "Round", "Match", "Date", "Time", "Team A", "Team B", "Venue", "Winner"])
        self.tbl_group_schedule.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.tbl_group_schedule.setStyleSheet("font-size: 11px; font-weight: bold;")
        self.tbl_group_schedule.itemChanged.connect(self.on_group_schedule_cell_changed)
        gs_split.addWidget(self.tbl_group_schedule, 68)
        right_gs = QVBoxLayout()
        right_gs.setSpacing(5)
        self.lbl_group_points_title = QLabel("🏆 GROUP POINTS TABLE")
        self.lbl_group_points_title.setAlignment(Qt.AlignCenter)
        self.lbl_group_points_title.setStyleSheet(
            "background:#25002f;color:#ffe600;font-size:17px;font-weight:900;"
            "padding:8px;border:1px solid #d6b900;"
        )
        right_gs.addWidget(self.lbl_group_points_title)
        # Broadcast-style points table, inspired by the user's ICC reference image.
        self.tbl_group_points = QTableWidget(0, 8)
        self.tbl_group_points.setHorizontalHeaderLabels(["POS", "TEAM", "P", "W", "L", "NR", "PTS", "NRR"])
        self.tbl_group_points.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.tbl_group_points.verticalHeader().setVisible(False)
        self.tbl_group_points.setAlternatingRowColors(False)
        self.tbl_group_points.setShowGrid(False)
        self.tbl_group_points.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.tbl_group_points.setSelectionMode(QAbstractItemView.NoSelection)
        self.tbl_group_points.setStyleSheet("""
            QTableWidget { background:#21002d; color:white; border:1px solid #4c3156;
                           gridline-color:#21002d; font-size:10px; font-weight:800; }
            QHeaderView::section { background:#160020; color:white; padding:5px 2px;
                                   border:0px; border-bottom:2px solid #e0c400;
                                   font-size:10px; font-weight:900; }
            QTableWidget::item { background:#064ca8; color:white; padding:4px 2px;
                                 border:0px; border-bottom:2px solid #21002d; }
            QTableWidget::item:selected { background:#064ca8; color:white; }
        """)
        right_gs.addWidget(self.tbl_group_points, 1)
        lbl_group_note = QLabel("NRR will appear when match score details are linked.")
        lbl_group_note.setWordWrap(True)
        lbl_group_note.setStyleSheet("color:#333;font-size:10px;")
        right_gs.addWidget(lbl_group_note)
        gs_split.addLayout(right_gs, 38)
        lay_gs_inner.addLayout(gs_split)
        gs_buttons = QHBoxLayout()
        btn_setup_groups = QPushButton("⚙ CREATE / SET GROUPS")
        btn_setup_groups.clicked.connect(self.create_group_tournament)
        gs_buttons.addWidget(btn_setup_groups)
        btn_group_winner = QPushButton("🏅 SET MATCH WINNER")
        btn_group_winner.clicked.connect(self.set_group_match_winner)
        gs_buttons.addWidget(btn_group_winner)
        btn_reset_groups = QPushButton("🗑 RESET GROUP SCHEDULE")
        btn_reset_groups.setStyleSheet("background:#c62828;color:white;font-weight:bold;padding:8px;")
        btn_reset_groups.clicked.connect(self.reset_group_tournament)
        gs_buttons.addWidget(btn_reset_groups)
        btn_refresh_groups = QPushButton("↻ REFRESH POINTS")
        btn_refresh_groups.clicked.connect(self.refresh_group_schedule_tables)
        gs_buttons.addWidget(btn_refresh_groups)
        lay_gs_inner.addLayout(gs_buttons)
        grp_gs.setLayout(lay_gs_inner)
        lay_gs.addWidget(grp_gs)
        tab_group_schedule.setLayout(lay_gs)
        self.main_tabs.addTab(tab_group_schedule, "🏏 Group Match Schedule")

        # Tournament-wide 4s/6s leaderboard (saved independently of match reset)
        tab_tournament_boundaries = QWidget()
        lay_tb_main = QVBoxLayout()
        grp_tb = QGroupBox("🏆 TOURNAMENT 4S & 6S PLAYER RECORD")
        lay_tb = QVBoxLayout()
        self.tbl_tournament_4s6s = QTableWidget(0, 6)
        self.tbl_tournament_4s6s.setHorizontalHeaderLabels(
            ["Sr. No.", "PLAYER NAME", "TEAM NAME", "4S", "6S", "STRIKE RATE"]
        )
        self.tbl_tournament_4s6s.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.tbl_tournament_4s6s.setEditTriggers(QTableWidget.NoEditTriggers)
        self.tbl_tournament_4s6s.setStyleSheet("font-size: 13px; font-weight: bold;")
        lay_tb.addWidget(self.tbl_tournament_4s6s)
        self.btn_reset_tournament_4s6s = QPushButton("🗑 MANUAL RESET TOURNAMENT 4S / 6S RECORD")
        self.btn_reset_tournament_4s6s.setStyleSheet(
            "background-color: #c62828; color: white; font-size: 13px; "
            "font-weight: bold; padding: 10px;"
        )
        self.btn_reset_tournament_4s6s.clicked.connect(self.reset_tournament_4s6s)
        lay_tb.addWidget(self.btn_reset_tournament_4s6s)

        # Separate manual reset for the tournament-wide vMix 4s/6s counters.
        self.btn_reset_tournament_boundary_counters = QPushButton(
            "🗑 RESET TOURNAMENT FOURS / SIXES vMix COUNTERS (INPUT 33 / 34)"
        )
        self.btn_reset_tournament_boundary_counters.setStyleSheet(
            "background-color: #8e0000; color: white; font-size: 13px; "
            "font-weight: bold; padding: 10px;"
        )
        self.btn_reset_tournament_boundary_counters.clicked.connect(
            self.reset_tournament_boundary_counters
        )
        lay_tb.addWidget(self.btn_reset_tournament_boundary_counters)
        grp_tb.setLayout(lay_tb)
        lay_tb_main.addWidget(grp_tb)
        tab_tournament_boundaries.setLayout(lay_tb_main)
        self.main_tabs.addTab(tab_tournament_boundaries, "🏆 4S & 6S Tournament")

        self.main_tabs.addTab(tab_live_scoring, "Live Scoring")

        tab_batsman_milestones = QWidget()
        lay_bm_main = QVBoxLayout()

        grp_milestones_table = QGroupBox("⭐ BATSMAN 50 / 100 MILESTONES RECORDS TABLE")
        grp_milestones_table.setStyleSheet("QGroupBox { background-color: #f8f9fa; color: #333; font-weight: bold; font-size: 14px; border: 1px solid #ccc; padding: 10px; }")
        lay_ms_table = QVBoxLayout()

        self.tbl_milestones = QTableWidget(0, 8)
        self.tbl_milestones.setHorizontalHeaderLabels([
            "Date and Time", "Player Name", "Team Name", "50 ya 100", "Run", "Ball", "Strike Rate", "VS Team Name"
        ])
        self.tbl_milestones.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.tbl_milestones.setStyleSheet("font-size: 12px; font-weight: bold; color: black; background-color: white;")
        lay_ms_table.addWidget(self.tbl_milestones)

        btn_refresh_ms = QPushButton("🔄 Refresh Milestones Table")
        btn_refresh_ms.setStyleSheet("background-color: #ff9800; color: white; font-size: 13px; font-weight: bold; padding: 8px;")
        btn_refresh_ms.clicked.connect(self.load_milestones_data_to_table)
        lay_ms_table.addWidget(btn_refresh_ms)

        btn_reset_ms = QPushButton("🗑 RESET BATSMAN MILESTONES")
        btn_reset_ms.setStyleSheet("background-color: #c62828; color: white; font-size: 13px; font-weight: bold; padding: 9px;")
        btn_reset_ms.clicked.connect(self.reset_batsman_milestones)
        lay_ms_table.addWidget(btn_reset_ms)

        grp_milestones_table.setLayout(lay_ms_table)
        lay_bm_main.addWidget(grp_milestones_table)

        tab_batsman_milestones.setLayout(lay_bm_main)
        self.main_tabs.addTab(tab_batsman_milestones, "⭐ Batsman Milestones")

        tab_bowler_milestones = QWidget()
        lay_bw_main = QVBoxLayout()

        grp_bowler_ms_table = QGroupBox("⭐ BOWLER 5-WICKET MILESTONES RECORDS TABLE")
        grp_bowler_ms_table.setStyleSheet("QGroupBox { background-color: #f8f9fa; color: #333; font-weight: bold; font-size: 14px; border: 1px solid #ccc; padding: 10px; }")
        lay_bms_table = QVBoxLayout()

        self.tbl_bowler_milestones = QTableWidget(0, 8)
        self.tbl_bowler_milestones.setHorizontalHeaderLabels([
            "Date and Time", "Bowler Name", "Team Name", "Milestone", "Overs", "Wickets", "Runs", "VS Team Name"
        ])
        self.tbl_bowler_milestones.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.tbl_bowler_milestones.setStyleSheet("font-size: 12px; font-weight: bold; color: black; background-color: white;")
        lay_bms_table.addWidget(self.tbl_bowler_milestones)

        btn_refresh_bms = QPushButton("🔄 Refresh Bowler Milestones Table")
        btn_refresh_bms.setStyleSheet("background-color: #e65100; color: white; font-size: 13px; font-weight: bold; padding: 8px;")
        btn_refresh_bms.clicked.connect(self.load_bowler_milestones_data_to_table)
        lay_bms_table.addWidget(btn_refresh_bms)

        btn_reset_bms = QPushButton("🗑 RESET BOWLER MILESTONES")
        btn_reset_bms.setStyleSheet("background-color: #c62828; color: white; font-size: 13px; font-weight: bold; padding: 9px;")
        btn_reset_bms.clicked.connect(self.reset_bowler_milestones)
        lay_bms_table.addWidget(btn_reset_bms)

        grp_bowler_ms_table.setLayout(lay_bms_table)
        lay_bw_main.addWidget(grp_bowler_ms_table)

        tab_bowler_milestones.setLayout(lay_bw_main)
        self.main_tabs.addTab(tab_bowler_milestones, "⭐ Bowler Milestones")

        tab_points_table = QWidget()
        lay_pt_main = QVBoxLayout()

        self.tbl_points_table = QTableWidget(50, 11)  
        self.tbl_points_table.setHorizontalHeaderLabels([
            "Sr No.", "Team", "Played (P)", "Won (W)", "Lost (L)", "Points (PTS)", 
            "Runs Scored", "Overs Faced", "Runs Conceded", "Overs Bowled", "NRR"
        ])
        self.tbl_points_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.tbl_points_table.setStyleSheet("font-size: 11px; font-weight: bold;")
        lay_pt_main.addWidget(self.tbl_points_table)

        lay_pt_buttons = QHBoxLayout()
        
        btn_refresh_pt = QPushButton("🔄 Refresh Table")
        btn_refresh_pt.setStyleSheet("background-color: #00bcd4; color: white; font-size: 12px; font-weight: bold; padding: 6px;")
        btn_refresh_pt.clicked.connect(self.update_points_table_display)
        lay_pt_buttons.addWidget(btn_refresh_pt)

        btn_manual_save = QPushButton("💾 Save Table Manually")
        btn_manual_save.setStyleSheet("background-color: #28a745; color: white; font-size: 12px; font-weight: bold; padding: 6px;")
        btn_manual_save.clicked.connect(self.save_points_data_to_file)
        lay_pt_buttons.addWidget(btn_manual_save)

        btn_manual_load = QPushButton("📂 Load Saved Table")
        btn_manual_load.setStyleSheet("background-color: #ffc107; color: black; font-size: 12px; font-weight: bold; padding: 6px;")
        btn_manual_load.clicked.connect(self.load_points_data_from_file)
        lay_pt_buttons.addWidget(btn_manual_load)

        btn_reset_points = QPushButton("🗑 RESET TOURNAMENT POINTS TABLE")
        btn_reset_points.setStyleSheet("background-color: #c62828; color: white; font-size: 12px; font-weight: bold; padding: 6px;")
        btn_reset_points.clicked.connect(self.reset_points_table)
        lay_pt_buttons.addWidget(btn_reset_points)

        lay_pt_main.addLayout(lay_pt_buttons)

        tab_points_table.setLayout(lay_pt_main)
        self.main_tabs.addTab(tab_points_table, "Points Table")

        tab_broadcast_graphics = QWidget()
        lay_bg_main = QVBoxLayout()

        bg_scroll = QScrollArea()
        bg_scroll.setWidgetResizable(True)
        bg_scroll_widget = QWidget()
        lay_bg_content = QVBoxLayout(bg_scroll_widget)

        grp_vmix_conn = QGroupBox("vMix CONNECTION SETTINGS")
        grp_vmix_conn.setStyleSheet("QGroupBox { background-color: #111; color: white; font-weight: bold; font-size: 13px; border: 1px solid #333; padding: 10px; }")
        lay_conn = QHBoxLayout()
        lay_conn.addWidget(QLabel("<font color='white'>vMix Host / IP:</font>"))
        self.txt_vmix_ip = QLineEdit("127.0.0.1")
        self.txt_vmix_ip.setStyleSheet("background-color: white; color: black; font-weight: bold; padding: 4px;")
        lay_conn.addWidget(self.txt_vmix_ip)

        lay_conn.addWidget(QLabel("<font color='white'>API Port:</font>"))
        self.txt_vmix_port = QLineEdit("8088")
        self.txt_vmix_port.setStyleSheet("background-color: white; color: black; font-weight: bold; padding: 4px; max-width: 80px;")
        lay_conn.addWidget(self.txt_vmix_port)

        self.btn_ping_vmix = QPushButton("Ping vMix Connection")
        self.btn_ping_vmix.setStyleSheet("background-color: #4CAF50; color: white; font-weight: bold; padding: 6px 12px;")
        self.btn_ping_vmix.clicked.connect(self.ping_vmix)
        lay_conn.addWidget(self.btn_ping_vmix)
        grp_vmix_conn.setLayout(lay_conn)
        lay_bg_content.addWidget(grp_vmix_conn)

        grp_design_sel = QGroupBox("SCOREBOARD DESIGN SELECTOR")
        grp_design_sel.setStyleSheet("QGroupBox { background-color: #111; color: white; font-weight: bold; font-size: 13px; border: 1px solid #333; padding: 10px; }")
        lay_dsg = QHBoxLayout()
        
        self.btn_dsg1 = QPushButton("⚡ Active Design 1 (Input 17 - Lower Third)")
        self.btn_dsg1.setStyleSheet("background-color: #1976D2; color: white; font-weight: bold; padding: 10px;")
        self.btn_dsg1.clicked.connect(lambda: self.trigger_vmix_overlay_action(17, "Active Design 1"))
        lay_dsg.addWidget(self.btn_dsg1)

        self.btn_dsg2 = QPushButton("⚡ Active Design 2 (Input 18 - Header / Target Bar)")
        self.btn_dsg2.setStyleSheet("background-color: #1976D2; color: white; font-weight: bold; padding: 10px;")
        self.btn_dsg2.clicked.connect(lambda: self.trigger_vmix_overlay_action(18, "Active Design 2"))
        lay_dsg.addWidget(self.btn_dsg2)

        self.btn_hide_score = QPushButton("🚫 Hide Scoreboards")
        self.btn_hide_score.setStyleSheet("background-color: #D32F2F; color: white; font-weight: bold; padding: 10px;")
        self.btn_hide_score.clicked.connect(lambda: self.trigger_vmix_overlay_action(0, "Hide Scoreboards"))
        lay_dsg.addWidget(self.btn_hide_score)

        grp_design_sel.setLayout(lay_dsg)
        lay_bg_content.addWidget(grp_design_sel)

        grp_so_toggle = QGroupBox("SUPER OVER OVERLAY CONTROL (Input 32)")
        grp_so_toggle.setStyleSheet("QGroupBox { background-color: #222; color: white; font-weight: bold; font-size: 13px; border: 1px solid #ff9800; padding: 10px; }")
        lay_so_tog = QHBoxLayout()
        
        self.btn_toggle_so_overlay = QPushButton("⚡ TOGGLE SUPER OVER OVERLAY (INPUT 32) [OFF]")
        self.btn_toggle_so_overlay.setStyleSheet("background-color: #e65100; color: white; font-weight: bold; padding: 12px; font-size: 13px;")
        self.btn_toggle_so_overlay.clicked.connect(self.toggle_super_over_overlay_input32)
        lay_so_tog.addWidget(self.btn_toggle_so_overlay)

        grp_so_toggle.setLayout(lay_so_tog)
        lay_bg_content.addWidget(grp_so_toggle)

        grp_fs_overlays = QGroupBox("FULL SCREEN / SCORECARD OVERLAYS")
        grp_fs_overlays.setStyleSheet("QGroupBox { background-color: #111; color: white; font-weight: bold; font-size: 13px; border: 1px solid #333; padding: 10px; }")
        grid_fs = QGridLayout()

        overlays_list = [
            ("Match Info Toss (Input 2)", 2),
            ("Team Lineup Squads (Input 3)", 3),
            ("Partnership Overlay (Input 4)", 4),
            ("Player Stats Card (Input 5)", 5),
            ("Player Out Overlay (Input 6)", 6),
            ("Inning Break / Target (Input 16)", 16),
            ("1st Batting Card (Input 14)", 14),
            ("1st Bowling Card (Input 15)", 15),
            ("2nd Batting Card (Input 19)", 19),
            ("2nd Bowling Card (Input 20)", 20),
            ("Full Match Summary (Input 21)", 21),
            ("🏆 Win/Loss & Points Table (Input 24)", 24),
            ("🏆 Match Win Screen (Input 29)", 29),
            ("⭐ Batsman 50/100 Celebration (Input 27)", 27),
            ("⭐ Bowler 5-Wicket Celebration (Input 28)", 28)
        ]

        for idx, (title, inp_num) in enumerate(overlays_list):
            btn = QPushButton(title)
            btn.setStyleSheet("background-color: #263238; color: white; font-weight: bold; padding: 12px; border: 1px solid #455A64; border-radius: 4px;")
            btn.clicked.connect(lambda checked, num=inp_num, t=title: self.toggle_vmix_input(num, t))
            grid_fs.addWidget(btn, idx // 2, idx % 2)

        grp_fs_overlays.setLayout(grid_fs)
        lay_bg_content.addWidget(grp_fs_overlays)

        grp_instant = QGroupBox("INSTANT ANIMATIONS & CELEBRATIONS")
        grp_instant.setStyleSheet("QGroupBox { background-color: #111; color: white; font-weight: bold; font-size: 13px; border: 1px solid #333; padding: 10px; }")
        grid_instant = QGridLayout()

        instant_list = [
            ("FOUR Boundary (Input 7)", 7, "#E65100"),
            ("SIX Boundary (Input 8)", 8, "#673AB7"),
            ("WICKET Overlay (Input 22)", 22, "#C62828"),
            ("RUN OUT Overlay (Input 9)", 9, "#C62828"),
            ("WIDE BALL Overlay (Input 23)", 23, "#0288D1"),
            ("FREE HIT Animation (Input 11)", 11, "#E65100"),
            ("⭐ Batsman 50/100 Celebration (Input 27)", 27, "#E65100"),
            ("⭐ Bowler 5-Wicket Celebration (Input 28)", 28, "#E65100")
        ]

        for idx, (title, target_ref, color_code) in enumerate(instant_list):
            btn = QPushButton(title)
            btn.setStyleSheet(f"background-color: {color_code}; color: white; font-weight: bold; padding: 12px; border-radius: 4px;")
            if isinstance(target_ref, int):
                btn.clicked.connect(lambda checked, num=target_ref, t=title: self.toggle_vmix_input(num, t))
            else:
                btn.clicked.connect(lambda checked, ref=target_ref, t=title: self.trigger_vmix_gtzip(ref, t))
            grid_instant.addWidget(btn, idx // 2, idx % 2)

        grp_instant.setLayout(grid_instant)
        lay_bg_content.addWidget(grp_instant)

        self.btn_take_all_out = QPushButton("🚨 TAKE ALL OVERLAYS OUT (SLOT 1, 2, 3, 4)")
        self.btn_take_all_out.setStyleSheet("background-color: #B71C1C; color: white; font-weight: bold; font-size: 14px; padding: 15px; border-radius: 6px;")
        self.btn_take_all_out.clicked.connect(self.take_all_overlays_out)
        lay_bg_content.addWidget(self.btn_take_all_out)

        bg_scroll.setWidget(bg_scroll_widget)
        lay_bg_main.addWidget(bg_scroll)
        tab_broadcast_graphics.setLayout(lay_bg_main)
        self.main_tabs.addTab(tab_broadcast_graphics, "vMix Broadcast Graphics")

        main_master_layout.addWidget(self.main_tabs)
        self.setLayout(main_master_layout)

        self.txt_team1.textChanged.connect(self.on_team_change)
        self.txt_team2.textChanged.connect(self.on_team_change)
        self.txt_match_overs.textChanged.connect(self.update_score)
        self.cmb_toss_winner.currentIndexChanged.connect(self.update_toss_text)
        self.cmb_toss_choice.currentIndexChanged.connect(self.update_toss_text)
        self.txt_toss_details.textChanged.connect(self.sync_toss_to_vmix)

        for txt in self.team1_inputs + self.team2_inputs:
            txt.textChanged.connect(self.refresh_active_players_dropdowns)

        self.update_team_combos()
        self.refresh_active_players_dropdowns()
        self.load_milestones_data_to_table()
        self.load_bowler_milestones_data_to_table()
        self.load_tournament_4s6s_data()
        self.tournament_schedule_data = {"teams": [], "matches": [], "reentry": []}
        self._tournament_undo_stacks = {"schedule": [], "reentry": []}
        self._tournament_pending_undo = {"schedule": None, "reentry": None}
        self.load_custom_tournament()
        self.group_tournament_data = {"groups": [], "matches": [], "knockout_generated": False}
        self._refreshing_group_schedule = False
        self.load_group_tournament()

    def _tournament_data_path(self):
        return os.path.join(os.path.expanduser("~/Documents"), "custom_tournament_schedule.json")

    def save_custom_tournament(self):
        try:
            with open(self._tournament_data_path(), "w", encoding="utf-8") as f:
                json.dump(self.tournament_schedule_data, f, ensure_ascii=False, indent=4)
        except Exception as e:
            QMessageBox.critical(self, "Save Error", f"Tournament schedule save झाला नाही:\n{e}")

    def load_custom_tournament(self):
        try:
            path = self._tournament_data_path()
            if os.path.exists(path):
                with open(path, "r", encoding="utf-8") as f:
                    data = json.load(f)
                if isinstance(data, dict):
                    self.tournament_schedule_data = data
            self.refresh_custom_tournament_tables()
        except Exception as e:
            print(f"Tournament schedule load error: {e}")

    def refresh_custom_tournament_tables(self):
        if not hasattr(self, "tbl_tournament_schedule"):
            return
        self._refreshing_tournament_tables = True
        matches = self.tournament_schedule_data.get("matches", [])
        self.tbl_tournament_schedule.setRowCount(len(matches))
        for r, m in enumerate(matches):
            vals = [m.get(k, "") for k in ("round", "match", "date", "time", "team_a", "team_b", "winner")]
            for c, val in enumerate(vals):
                self.tbl_tournament_schedule.setItem(r, c, QTableWidgetItem(str(val)))
        re_matches = self.tournament_schedule_data.get("reentry", [])
        self.tbl_reentry.setRowCount(len(re_matches))
        for r, m in enumerate(re_matches):
            vals = [m.get(k, "") for k in ("match", "date", "time", "team_a", "team_b", "winner", "status")]
            for c, val in enumerate(vals):
                self.tbl_reentry.setItem(r, c, QTableWidgetItem(str(val)))
        self._refreshing_tournament_tables = False

    def _prepare_tournament_cell_undo(self, section):
        """Keep the pre-edit tournament state; commit it only if a cell changes."""
        self._tournament_pending_undo[section] = copy.deepcopy(self.tournament_schedule_data)

    def _push_tournament_undo(self, section):
        """Save a full bracket snapshot in the selected tab's independent history."""
        stack = self._tournament_undo_stacks[section]
        stack.append(copy.deepcopy(self.tournament_schedule_data))
        if len(stack) > 50:
            stack.pop(0)
        self._update_tournament_undo_buttons()

    def _commit_pending_tournament_undo(self, section):
        snapshot = self._tournament_pending_undo.get(section)
        self._tournament_pending_undo[section] = None
        if snapshot is not None:
            stack = self._tournament_undo_stacks[section]
            stack.append(snapshot)
            if len(stack) > 50:
                stack.pop(0)
            self._update_tournament_undo_buttons()

    def _update_tournament_undo_buttons(self):
        if hasattr(self, "btn_undo_tournament_schedule"):
            self.btn_undo_tournament_schedule.setEnabled(bool(self._tournament_undo_stacks["schedule"]))
        if hasattr(self, "btn_undo_reentry"):
            self.btn_undo_reentry.setEnabled(bool(self._tournament_undo_stacks["reentry"]))

    def undo_tournament_action(self, section):
        """Undo the last change made from the selected tournament tab."""
        stack = self._tournament_undo_stacks.get(section, [])
        if not stack:
            QMessageBox.information(self, "Undo", "या tab मध्ये Undo करण्यासाठी action उपलब्ध नाही.")
            self._update_tournament_undo_buttons()
            return

        answer = QMessageBox.question(
            self, "Confirm Undo",
            "या tab मधील शेवटचा Tournament बदल Undo करायचा आहे का?",
            QMessageBox.Yes | QMessageBox.No, QMessageBox.Yes
        )
        if answer != QMessageBox.Yes:
            return

        self.tournament_schedule_data = stack.pop()
        self._tournament_pending_undo[section] = None
        self.save_custom_tournament()
        self.refresh_custom_tournament_tables()
        self._update_tournament_undo_buttons()
        QMessageBox.information(self, "Undo Complete", "शेवटचा बदल Undo झाला आहे.")

    def on_custom_tournament_cell_changed(self, section, item):
        if getattr(self, "_refreshing_tournament_tables", False):
            return
        key = "matches" if section == "schedule" else "reentry"
        fields = ["round", "match", "date", "time", "team_a", "team_b", "winner"] if section == "schedule" else ["match", "date", "time", "team_a", "team_b", "winner", "status"]
        rows = self.tournament_schedule_data.get(key, [])
        if 0 <= item.row() < len(rows) and 0 <= item.column() < len(fields):
            self._commit_pending_tournament_undo(section)
            rows[item.row()][fields[item.column()]] = item.text().strip()
            self.save_custom_tournament()
            if section == "schedule" and fields[item.column()] == "winner":
                if rows[item.row()].get("round") == "1st Round":
                    self._rebuild_reentry_from_first_round()
                self._advance_knockout_rounds()
                self.refresh_custom_tournament_tables()
            elif section == "reentry" and fields[item.column()] == "winner":
                self._advance_knockout_rounds()
                self.refresh_custom_tournament_tables()

    def create_custom_tournament(self):
        count, ok = QInputDialog.getInt(self, "Custom Tournament", "किती टीम्सचा Tournament बनवायचा?", 8, 2, 64, 1)
        if not ok:
            return
        teams = []
        for i in range(count):
            name, ok = QInputDialog.getText(self, "Team Names", f"Team {i+1} चे नाव:")
            if not ok:
                return
            name = name.strip()
            if not name:
                QMessageBox.warning(self, "Team Name Required", "Team चे नाव रिकामे ठेवू नका.")
                return
            teams.append(name)
        matches = []
        # First-round knockout fixtures. Odd team counts receive one BYE.
        round_teams = teams[:]
        if len(round_teams) % 2:
            round_teams.append("BYE")
        for i in range(0, len(round_teams), 2):
            a, b = round_teams[i], round_teams[i+1]
            winner = a if b == "BYE" else (b if a == "BYE" else "")
            matches.append({"round": "1st Round", "match": f"R1-{i//2+1}", "date": "", "time": "", "team_a": a, "team_b": b, "winner": winner})
        self._push_tournament_undo("schedule")
        self.tournament_schedule_data = {"teams": teams, "matches": matches, "reentry": []}
        self._rebuild_reentry_from_first_round()
        self.save_custom_tournament()
        self.refresh_custom_tournament_tables()
        QMessageBox.information(self, "Tournament Created", f"{count} टीम्सचा 1st Round Schedule तयार झाला. Date आणि Time table मध्ये भरू शकता.")

    def _rebuild_reentry_from_first_round(self):
        losers = []
        for m in self.tournament_schedule_data.get("matches", []):
            if m.get("round") == "1st Round" and m.get("winner"):
                a, b, w = m.get("team_a", ""), m.get("team_b", ""), m.get("winner", "")
                loser = b if w == a else a if w == b else ""
                if loser and loser != "BYE":
                    losers.append(loser)
        reentry = []
        if len(losers) % 2:
            losers.append("BYE")
        for i in range(0, len(losers), 2):
            a, b = losers[i], losers[i+1]
            w = a if b == "BYE" else (b if a == "BYE" else "")
            reentry.append({"match": f"RE-{i//2+1}", "date": "", "time": "", "team_a": a, "team_b": b, "winner": w, "status": "BYE" if "BYE" in (a,b) else "Scheduled"})
        self.tournament_schedule_data["reentry"] = reentry

    def _round_label_for_count(self, team_count):
        """Name the next knockout stage from the number of teams entering it."""
        if team_count == 8:
            return "Quarter Final"
        if team_count == 4:
            return "Semi Final"
        if team_count == 2:
            return "Final"
        return f"Round of {team_count}"

    def _make_knockout_round(self, teams, round_name, existing_matches):
        """Create fixtures for one stage, retaining saved date/time for unchanged fixtures."""
        old_by_id = {
            m.get("match"): m for m in existing_matches
            if m.get("round") == round_name
        }
        stage = []
        stage_teams = list(teams)
        if len(stage_teams) % 2:
            stage_teams.append("BYE")
        for i in range(0, len(stage_teams), 2):
            a, b = stage_teams[i], stage_teams[i + 1]
            match_id = f"{round_name}-{i // 2 + 1}"
            old = old_by_id.get(match_id, {})
            same_pair = (
                old.get("team_a") == a and old.get("team_b") == b
            )
            stage.append({
                "round": round_name,
                "match": match_id,
                "date": old.get("date", "") if same_pair else "",
                "time": old.get("time", "") if same_pair else "",
                "team_a": a,
                "team_b": b,
                "winner": (old.get("winner", "") if same_pair else ""),
            })
            if b == "BYE":
                stage[-1]["winner"] = a
        return stage

    def _advance_knockout_rounds(self):
        """
        Generate the next knockout stage automatically.
        First-stage qualifiers are 1st Round winners plus Re-Entry winners.
        Every later stage is fed by the previous stage's winners.
        """
        data = self.tournament_schedule_data
        original = list(data.get("matches", []))
        first = [m for m in original if m.get("round") == "1st Round"]
        if not first or any(not m.get("winner") for m in first):
            data["matches"] = first
            return

        # Re-entry is a second-chance path: all re-entry fixtures must be decided
        # before their winners can join the main knockout bracket.
        reentry = data.get("reentry", [])
        if reentry and any(not m.get("winner") for m in reentry):
            data["matches"] = first
            return

        qualifiers = [m["winner"] for m in first if m.get("winner") and m["winner"] != "BYE"]
        qualifiers.extend(
            m["winner"] for m in reentry
            if m.get("winner") and m["winner"] != "BYE"
        )

        rebuilt = first[:]
        prior_winners = qualifiers
        old_matches = original[:]
        stage_number = 2
        while len(prior_winners) > 1:
            round_name = self._round_label_for_count(len(prior_winners))
            # Avoid duplicate labels if an unusual team count produces same stage name.
            stage_matches = self._make_knockout_round(prior_winners, round_name, old_matches)
            rebuilt.extend(stage_matches)
            if any(not m.get("winner") for m in stage_matches):
                break
            prior_winners = [m["winner"] for m in stage_matches if m.get("winner") != "BYE"]
            stage_number += 1
            if stage_number > 12:
                break

        data["matches"] = rebuilt

    def set_tournament_match_winner(self, section):
        table = self.tbl_tournament_schedule if section == "schedule" else self.tbl_reentry
        row = table.currentRow()
        if row < 0:
            QMessageBox.warning(self, "Select Match", "आधी table मधील Match select करा.")
            return
        data_key = "matches" if section == "schedule" else "reentry"
        matches = self.tournament_schedule_data.get(data_key, [])
        if row >= len(matches):
            return
        m = matches[row]
        options = [x for x in [m.get("team_a", ""), m.get("team_b", "")] if x and x != "BYE"]
        if not options:
            return
        winner, ok = QInputDialog.getItem(self, "Match Result", "Winner Team निवडा:", options, 0, False)
        if not ok:
            return
        self._push_tournament_undo(section)
        m["winner"] = winner
        if section == "reentry":
            m["status"] = "Completed"
        # Any result change can alter the bracket; rebuild later rounds from the
        # current first-round and re-entry results to prevent stale fixtures.
        if section == "schedule":
            round_name = m.get("round", "")
            if round_name == "1st Round":
                self._rebuild_reentry_from_first_round()
            self._advance_knockout_rounds()
        else:
            self._advance_knockout_rounds()
        self.save_custom_tournament()
        self.refresh_custom_tournament_tables()

    def reset_custom_tournament(self):
        ans = QMessageBox.question(self, "Confirm Reset", "पूर्ण Tournament Schedule आणि Teams delete करायचे का?", QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
        if ans != QMessageBox.Yes:
            return
        self._push_tournament_undo("schedule")
        self.tournament_schedule_data = {"teams": [], "matches": [], "reentry": []}
        self.save_custom_tournament()
        self.refresh_custom_tournament_tables()

    def reset_reentry_only(self):
        ans = QMessageBox.question(self, "Confirm Reset", "फक्त Re-Entry records reset करायचे का? Main Tournament Schedule सुरक्षित राहील.", QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
        if ans != QMessageBox.Yes:
            return
        self._push_tournament_undo("reentry")
        self.tournament_schedule_data["reentry"] = []
        self.save_custom_tournament()
        self.refresh_custom_tournament_tables()

    def _group_tournament_data_path(self):
        return os.path.join(os.path.expanduser("~/Documents"), "group_match_schedule.json")

    def save_group_tournament(self):
        try:
            with open(self._group_tournament_data_path(), "w", encoding="utf-8") as f:
                json.dump(self.group_tournament_data, f, ensure_ascii=False, indent=4)
        except Exception as e:
            QMessageBox.critical(self, "Save Error", f"Group Schedule save झाला नाही:\n{e}")

    def load_group_tournament(self):
        try:
            path = self._group_tournament_data_path()
            if os.path.exists(path):
                with open(path, "r", encoding="utf-8") as f:
                    data = json.load(f)
                if isinstance(data, dict):
                    self.group_tournament_data = data
            self.refresh_group_schedule_tables()
        except Exception as e:
            print(f"Group schedule load error: {e}")

    def create_group_tournament(self):
        count, ok = QInputDialog.getInt(self, "Group Setup", "किती Groups बनवायचे?", 2, 1, 16, 1)
        if not ok:
            return
        groups = []
        all_team_names = set()
        for gi in range(count):
            default_name = f"Group {chr(65 + gi)}" if gi < 26 else f"Group {gi + 1}"
            name, ok = QInputDialog.getText(self, "Group Name", f"Group {gi + 1} चे नाव:", text=default_name)
            if not ok:
                return
            name = name.strip()
            if not name:
                QMessageBox.warning(self, "Group Name", "Group चे नाव रिकामे ठेवू नका.")
                return
            if any(g["name"].casefold() == name.casefold() for g in groups):
                QMessageBox.warning(self, "Group Name", "प्रत्येक Group चे नाव वेगळे असावे.")
                return

            team_count, ok = QInputDialog.getInt(self, name, f"{name} मध्ये किती Teams असतील?", 4, 2, 32, 1)
            if not ok:
                return
            teams = []
            for ti in range(team_count):
                while True:
                    team, ok = QInputDialog.getText(self, "Team Names", f"{name} – Team {ti + 1} चे नाव:")
                    if not ok:
                        return
                    team = team.strip()
                    if not team:
                        QMessageBox.warning(self, "Team Name", "Team चे नाव रिकामे ठेवू नका.")
                        continue
                    if team.casefold() in all_team_names or any(t.casefold() == team.casefold() for t in teams):
                        QMessageBox.warning(self, "Team Name", "प्रत्येक Team चे नाव संपूर्ण Tournament मध्ये वेगळे असावे.")
                        continue
                    teams.append(team)
                    all_team_names.add(team.casefold())
                    break

            # समान सामने खेळण्यासाठी प्रत्येक Group मध्ये सर्व Teams चा degree समान असणे आवश्यक.
            # Odd team count असल्यास प्रत्येक Team चे सामने सम संख्येतच असू शकतात.
            default_games = min(team_count - 1, 4)
            if team_count % 2 == 1 and default_games % 2:
                default_games -= 1
            while True:
                games, ok = QInputDialog.getInt(
                    self, name,
                    f"प्रत्येक Team किती Matches खेळणार? (सर्व Teams समान Matches खेळतील; 1 ते 31)",
                    max(2, default_games), 1, 31, 1
                )
                if not ok:
                    return
                if team_count % 2 == 1 and games % 2 == 1:
                    QMessageBox.warning(
                        self, "Match Format",
                        f"{name} मध्ये {team_count} Teams आहेत. सर्व Teams ना समान सामने देण्यासाठी Matches ची संख्या सम असावी (2, 4, 6...). कृपया पुन्हा निवडा."
                    )
                    continue
                break

            qualify, ok = QInputDialog.getInt(self, name, "या Group मधून Knockout साठी किती Teams Qualify होतील?", 2, 1, team_count, 1)
            if not ok:
                return
            groups.append({"name": name, "teams": teams, "matches_per_team": games, "qualify": qualify})

        fixtures = []
        for group in groups:
            teams = group["teams"]
            team_count = len(teams)
            remaining_games = group["matches_per_team"]
            match_no = 1
            cycle_no = 1

            # Regular (equal-degree) fixture generation. For odd team counts,
            # an equal number of matches per team must be even. Repeated cycles
            # are allowed when requested matches exceed unique opponents.
            def pairings_for_degree(n, degree):
                pairs = []
                if n % 2 == 1:
                    for offset in range(1, degree // 2 + 1):
                        for i in range(n):
                            j = (i + offset) % n
                            if i < j:
                                pairs.append((i, j))
                            else:
                                pairs.append((j, i))
                else:
                    regular_offsets = degree // 2
                    for offset in range(1, regular_offsets + 1):
                        for i in range(n):
                            j = (i + offset) % n
                            if i < j:
                                pairs.append((i, j))
                            else:
                                pairs.append((j, i))
                    if degree % 2:
                        opposite = n // 2
                        for i in range(n // 2):
                            pairs.append((i, i + opposite))
                # Each undirected pairing appears once in this cycle.
                unique = []
                seen = set()
                for a_idx, b_idx in pairs:
                    key = (min(a_idx, b_idx), max(a_idx, b_idx))
                    if key not in seen:
                        seen.add(key)
                        unique.append(key)
                return unique

            while remaining_games > 0:
                cycle_degree = min(remaining_games, team_count - 1)
                # An odd-sized group cannot have an odd regular degree.
                if team_count % 2 == 1 and cycle_degree % 2:
                    cycle_degree -= 1
                if cycle_degree <= 0:
                    break
                for a_idx, b_idx in pairings_for_degree(team_count, cycle_degree):
                    fixtures.append({
                        "group": group["name"], "round": "Group Stage",
                        "match": f"{group['name']}-M{match_no}",
                        "date": "", "time": "", "team_a": teams[a_idx],
                        "team_b": teams[b_idx], "venue": "", "winner": "",
                        "status": "Scheduled", "cycle": cycle_no
                    })
                    match_no += 1
                remaining_games -= cycle_degree
                cycle_no += 1

        self.group_tournament_data = {"groups": groups, "matches": fixtures, "knockout_generated": False}
        self.save_group_tournament()
        self.refresh_group_schedule_tables()
        QMessageBox.information(
            self, "Group Schedule Created",
            "Group Stage Schedule तयार झाले. प्रत्येक Group मधील सर्व Teams समान Matches खेळतील. "
            "Date, Time आणि Venue table मध्ये थेट edit करू शकता. सर्व Group matches चे winners दिल्यावर Knockout ते Final आपोआप तयार होईल."
        )

    def refresh_group_schedule_tables(self):
        if not hasattr(self, "tbl_group_schedule"):
            return
        data = self.group_tournament_data
        self._refreshing_group_schedule = True
        matches = data.get("matches", [])
        self.tbl_group_schedule.setRowCount(len(matches))
        for r, match in enumerate(matches):
            vals = [match.get(k, "") for k in ("group", "round", "match", "date", "time", "team_a", "team_b", "venue", "winner")]
            for c, value in enumerate(vals):
                self.tbl_group_schedule.setItem(r, c, QTableWidgetItem(str(value)))
        self._refreshing_group_schedule = False

        # Build one compact broadcast-style block per group in the right-side panel.
        point_rows = []
        for group in data.get("groups", []):
            group_matches = [m for m in matches if m.get("group") == group["name"] and m.get("round") == "Group Stage"]
            stats = {team: {"played": 0, "won": 0, "lost": 0, "points": 0, "nr": 0} for team in group["teams"]}
            for m in group_matches:
                winner = m.get("winner", "")
                a, b = m.get("team_a", ""), m.get("team_b", "")
                if winner and a in stats and b in stats:
                    stats[a]["played"] += 1
                    stats[b]["played"] += 1
                    if winner in stats:
                        stats[winner]["won"] += 1
                        stats[winner]["points"] += 2
                        loser = b if winner == a else a
                        stats[loser]["lost"] += 1
            ranked = sorted(group["teams"], key=lambda t: (-stats[t]["points"], -stats[t]["won"], t.lower()))
            point_rows.append(("GROUP", group.get("name", "GROUP")))
            for pos, team in enumerate(ranked, 1):
                st = stats[team]
                # NRR needs innings runs/overs; don't fabricate it from winner-only data.
                point_rows.append(("TEAM", (pos, team, st["played"], st["won"], st["lost"], st["nr"], st["points"], "—")))
        self.tbl_group_points.clearSpans()
        self.tbl_group_points.setRowCount(len(point_rows))
        for r, entry in enumerate(point_rows):
            kind, payload = entry
            if kind == "GROUP":
                item = QTableWidgetItem(str(payload).upper())
                item.setTextAlignment(Qt.AlignCenter)
                item.setBackground(QColor("#d71920"))
                item.setForeground(QColor("#ffffff"))
                font = item.font(); font.setBold(True); item.setFont(font)
                self.tbl_group_points.setItem(r, 0, item)
                self.tbl_group_points.setSpan(r, 0, 1, 8)
                self.tbl_group_points.setRowHeight(r, 23)
            else:
                for c, value in enumerate(payload):
                    item = QTableWidgetItem(str(value))
                    item.setTextAlignment(Qt.AlignCenter if c != 1 else Qt.AlignVCenter | Qt.AlignLeft)
                    item.setForeground(QColor("#ffffff"))
                    item.setBackground(QColor("#064ca8"))
                    self.tbl_group_points.setItem(r, c, item)
                self.tbl_group_points.setRowHeight(r, 22)

    def on_group_schedule_cell_changed(self, item):
        if self._refreshing_group_schedule:
            return
        matches = self.group_tournament_data.get("matches", [])
        fields = ["group", "round", "match", "date", "time", "team_a", "team_b", "venue", "winner"]
        if 0 <= item.row() < len(matches) and 0 <= item.column() < len(fields):
            matches[item.row()][fields[item.column()]] = item.text().strip()
            self.save_group_tournament()
            self.refresh_group_schedule_tables()

    def set_group_match_winner(self):
        row = self.tbl_group_schedule.currentRow()
        matches = self.group_tournament_data.get("matches", [])
        if row < 0 or row >= len(matches):
            QMessageBox.warning(self, "Select Match", "आधी Group Schedule मधील Match select करा.")
            return
        match = matches[row]
        options = [x for x in (match.get("team_a", ""), match.get("team_b", "")) if x and x != "BYE"]
        if not options:
            return
        winner, ok = QInputDialog.getItem(self, "Match Result", "Winner Team निवडा:", options, 0, False)
        if not ok:
            return
        match["winner"] = winner
        match["status"] = "Completed"
        if match.get("round") == "Group Stage":
            self._generate_group_knockout_if_ready()
        else:
            self._advance_group_knockout()
        self.save_group_tournament()
        self.refresh_group_schedule_tables()

    def _generate_group_knockout_if_ready(self):
        data = self.group_tournament_data
        group_matches = [m for m in data.get("matches", []) if m.get("round") == "Group Stage"]
        if not group_matches or any(not m.get("winner") for m in group_matches):
            return
        if data.get("knockout_generated"):
            return
        qualifiers = []
        for group in data.get("groups", []):
            gm = [m for m in group_matches if m.get("group") == group["name"]]
            stats = {team: {"points": 0, "won": 0} for team in group["teams"]}
            for m in gm:
                w = m.get("winner", "")
                if w in stats:
                    stats[w]["points"] += 2
                    stats[w]["won"] += 1
            ranked = sorted(group["teams"], key=lambda t: (-stats[t]["points"], -stats[t]["won"], t.lower()))
            qualifiers.extend({"team": team, "group": group["name"], "seed": i + 1} for i, team in enumerate(ranked[:group["qualify"]]))
        teams = [q["team"] for q in qualifiers]
        if len(teams) < 2:
            QMessageBox.warning(self, "Knockout", "Knockout साठी किमान 2 qualifiers आवश्यक आहेत.")
            return
        self.group_tournament_data["qualifiers"] = qualifiers
        first_round = "Final" if len(teams) == 2 else ("Semi Final" if len(teams) == 4 else ("Quarter Final" if len(teams) == 8 else "Knockout Round"))
        self.group_tournament_data["matches"].extend(self._build_group_knockout_round(teams, first_round))
        self.group_tournament_data["knockout_generated"] = True

    def _build_group_knockout_round(self, teams, round_name):
        stage_teams = list(teams)
        # Pad to the next power of two; BYEs advance automatically.
        size = 1
        while size < len(stage_teams):
            size *= 2
        stage_teams.extend(["BYE"] * (size - len(stage_teams)))
        fixtures = []
        for i in range(0, len(stage_teams), 2):
            a, b = stage_teams[i], stage_teams[i + 1]
            winner = a if b == "BYE" else (b if a == "BYE" else "")
            fixtures.append({"group": "Knockout", "round": round_name, "match": f"{round_name}-{i//2+1}", "date": "", "time": "", "team_a": a, "team_b": b, "venue": "", "winner": winner, "status": "BYE" if "BYE" in (a, b) else "Scheduled"})
        return fixtures

    def _advance_group_knockout(self):
        """Advance only the winners of the latest completed knockout round.

        Earlier-round winners must not be mixed with the current round's
        winners; doing so can create duplicate rounds after the Final.
        """
        data = self.group_tournament_data
        matches = data.get("matches", [])
        knockout = [m for m in matches if m.get("round") != "Group Stage"]
        if not knockout:
            return

        # Repair schedules created by the older buggy version: it could append
        # extra rounds after a Final. Keep the Final and discard everything below it.
        final_index = next(
            (i for i, m in enumerate(matches) if m.get("round", "").strip().lower() == "final"),
            None
        )
        if final_index is not None:
            del matches[final_index + 1:]
            return

        # The most recently appended knockout stage is the active stage.
        latest_round = knockout[-1].get("round", "")
        current_round = [m for m in knockout if m.get("round") == latest_round]
        if not current_round or any(not m.get("winner") for m in current_round):
            return

        winners = [
            m.get("winner", "") for m in current_round
            if m.get("winner") and m.get("winner") != "BYE"
        ]

        # A completed Final or a single remaining champion ends the tournament.
        if len(winners) <= 1:
            return

        round_name = (
            "Final" if len(winners) == 2 else
            "Semi Final" if len(winners) == 4 else
            "Quarter Final" if len(winners) == 8 else
            f"Round of {len(winners)}"
        )

        # Never append a stage that already exists.
        if any(m.get("round") == round_name for m in knockout):
            return

        matches.extend(self._build_group_knockout_round(winners, round_name))

    def reset_group_tournament(self):
        answer = QMessageBox.question(self, "Reset Group Schedule", "Group configuration, fixtures, results आणि points table reset करायचे का?", QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
        if answer != QMessageBox.Yes:
            return
        self.group_tournament_data = {"groups": [], "matches": [], "knockout_generated": False}
        self.save_group_tournament()
        self.refresh_group_schedule_tables()

    def load_tournament_fours_counter(self):
        """Restore the all-tournament fours count from disk."""
        try:
            os.makedirs(os.path.dirname(self.tournament_fours_file), exist_ok=True)
            if os.path.exists(self.tournament_fours_file):
                with open(self.tournament_fours_file, "r", encoding="utf-8") as f:
                    data = json.load(f)
                self.tournament_fours_count = max(0, int(data.get("count", 0))) if isinstance(data, dict) else 0
        except Exception as e:
            print(f"Tournament Fours counter load error: {e}")
            self.tournament_fours_count = 0

    def save_tournament_fours_counter(self):
        """Atomically save the all-tournament fours count."""
        try:
            os.makedirs(os.path.dirname(self.tournament_fours_file), exist_ok=True)
            temp_path = self.tournament_fours_file + ".tmp"
            with open(temp_path, "w", encoding="utf-8") as f:
                json.dump({"count": int(self.tournament_fours_count)}, f, ensure_ascii=False, indent=2)
            os.replace(temp_path, self.tournament_fours_file)
        except Exception as e:
            print(f"Tournament Fours counter save error: {e}")

    def update_tournament_fours_vmix(self, trigger_overlay=False):
        """Write the three counter digits to GT Designer/vMix Input 33."""
        try:
            digits = f"{max(0, int(self.tournament_fours_count)):03d}"
            self.send_to_vmix(33, "DIGIT1.Text", digits[-3])
            self.send_to_vmix(33, "DIGIT2.Text", digits[-2])
            self.send_to_vmix(33, "DIGIT3.Text", digits[-1])
            if trigger_overlay:
                self.trigger_timed_overlay(33, "Tournament Fours Counter (Input 33)", 8000, overlay_channel=3)
        except Exception as e:
            print(f"Tournament Fours vMix update error: {e}")

    def record_tournament_four(self):
        """Increment and persist the tournament-wide fours counter."""
        self.tournament_fours_count += 1
        self.save_tournament_fours_counter()
        self.update_tournament_fours_vmix(trigger_overlay=True)

    def load_tournament_sixes_counter(self):
        """Restore the all-tournament sixes count from disk."""
        try:
            os.makedirs(os.path.dirname(self.tournament_sixes_file), exist_ok=True)
            if os.path.exists(self.tournament_sixes_file):
                with open(self.tournament_sixes_file, "r", encoding="utf-8") as f:
                    data = json.load(f)
                self.tournament_sixes_count = max(0, int(data.get("count", 0))) if isinstance(data, dict) else 0
        except Exception as e:
            print(f"Tournament Sixes counter load error: {e}")
            self.tournament_sixes_count = 0

    def save_tournament_sixes_counter(self):
        """Atomically save the all-tournament sixes count."""
        try:
            os.makedirs(os.path.dirname(self.tournament_sixes_file), exist_ok=True)
            temp_path = self.tournament_sixes_file + ".tmp"
            with open(temp_path, "w", encoding="utf-8") as f:
                json.dump({"count": int(self.tournament_sixes_count)}, f, ensure_ascii=False, indent=2)
            os.replace(temp_path, self.tournament_sixes_file)
        except Exception as e:
            print(f"Tournament Sixes counter save error: {e}")

    def update_tournament_sixes_vmix(self, trigger_overlay=False):
        """Write the three counter digits to GT Designer/vMix Input 34."""
        try:
            digits = f"{max(0, int(self.tournament_sixes_count)):03d}"
            self.send_to_vmix(34, "DIGIT1.Text", digits[-3])
            self.send_to_vmix(34, "DIGIT2.Text", digits[-2])
            self.send_to_vmix(34, "DIGIT3.Text", digits[-1])
            if trigger_overlay:
                self.trigger_timed_overlay(
                    34, "Tournament Sixes Counter (Input 34)", 8000,
                    overlay_channel=4
                )
        except Exception as e:
            print(f"Tournament Sixes vMix update error: {e}")

    def record_tournament_six(self):
        """Increment and persist the tournament-wide sixes counter."""
        self.tournament_sixes_count += 1
        self.save_tournament_sixes_counter()
        self.update_tournament_sixes_vmix(trigger_overlay=True)

    def load_tournament_4s6s_data(self):
        try:
            os.makedirs(os.path.dirname(self.tournament_4s6s_file), exist_ok=True)
            if os.path.exists(self.tournament_4s6s_file):
                with open(self.tournament_4s6s_file, "r", encoding="utf-8") as f:
                    loaded = json.load(f)
                self.tournament_4s6s_data = loaded if isinstance(loaded, dict) else {}
        except Exception as e:
            print(f"Tournament 4S/6S load error: {e}")
            self.tournament_4s6s_data = {}
        self.update_tournament_4s6s_table()

    def save_tournament_4s6s_data(self):
        try:
            os.makedirs(os.path.dirname(self.tournament_4s6s_file), exist_ok=True)
            temp_path = self.tournament_4s6s_file + ".tmp"
            with open(temp_path, "w", encoding="utf-8") as f:
                json.dump(self.tournament_4s6s_data, f, ensure_ascii=False, indent=2)
            os.replace(temp_path, self.tournament_4s6s_file)
        except Exception as e:
            print(f"Tournament 4S/6S save error: {e}")

    def record_tournament_batting(self, player_name, runs=0, balls=0, fours=0, sixes=0):
        player_name = (player_name or "").strip()
        if not player_name:
            return
        batting_team = self.get_batting_bowling_teams()[0].strip() or "TEAM"
        key = f"{batting_team}||{player_name}"
        rec = self.tournament_4s6s_data.setdefault(key, {
            "player": player_name, "team": batting_team,
            "runs": 0, "balls": 0, "4s": 0, "6s": 0
        })
        rec["runs"] = int(rec.get("runs", 0)) + int(runs)
        rec["balls"] = int(rec.get("balls", 0)) + int(balls)
        rec["4s"] = int(rec.get("4s", 0)) + int(fours)
        rec["6s"] = int(rec.get("6s", 0)) + int(sixes)
        self.save_tournament_4s6s_data()
        self.update_tournament_4s6s_table()

    def update_tournament_4s6s_table(self):
        if not hasattr(self, "tbl_tournament_4s6s"):
            return
        records = sorted(
            self.tournament_4s6s_data.values(),
            key=lambda x: (int(x.get("6s", 0)), int(x.get("4s", 0)), x.get("player", "").lower()),
            reverse=True
        )
        self.tbl_tournament_4s6s.setRowCount(len(records))
        for row, rec in enumerate(records):
            runs = int(rec.get("runs", 0))
            balls = int(rec.get("balls", 0))
            sr = (runs * 100.0 / balls) if balls else 0.0
            values = [str(row + 1), rec.get("player", ""), rec.get("team", ""),
                      str(rec.get("4s", 0)), str(rec.get("6s", 0)), f"{sr:.2f}"]
            for col, value in enumerate(values):
                item = QTableWidgetItem(value)
                item.setTextAlignment(Qt.AlignCenter)
                self.tbl_tournament_4s6s.setItem(row, col, item)

    def reset_tournament_4s6s(self):
        answer = QMessageBox.question(
            self, "Confirm Tournament Record Reset",
            "Are you sure you want to permanently delete ALL tournament 4s/6s records?\n"
            "This will not reset the current match score.",
            QMessageBox.Yes | QMessageBox.No, QMessageBox.No
        )
        if answer != QMessageBox.Yes:
            return
        self.tournament_4s6s_data = {}
        self.save_tournament_4s6s_data()
        self.update_tournament_4s6s_table()
        QMessageBox.information(self, "Tournament Record", "Tournament 4s/6s records have been reset.")

    def reset_tournament_boundary_counters(self):
        """Reset only the tournament-wide Fours and Sixes vMix counters."""
        answer = QMessageBox.question(
            self,
            "Confirm Tournament Fours / Sixes Counter Reset",
            "Are you sure you want to reset both tournament-wide counters?\\n\\n"
            "Fours Counter (vMix Input 33) will become 000.\\n"
            "Sixes Counter (vMix Input 34) will become 000.\\n\\n"
            "The player 4s/6s records and current match score will NOT be changed.",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )
        if answer != QMessageBox.Yes:
            return

        try:
            self.tournament_fours_count = 0
            self.tournament_sixes_count = 0

            # Persist zero values so the counters remain reset after restarting.
            self.save_tournament_fours_counter()
            self.save_tournament_sixes_counter()

            # Immediately send 000 to the corresponding vMix title inputs.
            self.update_tournament_fours_vmix(trigger_overlay=False)
            self.update_tournament_sixes_vmix(trigger_overlay=False)

            QMessageBox.information(
                self,
                "Tournament Counters Reset",
                "Tournament Fours Counter (Input 33) = 000\\n"
                "Tournament Sixes Counter (Input 34) = 000\\n\\n"
                "Both counters have been saved as zero."
            )
        except Exception as e:
            QMessageBox.critical(
                self,
                "Counter Reset Error",
                f"Could not reset tournament Fours/Sixes counters:\\n{e}"
            )

    def check_batsman_milestone(self, name, runs, balls, fours, sixes, sr):
        current_bat_stats = self.batting_stats_t1 if self.current_innings == 1 else self.batting_stats_t2
        if name not in current_bat_stats:
            current_bat_stats[name] = {"runs": runs, "balls": balls, "4s": fours, "6s": sixes, "out_by": "", "dismissal": "NOT OUT", "fifty_celebrated": False, "hundy_celebrated": False}
        
        stat = current_bat_stats[name]
        if "fifty_celebrated" not in stat: stat["fifty_celebrated"] = False
        if "hundy_celebrated" not in stat: stat["hundy_celebrated"] = False

        milestone_label = None
        if runs >= 100 and not stat["hundy_celebrated"]:
            stat["hundy_celebrated"] = True
            stat["fifty_celebrated"] = True
            milestone_label = "100 Runs"
        elif runs >= 50 and not stat["fifty_celebrated"]:
            stat["fifty_celebrated"] = True
            milestone_label = "50 Runs"

        if milestone_label:
            try:
                batting_team, bowling_team, _, _, bat_logo, _ = self.get_batting_bowling_teams()
                
                self.save_milestone_to_excel(name, batting_team, milestone_label, runs, balls, sr, bowling_team)

                self.send_to_vmix(27, "PLAYERNAMETXT.Text", name)
                self.send_to_vmix(27, "RUNTXT.Text", str(runs))
                self.send_to_vmix(27, "BALTXT.Text", str(balls))
                self.send_to_vmix(27, "FOURTXT.Text", str(fours))
                self.send_to_vmix(27, "SIXTXT.Text", str(sixes))
                self.send_to_vmix(27, "STRIKERATETXT.Text", str(sr))

                if bat_logo:
                    self.send_image_to_vmix(27, "TEAMLOGO16.Source", bat_logo.replace("\\", "/"))

                url = self.get_base_url()
                requests.get(f"{url}?Function=OverlayInput1In&Input=27", timeout=0.3)
                QTimer.singleShot(10000, lambda: requests.get(f"{url}?Function=OverlayInput1Out&Input=27", timeout=0.3))
            except Exception as e:
                print(f"Error triggering 50/100 celebration: {e}")

    def check_bowler_milestone(self, bowler_name, b_balls, b_runs, b_wickets, b_maidens):
        current_bowl_stats = self.bowling_stats_t1 if self.current_innings == 1 else self.bowling_stats_t2
        if bowler_name not in current_bowl_stats:
            return
            
        stat = current_bowl_stats[bowler_name]
        if "five_wkt_celebrated" not in stat:
            stat["five_wkt_celebrated"] = False

        if b_wickets >= 5 and not stat["five_wkt_celebrated"]:
            stat["five_wkt_celebrated"] = True
            try:
                _, bowling_team, batting_team, _, _, bowl_logo = self.get_batting_bowling_teams()
                
                b_ov = b_balls // 6
                b_rem = b_balls % 6
                b_ov_str = f"{b_ov}.{b_rem}"
                
                tot_ov_f = b_ov + (b_rem / 6.0)
                b_eco = f"{b_runs / tot_ov_f:.2f}" if tot_ov_f > 0 else "0.00"

                self.save_bowler_milestone_to_excel(bowler_name, bowling_team, "5 Wickets", b_ov_str, b_wickets, b_runs, batting_team)

                self.send_to_vmix(28, "BOWLERNAMETXT.Text", bowler_name)
                self.send_to_vmix(28, "OVERTXT.Text", b_ov_str)
                self.send_to_vmix(28, "WICKETTXT.Text", str(b_wickets))
                self.send_to_vmix(28, "RUNSTXT.Text", str(b_runs))
                self.send_to_vmix(28, "MAIDENTXT.Text", str(b_maidens))
                self.send_to_vmix(28, "ECOTXT.Text", b_eco)

                if bowl_logo:
                    self.send_image_to_vmix(28, "TEAMLOGO17.Source", bowl_logo.replace("\\", "/"))

                url = self.get_base_url()
                requests.get(f"{url}?Function=OverlayInput1In&Input=28", timeout=0.3)
                QTimer.singleShot(10000, lambda: requests.get(f"{url}?Function=OverlayInput1Out&Input=28", timeout=0.3))
            except Exception as e:
                print(f"Error triggering Bowler 5-Wicket celebration: {e}")

    def _reset_excel_record_sheet(self, sheet_name, headers):
        """Clear only the requested tournament-record sheet; preserve all other workbook sheets."""
        docs_path = os.path.expanduser("~/Documents")
        excel_file_path = os.path.join(docs_path, "live_match_autosave.xlsx")
        from openpyxl import Workbook, load_workbook

        if os.path.exists(excel_file_path):
            wb = load_workbook(excel_file_path)
        else:
            wb = Workbook()

        if sheet_name in wb.sheetnames:
            ws = wb[sheet_name]
            wb.remove(ws)

        # Recreate an empty sheet with its column headings.
        ws = wb.create_sheet(sheet_name)
        ws.append(headers)

        # Remove the default blank sheet only when another sheet is present.
        if "Sheet" in wb.sheetnames and len(wb.sheetnames) > 1:
            default_ws = wb["Sheet"]
            if default_ws.max_row == 1 and default_ws.max_column == 1 and default_ws["A1"].value is None:
                wb.remove(default_ws)

        wb.save(excel_file_path)

    def reset_batsman_milestones(self):
        answer = QMessageBox.question(
            self, "Confirm Reset",
            "Batsman Milestones madhil sarva records कायमचे delete करायचे आहेत का?\nहा reset फक्त Batsman Milestones साठी असेल.",
            QMessageBox.Yes | QMessageBox.No, QMessageBox.No
        )
        if answer != QMessageBox.Yes:
            return
        try:
            self._reset_excel_record_sheet(
                "Milestones",
                ["Date and Time", "Player Name", "Team Name", "50 ya 100", "Run", "Ball", "Strike Rate", "VS Team Name"]
            )
            self.tbl_milestones.setRowCount(0)
            QMessageBox.information(self, "Reset Complete", "Batsman Milestones records reset झाले.")
        except Exception as e:
            QMessageBox.critical(self, "Reset Error", f"Batsman Milestones reset करता आले नाही:\\n{e}")

    def reset_bowler_milestones(self):
        answer = QMessageBox.question(
            self, "Confirm Reset",
            "Bowler Milestones madhil sarva records कायमचे delete करायचे आहेत का?\nहा reset फक्त Bowler Milestones साठी असेल.",
            QMessageBox.Yes | QMessageBox.No, QMessageBox.No
        )
        if answer != QMessageBox.Yes:
            return
        try:
            self._reset_excel_record_sheet(
                "Bowler_Milestones",
                ["Date and Time", "Bowler Name", "Team Name", "Milestone", "Overs", "Wickets", "Runs", "VS Team Name"]
            )
            self.tbl_bowler_milestones.setRowCount(0)
            QMessageBox.information(self, "Reset Complete", "Bowler Milestones records reset झाले.")
        except Exception as e:
            QMessageBox.critical(self, "Reset Error", f"Bowler Milestones reset करता आले नाही:\\n{e}")

    def save_milestone_to_excel(self, player_name, team_name, milestone, runs, balls, sr, vs_team):
        try:
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            row_data = {
                "Date and Time": [timestamp],
                "Player Name": [player_name],
                "Team Name": [team_name],
                "50 ya 100": [milestone],
                "Run": [runs],
                "Ball": [balls],
                "Strike Rate": [sr],
                "VS Team Name": [vs_team]
            }
            df_new = pd.DataFrame(row_data)
            docs_path = os.path.expanduser("~/Documents")
            excel_file_path = os.path.join(docs_path, "live_match_autosave.xlsx")

            if os.path.exists(excel_file_path):
                try:
                    df_existing = pd.read_excel(excel_file_path, sheet_name="Milestones")
                    already_saved = ((df_existing["Player Name"] == player_name) & 
                                     (df_existing["50 ya 100"] == milestone)).any()
                    if already_saved:
                        return
                    df_combined = pd.concat([df_existing, df_new], ignore_index=True)
                except Exception:
                    df_combined = df_new

                with pd.ExcelWriter(excel_file_path, engine="openpyxl", mode="a", if_sheet_exists="replace") as writer:
                    df_combined.to_excel(writer, sheet_name="Milestones", index=False)
            else:
                with pd.ExcelWriter(excel_file_path, engine="openpyxl", mode="w") as writer:
                    df_new.to_excel(writer, sheet_name="Milestones", index=False)
            
            self.load_milestones_data_to_table()
        except Exception as e:
            print(f"Milestone Excel Auto-Save Error: {e}")

    def load_milestones_data_to_table(self):
        try:
            docs_path = os.path.expanduser("~/Documents")
            excel_file_path = os.path.join(docs_path, "live_match_autosave.xlsx")
            if os.path.exists(excel_file_path):
                try:
                    df = pd.read_excel(excel_file_path, sheet_name="Milestones")
                    self.tbl_milestones.setRowCount(len(df))
                    for row_idx, row in df.iterrows():
                        self.tbl_milestones.setItem(row_idx, 0, QTableWidgetItem(str(row.get("Date and Time", ""))))
                        self.tbl_milestones.setItem(row_idx, 1, QTableWidgetItem(str(row.get("Player Name", ""))))
                        self.tbl_milestones.setItem(row_idx, 2, QTableWidgetItem(str(row.get("Team Name", ""))))
                        self.tbl_milestones.setItem(row_idx, 3, QTableWidgetItem(str(row.get("50 ya 100", ""))))
                        self.tbl_milestones.setItem(row_idx, 4, QTableWidgetItem(str(row.get("Run", ""))))
                        self.tbl_milestones.setItem(row_idx, 5, QTableWidgetItem(str(row.get("Ball", ""))))
                        self.tbl_milestones.setItem(row_idx, 6, QTableWidgetItem(str(row.get("Strike Rate", ""))))
                        self.tbl_milestones.setItem(row_idx, 7, QTableWidgetItem(str(row.get("VS Team Name", ""))))
                except Exception:
                    self.tbl_milestones.setRowCount(0)
        except Exception as e:
            print(f"Error loading milestones to table: {e}")

    def save_bowler_milestone_to_excel(self, bowler_name, team_name, milestone, overs, wickets, runs, vs_team):
        try:
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            row_data = {
                "Date and Time": [timestamp],
                "Bowler Name": [bowler_name],
                "Team Name": [team_name],
                "Milestone": [milestone],
                "Overs": [overs],
                "Wickets": [wickets],
                "Runs": [runs],
                "VS Team Name": [vs_team]
            }
            df_new = pd.DataFrame(row_data)
            docs_path = os.path.expanduser("~/Documents")
            excel_file_path = os.path.join(docs_path, "live_match_autosave.xlsx")

            if os.path.exists(excel_file_path):
                try:
                    df_existing = pd.read_excel(excel_file_path, sheet_name="Bowler_Milestones")
                    already_saved = ((df_existing["Bowler Name"] == bowler_name) & 
                                     (df_existing["Milestone"] == milestone)).any()
                    if already_saved:
                        return
                    df_combined = pd.concat([df_existing, df_new], ignore_index=True)
                except Exception:
                    df_combined = df_new

                with pd.ExcelWriter(excel_file_path, engine="openpyxl", mode="a", if_sheet_exists="replace") as writer:
                    df_combined.to_excel(writer, sheet_name="Bowler_Milestones", index=False)
            else:
                with pd.ExcelWriter(excel_file_path, engine="openpyxl", mode="w") as writer:
                    df_new.to_excel(writer, sheet_name="Bowler_Milestones", index=False)
            
            self.load_bowler_milestones_data_to_table()
        except Exception as e:
            print(f"Bowler Milestone Excel Auto-Save Error: {e}")

    def load_bowler_milestones_data_to_table(self):
        try:
            docs_path = os.path.expanduser("~/Documents")
            excel_file_path = os.path.join(docs_path, "live_match_autosave.xlsx")
            if os.path.exists(excel_file_path):
                try:
                    df = pd.read_excel(excel_file_path, sheet_name="Bowler_Milestones")
                    self.tbl_bowler_milestones.setRowCount(len(df))
                    for row_idx, row in df.iterrows():
                        self.tbl_bowler_milestones.setItem(row_idx, 0, QTableWidgetItem(str(row.get("Date and Time", ""))))
                        self.tbl_bowler_milestones.setItem(row_idx, 1, QTableWidgetItem(str(row.get("Bowler Name", ""))))
                        self.tbl_bowler_milestones.setItem(row_idx, 2, QTableWidgetItem(str(row.get("Team Name", ""))))
                        self.tbl_bowler_milestones.setItem(row_idx, 3, QTableWidgetItem(str(row.get("Milestone", ""))))
                        self.tbl_bowler_milestones.setItem(row_idx, 4, QTableWidgetItem(str(row.get("Overs", ""))))
                        self.tbl_bowler_milestones.setItem(row_idx, 5, QTableWidgetItem(str(row.get("Wickets", ""))))
                        self.tbl_bowler_milestones.setItem(row_idx, 6, QTableWidgetItem(str(row.get("Runs", ""))))
                        self.tbl_bowler_milestones.setItem(row_idx, 7, QTableWidgetItem(str(row.get("VS Team Name", ""))))
                except Exception:
                    self.tbl_bowler_milestones.setRowCount(0)
        except Exception as e:
            print(f"Error loading bowler milestones to table: {e}")

    def toggle_super_over_overlay_input32(self):
        self.super_over_overlay_visible = not self.super_over_overlay_visible
        url = self.get_base_url()
        try:
            if self.super_over_overlay_visible:
                self.btn_toggle_so_overlay.setText("⚡ TOGGLE SUPER OVER OVERLAY (INPUT 32) [ON]")
                self.btn_toggle_so_overlay.setStyleSheet("background-color: #28a745; color: white; font-weight: bold; padding: 12px; font-size: 13px;")
                self.send_to_vmix(32, "SUPEROVERTXT.Text", "SUPER OVER")
                requests.get(f"{url}?Function=OverlayInput1In&Input=32", timeout=0.3)
            else:
                self.btn_toggle_so_overlay.setText("⚡ TOGGLE SUPER OVER OVERLAY (INPUT 32) [OFF]")
                self.btn_toggle_so_overlay.setStyleSheet("background-color: #e65100; color: white; font-weight: bold; padding: 12px; font-size: 13px;")
                requests.get(f"{url}?Function=OverlayInput1Out&Input=32", timeout=0.3)
        except Exception as e:
            print(f"Error toggling Input 32 Super Over: {e}")

    def auto_save_match_to_excel(self):
        try:
            batting_team, bowling_team, _, _, _, _ = self.get_batting_bowling_teams()
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

            b_ov_num = self.bowler_balls // 6
            b_rem_num = self.bowler_balls % 6
            bowler_overs_str = f"{b_ov_num}.{b_rem_num}"

            row_data = {
                "Timestamp": [timestamp],
                "Innings": [self.current_innings],
                "Batting Team": [batting_team],
                "Bowling Team": [bowling_team],
                "Total Score": [f"{self.runs}/{self.wickets}"],
                "Overs": [f"{self.overs}.{self.balls}"],
                "Extras": [self.extras],
                "Striker Name": [self.bat1_name if self.bat1_name else "-"],
                "Striker Runs": [self.bat1_runs],
                "Striker Balls": [self.bat1_balls],
                "Non-Striker Name": [self.bat2_name if self.bat2_name else "-"],
                "Non-Striker Runs": [self.bat2_runs],
                "Non-Striker Balls": [self.bat2_balls],
                "Current Bowler Name": [self.current_bowler_name if self.current_bowler_name else "-"],
                "Bowler Overs": [bowler_overs_str],
                "Bowler Runs": [self.bowler_runs],
                "Bowler Wickets": [self.bowler_wickets],
                "Target": [self.target_runs if self.current_innings == 2 else "-"],
                "Status": ["COMPLETED" if self.match_ended else "LIVE"]
            }

            df_new = pd.DataFrame(row_data)
            docs_path = os.path.expanduser("~/Documents")
            excel_file_path = os.path.join(docs_path, "live_match_autosave.xlsx")
            
            if os.path.exists(excel_file_path):
                try:
                    df_existing = pd.read_excel(excel_file_path, sheet_name="Live_Score")
                    df_combined = pd.concat([df_existing, df_new], ignore_index=True)
                except Exception:
                    df_combined = df_new

                with pd.ExcelWriter(excel_file_path, engine="openpyxl", mode="a", if_sheet_exists="replace") as writer:
                    df_combined.to_excel(writer, sheet_name="Live_Score", index=False)
            else:
                with pd.ExcelWriter(excel_file_path, engine="openpyxl", mode="w") as writer:
                    df_new.to_excel(writer, sheet_name="Live_Score", index=False)
        except Exception as e:
            print(f"Excel Detailed Auto-Save Error: {e}")

    def start_super_over(self):
        options = ["3 Balls", "6 Balls", "1 Over", "2 Overs"]
        item, ok = QInputDialog.getItem(self, "Super Over Setup", "Select Super Over Format:", options, 0, False)
        
        if not ok or not item:
            return

        if item == "3 Balls":
            over_val = "0.3"  
        elif item == "6 Balls" or item == "1 Over":
            over_val = "1"    
        elif item == "2 Overs":
            over_val = "2"    
        else:
            over_val = "1"

        self.is_super_over = True
        self.super_over_overlay_visible = True
        self.btn_toggle_so_overlay.setText("⚡ TOGGLE SUPER OVER OVERLAY (INPUT 32) [ON]")
        self.btn_toggle_so_overlay.setStyleSheet("background-color: #28a745; color: white; font-weight: bold; padding: 12px; font-size: 13px;")
        
        try: 
            self.send_to_vmix(32, "SUPEROVERTXT.Text", "SUPER OVER")
            requests.get(f"{self.get_base_url()}?Function=OverlayInput1In&Input=32", timeout=0.3)
        except: pass

        self.current_innings = 1
        self.first_innings_ended = False
        self.runs = 0
        self.wickets = 0
        self.overs = 0
        self.balls = 0
        self.extras = 0
        self.match_ended = False
        
        self.txt_match_overs.setText(over_val)
        
        self.batting_stats_t1.clear()
        self.batting_stats_t2.clear()
        self.bowling_stats_t1.clear()
        self.bowling_stats_t2.clear()
        
        self.bat1_name = ""
        self.bat2_name = ""
        self.current_bowler_name = ""
        self.bat1_runs = 0
        self.bat1_balls = 0
        self.bat1_4s = 0
        self.bat1_6s = 0
        self.bat2_runs = 0
        self.bat2_balls = 0
        self.bat2_4s = 0
        self.bat2_6s = 0
        
        self.partnership_runs = 0
        self.partnership_balls = 0
        self.partnership_4s = 0
        self.partnership_6s = 0
        self.this_over_balls.clear()
        self.fall_of_wickets_list.clear()

        self.lbl_1st_score.setText("0/0")
        self.lbl_1st_over.setText("0.0")
        self.lbl_1st_extra.setText("0")
        self.txt_lw_player.clear()
        self.txt_lw_fielder.clear()
        self.txt_lw_bowler.clear()
        self.txt_lw_run.setText("0")
        self.txt_lw_ball.setText("0")
        self.txt_lw_outtype.clear()

        for table in [self.tbl_full_batting, self.tbl_full_bowling, self.tbl_full_batting2, self.tbl_full_bowling2, self.tbl_sum_t1_bat, self.tbl_sum_t2_bowl, self.tbl_sum_t2_bat, self.tbl_sum_t1_bowl]:
            table.clearContents()

        self.grp_active.setTitle("1st Innings Active Players & Live Scorecard Stats")
        self.btn_end_inning.setEnabled(True)

        self.refresh_active_players_dropdowns()
        self.update_score()
        QMessageBox.information(self, "Super Over Started", f"⚡ Super Over started with format: {item}!\nInput 32 activated automatically.")

    def save_points_data_to_file(self):
        try:
            docs_path = os.path.expanduser("~/Documents")
            file_path = os.path.join(docs_path, "tournament_data.json")
            
            with open(file_path, "w", encoding="utf-8") as f:
                json.dump(self.points_table_data, f, ensure_ascii=False, indent=4)
            QMessageBox.information(self, "Saved Successfully", f"Tournament Points Table successfully saved to:\n{file_path}")
        except Exception as e:
            QMessageBox.critical(self, "Save Error", f"Could not save points table:\n{str(e)}")

    def load_points_data_from_file(self):
        try:
            docs_path = os.path.expanduser("~/Documents")
            file_path = os.path.join(docs_path, "tournament_data.json")
            
            if os.path.exists(file_path):
                with open(file_path, "r", encoding="utf-8") as f:
                    self.points_table_data = json.load(f)
                self.update_points_table_display()
        except Exception as e:
            print(f"Error loading data: {e}")

    def reset_points_table(self):
        answer = QMessageBox.question(
            self, "Confirm Tournament Reset",
            "Tournament Points Table मधील सर्व teams, matches, points आणि NRR records delete करायचे आहेत का?\nहा reset फक्त Points Table साठी आहे.",
            QMessageBox.Yes | QMessageBox.No, QMessageBox.No
        )
        if answer != QMessageBox.Yes:
            return
        try:
            self.points_table_data = {}
            self._points_second_innings_saved = False
            self._points_match_result_recorded = False
            docs_path = os.path.expanduser("~/Documents")
            file_path = os.path.join(docs_path, "tournament_data.json")
            with open(file_path, "w", encoding="utf-8") as f:
                json.dump({}, f, ensure_ascii=False, indent=4)
            self.update_points_table_display()
            QMessageBox.information(self, "Reset Complete", "Tournament Points Table reset झाले.")
        except Exception as e:
            QMessageBox.critical(self, "Reset Error", f"Points Table reset करता आले नाही:\\n{e}")

    def get_base_url(self):
        ip = self.txt_vmix_ip.text().strip() or "127.0.0.1"
        port = self.txt_vmix_port.text().strip() or "8088"
        return f"http://{ip}:{port}/api/"

    def ping_vmix(self):
        url = self.get_base_url()
        try:
            resp = requests.get(url, timeout=1.5)
            if resp.status_code == 200:
                QMessageBox.information(self, "vMix Connected", "Successfully connected to vMix API!")
            else:
                QMessageBox.warning(self, "vMix Connection", f"Connected, but returned status code: {resp.status_code}")
        except Exception as e:
            QMessageBox.critical(self, "Connection Failed", f"Could not connect to vMix at {url}.\nError: {str(e)}")

    def toggle_vmix_input(self, input_num, label_name):
        url = f"{self.get_base_url()}?Function=OverlayInput1In&Input={input_num}"
        try:
            requests.get(url, timeout=0.5)
        except Exception as e:
            print(f"Error toggling {label_name}: {e}")

    def trigger_timed_overlay(self, input_num, label_name, duration_ms=8000, overlay_channel=1):
        """Show an input on the selected vMix Overlay Channel, then take it out."""
        overlay_channel = max(1, min(4, int(overlay_channel)))
        url = self.get_base_url()
        try:
            response = requests.get(
                f"{url}?Function=OverlayInput{overlay_channel}In&Input={input_num}",
                timeout=1.5
            )
            if response.status_code != 200:
                print(f"vMix overlay trigger failed for {label_name}: "
                      f"HTTP {response.status_code} - {response.text[:200]}")
            else:
                print(f"vMix overlay ON: {label_name} "
                      f"(Input {input_num}, Overlay {overlay_channel})")
            QTimer.singleShot(
                duration_ms,
                lambda: self.hide_vmix_input(input_num, overlay_channel)
            )
        except Exception as e:
            print(f"Error on timed overlay {label_name}: {e}")

    def hide_vmix_input(self, input_num, overlay_channel=1):
        overlay_channel = max(1, min(4, int(overlay_channel)))
        url = self.get_base_url()
        try:
            response = requests.get(
                f"{url}?Function=OverlayInput{overlay_channel}Out&Input={input_num}",
                timeout=1.5
            )
            if response.status_code != 200:
                print(f"vMix overlay OUT failed for Input {input_num}, "
                      f"Overlay {overlay_channel}: HTTP {response.status_code} - "
                      f"{response.text[:200]}")
        except Exception as e:
            print(f"Error hiding input {input_num} on Overlay {overlay_channel}: {e}")

    def trigger_vmix_gtzip(self, filename, label_name):
        url = f"{self.get_base_url()}?Function=Play&Input={filename}"
        try:
            requests.get(url, timeout=0.3)
        except Exception as e:
            print(f"Error playing {label_name}: {e}")

    def trigger_vmix_overlay_action(self, input_num, action_type):
        url = self.get_base_url()
        try:
            if action_type == "Hide Scoreboards":
                requests.get(f"{url}?Function=OverlayInput1Out&Input=17", timeout=0.3)
                requests.get(f"{url}?Function=OverlayInput2Out&Input=18", timeout=0.3)
            elif input_num == 17:
                requests.get(f"{url}?Function=OverlayInput1In&Input=17", timeout=0.3)
            elif input_num == 18:
                requests.get(f"{url}?Function=OverlayInput2In&Input=18", timeout=0.3)
        except Exception as e:
            print(f"Error on {action_type}: {e}")

    def take_all_overlays_out(self):
        url = self.get_base_url()
        try:
            for i in range(1, 5):
                requests.get(f"{url}?Function=OverlayInput{i}Out", timeout=0.2)
        except Exception as e:
            print(f"Error taking all overlays out: {e}")

    def browse_logo_a(self):
        file_path, _ = QFileDialog.getOpenFileName(self, "Select Team A Logo", "", "Image Files (*.png *.jpg *.jpeg)")
        if file_path:
            self.logo_a_path = file_path
            self.lbl_logo_a_name.setText(os.path.basename(file_path))
            self.update_score()

    def browse_logo_b(self):
        file_path, _ = QFileDialog.getOpenFileName(self, "Select Team B Logo", "", "Image Files (*.png *.jpg *.jpeg)")
        if file_path:
            self.logo_b_path = file_path
            self.lbl_logo_b_name.setText(os.path.basename(file_path))
            self.update_score()

    def get_1st_innings_teams(self):
        t1 = self.txt_team1.text().strip() or "TEAM A"
        t2 = self.txt_team2.text().strip() or "TEAM B"
        winner = self.cmb_toss_winner.currentText().strip()
        choice = self.cmb_toss_choice.currentText().strip()

        if (winner == t1 and choice == "BAT FIRST") or (winner == t2 and choice == "BOWL FIRST"):
            return t1, t2, self.team1_inputs, self.team2_inputs, self.logo_a_path, self.logo_b_path
        else:
            return t2, t1, self.team2_inputs, self.team1_inputs, self.logo_b_path, self.logo_a_path

    def get_batting_bowling_teams(self):
        t1_bat, t1_bowl, t1_bat_inps, t1_bowl_inps, t1_bat_logo, t1_bowl_logo = self.get_1st_innings_teams()
        if self.current_innings == 2:
            return t1_bowl, t1_bat, t1_bowl_inps, t1_bat_inps, t1_bowl_logo, t1_bat_logo
        return t1_bat, t1_bowl, t1_bat_inps, t1_bowl_inps, t1_bat_logo, t1_bowl_logo

    def on_team_change(self):
        t1 = self.txt_team1.text().strip() or "TEAM A"
        t2 = self.txt_team2.text().strip() or "TEAM B"
        self.grp_team1_squad.setTitle(f"{t1} (Squad Lineup)")
        self.grp_team2_squad.setTitle(f"{t2} (Squad Lineup)")
        self.update_team_combos()
        self.refresh_active_players_dropdowns()

    def update_team_combos(self):
        t1 = self.txt_team1.text().strip() or "TEAM A"
        t2 = self.txt_team2.text().strip() or "TEAM B"
        curr = self.cmb_toss_winner.currentText()
        self.cmb_toss_winner.blockSignals(True)
        self.cmb_toss_winner.clear()
        self.cmb_toss_winner.addItems([t1, t2])
        idx = self.cmb_toss_winner.findText(curr)
        if idx >= 0:
            self.cmb_toss_winner.setCurrentIndex(idx)
        self.cmb_toss_winner.blockSignals(False)
        self.update_toss_text()

    def refresh_active_players_dropdowns(self):
        bat_team, bowl_team, bat_inputs, bowl_inputs, _, _ = self.get_batting_bowling_teams()
        t_bat_players = [inp.text().strip() for inp in bat_inputs if inp.text().strip()]
        t_bowl_players = [inp.text().strip() for inp in bowl_inputs if inp.text().strip()]

        current_bat_stats = self.batting_stats_t1 if self.current_innings == 1 else self.batting_stats_t2
        current_bowl_stats = self.bowling_stats_t1 if self.current_innings == 1 else self.bowling_stats_t2

        for name in t_bat_players:
            if name not in current_bat_stats:
                current_bat_stats[name] = {"runs": 0, "balls": 0, "4s": 0, "6s": 0, "out_by": "", "dismissal": "DNB", "fifty_celebrated": False, "hundy_celebrated": False}

        for name in t_bowl_players:
            if name not in current_bowl_stats:
                current_bowl_stats[name] = {"balls": 0, "maidens": 0, "runs": 0, "wickets": 0, "five_wkt_celebrated": False}

        self.on_batsman_change()

    def on_player_select(self, team_num, player_idx):
        bat_team, bowl_team, bat_inputs, bowl_inputs, _, _ = self.get_batting_bowling_teams()
        
        t1_name = self.txt_team1.text().strip() or "TEAM A"
        selected_team_name = t1_name if team_num == 1 else (self.txt_team2.text().strip() or "TEAM B")
        
        clicked_player_name = (self.team1_inputs if team_num == 1 else self.team2_inputs)[player_idx].text().strip()
        if not clicked_player_name:
            return

        current_bat_stats = self.batting_stats_t1 if self.current_innings == 1 else self.batting_stats_t2
        current_bowl_stats = self.bowling_stats_t1 if self.current_innings == 1 else self.bowling_stats_t2

        if selected_team_name == bat_team:
            if current_bat_stats[clicked_player_name]["dismissal"] not in ["NOT OUT", "DNB", "RETIRED HURT"]:
                QMessageBox.warning(self, "Already Out", f"{clicked_player_name} is already OUT or batted.")
                return

            if not self.bat1_name:
                self.bat1_name = clicked_player_name
                if current_bat_stats[clicked_player_name]["dismissal"] in ["DNB", "RETIRED HURT"]:
                    current_bat_stats[clicked_player_name]["dismissal"] = "NOT OUT"
            elif not self.bat2_name and clicked_player_name != self.bat1_name:
                self.bat2_name = clicked_player_name
                if current_bat_stats[clicked_player_name]["dismissal"] in ["DNB", "RETIRED HURT"]:
                    current_bat_stats[clicked_player_name]["dismissal"] = "NOT OUT"
            else:
                msg = QMessageBox()
                msg.setIcon(QMessageBox.Question if hasattr(QMessageBox, 'Question') else QMessageBox.Information)
                msg.setText(f"Where to send {clicked_player_name}?")
                btn_b1 = msg.addButton("Set as Batsman 1 (Striker)", QMessageBox.ActionRole)
                btn_b2 = msg.addButton("Set as Batsman 2 (Non-Striker)", QMessageBox.ActionRole)
                msg.exec_()

                if msg.clickedButton() == btn_b1:
                    self.bat1_name = clicked_player_name
                elif msg.clickedButton() == btn_b2:
                    self.bat2_name = clicked_player_name

                if current_bat_stats[clicked_player_name]["dismissal"] in ["DNB", "RETIRED HURT"]:
                    current_bat_stats[clicked_player_name]["dismissal"] = "NOT OUT"

        else:
            if self.current_bowler_name and self.balls > 0 and clicked_player_name != self.current_bowler_name:
                QMessageBox.warning(self, "Over in Progress!", f"Over is currently running ({self.overs}.{self.balls} balls)!\nYou cannot change the bowler ({self.current_bowler_name}) until this over is completed.")
                return

            if self.over_completed_need_new_bowler and clicked_player_name == self.last_bowler_name:
                QMessageBox.warning(self, "Invalid Bowler Selection", f"{clicked_player_name} just completed an over!\nConsecutive overs not allowed.")
                return

            self.over_completed_need_new_bowler = False
            self.current_bowler_name = clicked_player_name
            self.txt_wkt_bowler.setText(clicked_player_name)
            
            if clicked_player_name in current_bowl_stats:
                self.bowler_balls = current_bowl_stats[clicked_player_name]["balls"]
                self.bowler_runs = current_bowl_stats[clicked_player_name]["runs"]
                self.bowler_wickets = current_bowl_stats[clicked_player_name]["wickets"]
                self.bowler_maidens = current_bowl_stats[clicked_player_name]["maidens"]
            else:
                self.bowler_balls = 0
                self.bowler_runs = 0
                self.bowler_wickets = 0
                self.bowler_maidens = 0

        self.on_batsman_change()

    def on_batsman_change(self):
        current_bat_stats = self.batting_stats_t1 if self.current_innings == 1 else self.batting_stats_t2

        if self.bat1_name and self.bat1_name in current_bat_stats and current_bat_stats[self.bat1_name]["dismissal"] == "DNB":
            current_bat_stats[self.bat1_name]["dismissal"] = "NOT OUT"
        if self.bat2_name and self.bat2_name in current_bat_stats and current_bat_stats[self.bat2_name]["dismissal"] == "DNB":
            current_bat_stats[self.bat2_name]["dismissal"] = "NOT OUT"

        self.lbl_bat1_disp.setText(self.bat1_name if self.bat1_name else "None")
        self.lbl_bat2_disp.setText(self.bat2_name if self.bat2_name else "None")
        self.lbl_bowler_disp.setText(self.current_bowler_name if self.current_bowler_name else "None")

        self.cmb_out_batsman.blockSignals(True)
        self.cmb_out_batsman.clear()
        if self.bat1_name: self.cmb_out_batsman.addItem(self.bat1_name)
        if self.bat2_name and self.bat2_name != self.bat1_name: self.cmb_out_batsman.addItem(self.bat2_name)
        self.cmb_out_batsman.blockSignals(False)

        bat_team, bowl_team, bat_inputs, bowl_inputs, _, _ = self.get_batting_bowling_teams()
        t_bowl_players = [inp.text().strip() for inp in bowl_inputs if inp.text().strip()]
        
        self.cmb_fielder.blockSignals(True)
        self.cmb_fielder.clear()
        self.cmb_fielder.addItems(t_bowl_players)
        self.cmb_fielder.blockSignals(False)

        self.txt_wkt_bowler.setText(self.current_bowler_name)
        self.update_wkt_preview_stats()
        self.update_score()

    def update_wkt_preview_stats(self):
        selected_out = self.cmb_out_batsman.currentText().strip()
        current_bat_stats = self.batting_stats_t1 if self.current_innings == 1 else self.batting_stats_t2

        r_val, b_val = 0, 0
        if selected_out == self.bat1_name:
            r_val = self.bat1_runs
            b_val = self.bat1_balls
        elif selected_out == self.bat2_name:
            r_val = self.bat2_runs
            b_val = self.bat2_balls
        elif selected_out in current_bat_stats:
            r_val = current_bat_stats[selected_out].get("runs", 0)
            b_val = current_bat_stats[selected_out].get("balls", 0)

        self.txt_wkt_runs.setText(str(r_val))
        self.txt_wkt_balls.setText(str(b_val))

    def update_toss_text(self):
        winner = self.cmb_toss_winner.currentText()
        choice = self.cmb_toss_choice.currentText()
        if winner:
            toss_str = f"{winner.upper()} WON THE TOSS & ELECTED TO {choice}"
            self.txt_toss_details.setText(toss_str)
        self.refresh_active_players_dropdowns()

    def sync_toss_to_vmix(self):
        toss_str = self.txt_toss_details.text().strip()
        t1 = self.txt_team1.text().strip() or "TEAM A"
        t2 = self.txt_team2.text().strip() or "TEAM B"
        
        self.send_to_vmix(2, "TOSSTEXT.Text", toss_str)
        self.send_to_vmix(2, "TEAMANAMETXT.Text", t1)
        self.send_to_vmix(2, "TEAMBNAMETXT.Text", t2)
        
        if self.logo_a_path: 
            img_a = self.logo_a_path.replace("\\", "/")
            self.send_image_to_vmix(2, "TEAMALOGO.Source", img_a)
            self.send_image_to_vmix(2, "TEAMALOGO3.Source", img_a)

        if self.logo_b_path: 
            img_b = self.logo_b_path.replace("\\", "/")
            self.send_image_to_vmix(2, "TEAMBLOGO.Source", img_b)
            self.send_image_to_vmix(2, "TEAMBLOGO3.Source", img_b)

        self.send_to_vmix(3, "TOSSINFO.Text", toss_str)

    def toggle_squad_overlay(self):
        vMixIP = f"{self.txt_vmix_ip.text().strip() or '127.0.0.1'}:{self.txt_vmix_port.text().strip() or '8088'}"
        t1 = self.txt_team1.text().strip() or "TEAM A"
        t2 = self.txt_team2.text().strip() or "TEAM B"
        toss_str = self.txt_toss_details.text().strip()

        if self.squad_overlay_visible:
            try: requests.get(f"http://{vMixIP}/api/?Function=OverlayInput1Out&Input=3", timeout=0.3)
            except: pass
            self.squad_overlay_visible = False
            self.btn_toggle_squad.setText("TOGGLE SQUAD OVERLAY ON LIVE CAMERA (Input 3)")
            self.btn_toggle_squad.setStyleSheet("background-color: #0275d8; color: white; font-size: 12px; font-weight: bold; padding: 5px;")
        else:
            self.send_to_vmix(3, "TEAMATXT.Text", t1)
            self.send_to_vmix(3, "TEAMBTXT.Text", t2)
            self.send_to_vmix(3, "TEAMANAME.Text", t1)
            self.send_to_vmix(3, "TEAMBNAME.Text", t2)
            self.send_to_vmix(3, "TOSSINFO.Text", toss_str)

            if self.logo_a_path:
                img_a = self.logo_a_path.replace("\\", "/")
                self.send_image_to_vmix(3, "TEAMALOGO3.Source", img_a)
                self.send_image_to_vmix(3, "TEAMALOGO.Source", img_a)
                self.send_image_to_vmix(3, "Team1logo.Source", img_a)

            if self.logo_b_path:
                img_b = self.logo_b_path.replace("\\", "/")
                self.send_image_to_vmix(3, "TEAMBLOGO3.Source", img_b)
                self.send_image_to_vmix(3, "TEAMBLOGO.Source", img_b)
                self.send_image_to_vmix(3, "Team2logo.Source", img_b)

            for i in range(11):
                self.send_to_vmix(3, f"A{i+1}.Text", self.team1_inputs[i].text().strip())
                self.send_to_vmix(3, f"B{i+1}.Text", self.team2_inputs[i].text().strip())

            try: requests.get(f"http://{vMixIP}/api/?Function=OverlayInput1In&Input=3", timeout=0.3)
            except: pass
            self.squad_overlay_visible = True
            self.btn_toggle_squad.setText("HIDE SQUAD OVERLAY (Input 3)")
            self.btn_toggle_squad.setStyleSheet("background-color: #d9534f; color: white; font-size: 12px; font-weight: bold; padding: 5px;")

    def swap_strike(self):
        self.striker_slot = 2 if self.striker_slot == 1 else 1
        self.update_score()

    def check_match_limits(self):
        if self.match_ended:
            return False

        if self.current_innings == 2 and self.runs >= self.target_runs:
            return False

        if self.over_completed_need_new_bowler:
            QMessageBox.critical(self, "Over Completed!", f"Over finished! Please select a NEW BOWLER using SELECT button.")
            return False
        return True

    def end_first_innings(self):
        if self.current_innings == 1:
            try:
                t1_bat_name, t1_bowl_name, t1_bat_inps, t1_bowl_inps, _, _ = self.get_1st_innings_teams()
                
                self.t1_bat_player_inputs = t1_bat_inps
                self.t1_bowl_player_inputs = t1_bowl_inps

                self.t1_bat_team_name = t1_bat_name
                self.t1_bowl_team_name = t1_bowl_name
                
                self.t1_total_score = f"{self.runs}/{self.wickets}"
                self.t1_overs = f"{self.overs}.{self.balls}"
                self.t1_extras = str(self.extras)

                if not self.is_super_over:
                    self.save_innings_stats_to_points_table(t1_bat_name, self.runs, self.overs, self.balls, is_batting=True)
                    self.save_innings_stats_to_points_table(t1_bowl_name, self.runs, self.overs, self.balls, is_batting=False)

                self.update_input_14_data(t1_bat_name, t1_bat_inps, self.t1_total_score, self.t1_overs, self.t1_extras, final_freeze=True)
                self.update_input_15_data(t1_bowl_name, t1_bowl_inps, self.t1_total_score, self.t1_overs, self.t1_extras, final_freeze=True)

                self.lbl_1st_score.setText(self.t1_total_score)
                self.lbl_1st_over.setText(self.t1_overs)
                self.lbl_1st_extra.setText(self.t1_extras)

                self.first_innings_ended = True
                self.target_runs = self.runs + 1
                
                tot_ov_f = self.overs + (self.balls / 6.0)
                first_inning_rr = f"{round(self.runs / tot_ov_f, 2):.2f}" if tot_ov_f > 0 else "0.00"

                self.current_innings = 2
                self.striker_slot = 1

                match_overs = self.txt_match_overs.text().strip() or "20"
                self.send_to_vmix(16, "TEAMNAMETXT.Text", t1_bowl_name)
                self.send_to_vmix(16, "TARGETTXT.Text", str(self.target_runs))
                self.send_to_vmix(16, "OVERTXT.Text", match_overs)
                self.send_to_vmix(16, "RUNRATETXT.Text", first_inning_rr)
                
                chasing_logo = self.logo_a_path if t1_bowl_name == self.txt_team1.text().strip() else self.logo_b_path
                if chasing_logo:
                    self.send_image_to_vmix(16, "TEAMLOGO.Source", chasing_logo.replace("\\", "/"))

                self.runs = 0
                self.wickets = 0
                self.overs = 0
                self.balls = 0
                self.extras = 0
                self.fours = 0
                self.sixes = 0
                self.bat1_name = ""
                self.bat2_name = ""
                self.current_bowler_name = ""
                self.bat1_runs = 0
                self.bat1_balls = 0
                self.bat1_4s = 0
                self.bat1_6s = 0
                self.bat2_runs = 0
                self.bat2_balls = 0
                self.bat2_4s = 0
                self.bat2_6s = 0
                self.partnership_runs = 0
                self.partnership_balls = 0
                self.partnership_4s = 0
                self.partnership_6s = 0
                self.bowler_balls = 0
                self.bowler_runs = 0
                self.bowler_wickets = 0
                self.bowler_maidens = 0
                self.over_runs_count = 0
                self.last_bowler_name = ""
                self.over_completed_need_new_bowler = False
                self.this_over_balls.clear()
                self.fall_of_wickets_list.clear()

                self.grp_active.setTitle("2nd Innings Active Players & Live Scorecard Stats")
                self.btn_end_inning.setEnabled(False)

                QMessageBox.information(self, "1st Innings Completed!", f"Target Set: {self.target_runs} Runs.")
                self.refresh_active_players_dropdowns()
                self.tab_side.setCurrentIndex(4)
                self.update_score()
            except Exception as e:
                print(f"Error in end_first_innings: {e}")

    def save_innings_stats_to_points_table(self, team_name, runs, overs, balls, is_batting):
        """Add one completed innings to tournament NRR totals."""
        if not team_name:
            return

        if team_name not in self.points_table_data:
            self.points_table_data[team_name] = {
                "played": 0, "won": 0, "lost": 0, "points": 0,
                "runs_scored": 0, "overs_faced": 0.0,
                "runs_conceded": 0.0, "overs_bowled": 0.0
            }

        # Cricket overs are stored internally as a true decimal fraction:
        # 2 overs + 4 balls = 2 + (4/6), NOT 2.4 as a decimal number.
        total_overs_val = float(overs) + (float(balls) / 6.0)

        # Under standard cricket NRR rules, an all-out innings is charged
        # with the full allotted overs, even if the team was dismissed early.
        max_wickets = 2 if self.is_super_over else 10
        if not self.is_super_over and self.wickets >= max_wickets:
            max_overs_str = self.txt_match_overs.text().strip() or "20"
            try:
                if "." in max_overs_str:
                    quota_overs, quota_balls = map(int, max_overs_str.split(".", 1))
                else:
                    quota_overs, quota_balls = int(max_overs_str), 0

                if 0 <= quota_balls < 6 and quota_overs >= 0:
                    total_overs_val = quota_overs + (quota_balls / 6.0)
            except (TypeError, ValueError):
                pass

        if is_batting:
            self.points_table_data[team_name]["runs_scored"] = (
                float(self.points_table_data[team_name].get("runs_scored", 0)) + float(runs)
            )
            self.points_table_data[team_name]["overs_faced"] = (
                float(self.points_table_data[team_name].get("overs_faced", 0)) + total_overs_val
            )
        else:
            self.points_table_data[team_name]["runs_conceded"] = (
                float(self.points_table_data[team_name].get("runs_conceded", 0)) + float(runs)
            )
            self.points_table_data[team_name]["overs_bowled"] = (
                float(self.points_table_data[team_name].get("overs_bowled", 0)) + total_overs_val
            )

    def _format_points_table_overs(self, overs_value):
        """Display accumulated NRR overs in cricket notation (e.g. 2.4)."""
        try:
            total_balls = int(round(float(overs_value) * 6))
            completed_overs, remaining_balls = divmod(total_balls, 6)
            return f"{completed_overs}.{remaining_balls}"
        except (TypeError, ValueError):
            return "0.0"

    def handle_end_match_action(self):
        try:
            # Prevent a second click / automatic callback from recording the
            # same match result and points twice.
            if self._points_match_result_recorded:
                self.update_points_table_display()
                return

            t1_name = self.txt_team1.text().strip() or "TEAM A"
            t2_name = self.txt_team2.text().strip() or "TEAM B"
            t1_bat_name, t1_bowl_name, _, _, _, _ = self.get_1st_innings_teams()

            winner_team = "MATCH TIED"
            loser_team = "MATCH TIED"
            margin = "Match Tied"

            if self.current_innings == 2 and self.runs >= self.target_runs:
                winner_team = t1_bowl_name
                loser_team = t1_bat_name
                margin = f"Won by {2 - self.wickets if self.is_super_over else 10 - self.wickets} Wickets"
            elif self.runs < self.target_runs - 1:
                winner_team = t1_bat_name
                loser_team = t1_bowl_name
                diff = (self.target_runs - 1) - self.runs
                margin = f"Won by {diff} Runs"
            else:
                if self.is_super_over and self.runs == self.target_runs - 1:
                    winner_choice, ok = QInputDialog.getItem(
                        self, "Super Over Tied", 
                        "Super Over Tied! Select Winner:", 
                        [t1_name, t2_name], 0, False
                    )
                    if ok and winner_choice:
                        winner_team = winner_choice
                        loser_team = t2_name if winner_choice == t1_name else t1_name
                        margin = "Won Super Over"

            self.match_ended = True
            self.txt_sum_result.setText(f"{winner_team} {margin}")
            self.txt_sum_status.setText("MATCH COMPLETE")
            self.auto_save_match_to_excel()

            # First innings is saved in end_first_innings().
            # Save the chase innings here so BOTH teams receive their
            # runs-scored / runs-conceded and overs totals for NRR.
            if (
                self.current_innings == 2
                and not self.is_super_over
                and not self._points_second_innings_saved
            ):
                second_batting_team = t1_bowl_name
                second_bowling_team = t1_bat_name

                self.save_innings_stats_to_points_table(
                    second_batting_team, self.runs, self.overs, self.balls,
                    is_batting=True
                )
                self.save_innings_stats_to_points_table(
                    second_bowling_team, self.runs, self.overs, self.balls,
                    is_batting=False
                )
                self._points_second_innings_saved = True

            for team in [t1_name, t2_name]:
                if team not in self.points_table_data:
                    self.points_table_data[team] = {
                        "played": 0, "won": 0, "lost": 0, "points": 0,
                        "runs_scored": 0, "overs_faced": 0.0,
                        "runs_conceded": 0.0, "overs_bowled": 0.0
                    }
            
            if not self.is_super_over:
                self.points_table_data[t1_name]["played"] += 1
                self.points_table_data[t2_name]["played"] += 1

            if winner_team != "MATCH TIED":
                self.points_table_data[winner_team]["won"] += 1
                self.points_table_data[winner_team]["points"] += 2
                self.points_table_data[loser_team]["lost"] += 1
            else:
                self.points_table_data[t1_name]["points"] += 1
                self.points_table_data[t2_name]["points"] += 1

            self._points_match_result_recorded = True
            self.update_points_table_display()
            self.save_points_data_to_file()

            t1_pts = str(self.points_table_data.get(t1_name, {}).get("points", 0))
            t2_pts = str(self.points_table_data.get(t2_name, {}).get("points", 0))
            winning_message = f"{winner_team} {margin}"

            self.send_to_vmix(24, "WINNERTEAMTXT.Text", winner_team)
            self.send_to_vmix(24, "LOSERTEAMTXT.Text", loser_team)
            self.send_to_vmix(24, "MARGINTXT.Text", margin)
            self.send_to_vmix(24, "TEAM1NAMETXT.Text", t1_name)
            self.send_to_vmix(24, "TEAM1POINTSTXT.Text", t1_pts)
            self.send_to_vmix(24, "TEAM2NAMETXT.Text", t2_name)
            self.send_to_vmix(24, "TEAM2POINTSTXT.Text", t2_pts)

            if self.logo_a_path:
                self.send_image_to_vmix(24, "TEAM1LOGO.Source", self.logo_a_path.replace("\\", "/"))
            if self.logo_b_path:
                self.send_image_to_vmix(24, "TEAM2LOGO.Source", self.logo_b_path.replace("\\", "/"))

            self.send_to_vmix(29, "WONTEAMTXT.Text", winning_message)
            self.send_to_vmix(29, "ATEAMTXT.Text", t1_name)
            self.send_to_vmix(29, "BTEAMTXT.Text", t2_name)

            if self.logo_a_path:
                self.send_image_to_vmix(29, "TEAMALOGO28.Source", self.logo_a_path.replace("\\", "/"))
            if self.logo_b_path:
                self.send_image_to_vmix(29, "TEAMBLOGO28.Source", self.logo_b_path.replace("\\", "/"))

            self.toggle_vmix_input(29, "Match Win Screen (Input 29)")

            QMessageBox.information(self, "Match Ended!", f"Match Successfully Completed!\nWinner: {winner_team}\nPoints Table Updated & Auto-Saved.")
        except Exception as e:
            print(f"Error in handle_end_match_action: {e}")

    def update_points_table_display(self):
        sorted_teams = []

        for team, d in self.points_table_data.items():
            # Fill missing fields when loading an older tournament_data.json.
            for key, default in {
                "played": 0, "won": 0, "lost": 0, "points": 0,
                "runs_scored": 0, "overs_faced": 0.0,
                "runs_conceded": 0, "overs_bowled": 0.0
            }.items():
                d.setdefault(key, default)

            runs_scored = float(d.get("runs_scored", 0) or 0)
            overs_faced = float(d.get("overs_faced", 0) or 0)
            runs_conceded = float(d.get("runs_conceded", 0) or 0)
            overs_bowled = float(d.get("overs_bowled", 0) or 0)

            run_rate_for = runs_scored / overs_faced if overs_faced > 0 else 0.0
            run_rate_against = runs_conceded / overs_bowled if overs_bowled > 0 else 0.0
            nrr = run_rate_for - run_rate_against

            d["nrr"] = round(nrr, 3)
            sorted_teams.append((team, d))

        # Points first, then NRR as the tie-breaker.
        sorted_teams.sort(
            key=lambda item: (
                float(item[1].get("points", 0) or 0),
                float(item[1].get("nrr", 0) or 0)
            ),
            reverse=True
        )

        self.tbl_points_table.setRowCount(max(50, len(sorted_teams)))

        for row_idx, (team, d) in enumerate(sorted_teams):
            self.tbl_points_table.setItem(row_idx, 0, QTableWidgetItem(str(row_idx + 1)))
            self.tbl_points_table.setItem(row_idx, 1, QTableWidgetItem(str(team)))
            self.tbl_points_table.setItem(row_idx, 2, QTableWidgetItem(str(d["played"])))
            self.tbl_points_table.setItem(row_idx, 3, QTableWidgetItem(str(d["won"])))
            self.tbl_points_table.setItem(row_idx, 4, QTableWidgetItem(str(d["lost"])))
            self.tbl_points_table.setItem(row_idx, 5, QTableWidgetItem(str(d["points"])))
            self.tbl_points_table.setItem(row_idx, 6, QTableWidgetItem(str(d["runs_scored"])))
            self.tbl_points_table.setItem(
                row_idx, 7, QTableWidgetItem(self._format_points_table_overs(d["overs_faced"]))
            )
            self.tbl_points_table.setItem(row_idx, 8, QTableWidgetItem(str(d["runs_conceded"])))
            self.tbl_points_table.setItem(
                row_idx, 9, QTableWidgetItem(self._format_points_table_overs(d["overs_bowled"]))
            )
            self.tbl_points_table.setItem(row_idx, 10, QTableWidgetItem(f"{d['nrr']:+.3f}"))

        for row_idx in range(len(sorted_teams), 50):
            self.tbl_points_table.setItem(row_idx, 0, QTableWidgetItem(str(row_idx + 1)))
            for col_idx in range(1, 11):
                self.tbl_points_table.setItem(row_idx, col_idx, QTableWidgetItem("-"))

    def update_input_14_data(self, batting_team, bat_inputs, total_score, overs_str, extras_str, final_freeze=False):
        bat_logo = self.logo_a_path if batting_team == self.txt_team1.text().strip() else self.logo_b_path
        
        self.send_to_vmix(14, "1stBATTINGNAME.Text", batting_team)
        if bat_logo:
            img_a = bat_logo.replace("\\", "/")
            self.send_image_to_vmix(14, "TEAMALOGO5.Source", img_a)

        self.send_to_vmix(14, "OVER1STINNTXT.Text", overs_str)
        self.send_to_vmix(14, "RUNWKTTXT.Text", total_score)
        self.send_to_vmix(14, "EXTRARUNTXT.Text", extras_str)

        current_active_bat_stats = self.batting_stats_t1 if self.current_innings == 1 else self.batting_stats_t2
        
        for idx in range(11):
            i = idx + 1
            p_name = bat_inputs[idx].text().strip() if idx < len(bat_inputs) else ""

            if p_name and p_name in current_active_bat_stats:
                p_data = current_active_bat_stats[p_name]
                p_runs = str(p_data["runs"])
                p_balls = str(p_data["balls"])
                p_dismissal = p_data["dismissal"] 
            else:
                p_runs = ""
                p_balls = ""
                p_dismissal = "DNB"

            is_batted = p_name and p_dismissal != "DNB"
            display_name = p_name if is_batted else ""

            self.send_to_vmix(14, f"BATSMAN{i}TXT.Text", display_name)
            
            r_val = p_runs if is_batted else ""
            b_val = p_balls if is_batted else ""
            
            self.send_to_vmix(14, f"RUNB{i}TXT.Text", r_val)
            self.send_to_vmix(14, f"BALLB{i}TXT.Text", b_val)
            
            if p_dismissal in ["NOT OUT", "DNB", ""]:
                out_by_text = ""
            else:
                out_by_text = p_dismissal

            self.send_to_vmix(14, f"OUTWHICHBA{i}TXT.Text", out_by_text)
            
            if final_freeze:
                row_status = p_dismissal if p_dismissal not in ["DNB", "NOT OUT"] else ("NOT OUT" if p_dismissal == "NOT OUT" else "")
            else:
                if p_dismissal == "NOT OUT" and is_batted:
                    row_status = "NOT OUT"
                else:
                    row_status = ""

            self.send_to_vmix(14, f"NotOuttxt{i}.Text", row_status if display_name else "")
            self.send_to_vmix(14, f"NotOutRow{i}.Text", row_status if display_name else "")

    def update_input_19_data(self, batting_team, bat_inputs, total_score, overs_str, extras_str, final_freeze=False):
        bat_logo = self.logo_a_path if batting_team == self.txt_team1.text().strip() else self.logo_b_path
        
        self.send_to_vmix(19, "2NDBATTINGNAME.Text", batting_team)
        if bat_logo:
            img_a = bat_logo.replace("\\", "/")
            self.send_image_to_vmix(19, "TEAMBLOGO11.Source", img_a)

        self.send_to_vmix(19, "OVER1STINNTXT.Text", overs_str)
        self.send_to_vmix(19, "RUNWKTTXT.Text", total_score)
        self.send_to_vmix(19, "EXTRARUNTXT.Text", extras_str)

        current_active_bat_stats = self.batting_stats_t2
        
        for idx in range(11):
            i = idx + 1
            p_name = bat_inputs[idx].text().strip() if idx < len(bat_inputs) else ""

            if p_name and p_name in current_active_bat_stats:
                p_data = current_active_bat_stats[p_name]
                p_runs = str(p_data["runs"])
                p_balls = str(p_data["balls"])
                p_dismissal = p_data["dismissal"] 
            else:
                p_runs = "0"
                p_balls = "0"
                p_dismissal = "DNB"

            is_batted = p_name and p_dismissal != "DNB"
            display_name = p_name if is_batted else ""

            self.send_to_vmix(19, f"BATSMAN{i}TXT.Text", display_name)
            
            r_val = p_runs if is_batted else ""
            b_val = p_balls if is_batted else ""
            
            self.send_to_vmix(19, f"RUNB{i}TXT.Text", r_val)
            self.send_to_vmix(19, f"RUN{i}TXT.Text", r_val)
            self.send_to_vmix(19, f"BALLB{i}TXT.Text", b_val)
            self.send_to_vmix(19, f"BALL{i}TXT.Text", b_val)
            
            if p_dismissal in ["NOT OUT", "DNB", ""]:
                out_by_text = ""
            else:
                out_by_text = p_dismissal

            self.send_to_vmix(19, f"OUTWHICHBA{i}TXT.Text", out_by_text)
            
            if final_freeze:
                row_status = p_dismissal if p_dismissal not in ["DNB", "NOT OUT"] else ("NOT OUT" if p_dismissal == "NOT OUT" else "")
            else:
                if p_dismissal == "NOT OUT" and is_batted:
                    row_status = "NOT OUT"
                else:
                    row_status = ""

            self.send_to_vmix(19, f"NotOuttxt{i}.Text", row_status if display_name else "")
            self.send_to_vmix(19, f"NotOutRow{i}.Text", row_status if display_name else "")

    def update_input_15_data(self, bowling_team, bowl_inputs, total_score, overs_str, extras_str, final_freeze=False):
        bowl_logo = self.logo_a_path if bowling_team == self.txt_team1.text().strip() else self.logo_b_path
        
        self.send_to_vmix(15, "TEAMBNAME6.Text", bowling_team)
        if bowl_logo:
            img_b = bowl_logo.replace("\\", "/")
            self.send_image_to_vmix(15, "BOWLINGTEAMLOGO.Source", img_b)

        self.send_to_vmix(15, "OVERTOTALTXT.Text", overs_str)
        self.send_to_vmix(15, "TOTALWKTTXT.Text", total_score)
        self.send_to_vmix(15, "EXTRARUNTXT.Text", extras_str)

        current_active_bowl_stats = self.bowling_stats_t1 if self.current_innings == 1 else self.bowling_stats_t2

        active_bowlers = []
        for b_name, b_data in current_active_bowl_stats.items():
            if b_data["balls"] > 0 and b_name not in active_bowlers:
                active_bowlers.append(b_name)
        
        if self.current_bowler_name and self.current_bowler_name not in active_bowlers:
            active_bowlers.append(self.current_bowler_name)

        for idx in range(7):
            i = idx + 1
            if idx < len(active_bowlers):
                b_name = active_bowlers[idx]
                b_data = current_active_bowl_stats.get(b_name, {"balls": 0, "runs": 0, "wickets": 0})
                
                if b_name == self.current_bowler_name:
                    b_data["balls"] = self.bowler_balls
                    b_data["runs"] = self.bowler_runs
                    b_data["wickets"] = self.bowler_wickets

                b_balls_val = b_data["balls"]
                b_ov = b_balls_val // 6
                b_rem = b_balls_val % 6
                b_ov_str = f"{b_ov}.{b_rem}"
                b_dots = str(max(0, b_balls_val - b_data["runs"]))
                b_runs = str(b_data["runs"])
                b_wkts = str(b_data["wickets"])
                
                tot_ov_f = b_ov + (b_rem / 6.0)
                if tot_ov_f > 0:
                    eco_val = b_data["runs"] / tot_ov_f
                    b_eco = f"{eco_val:.2f}"
                else:
                    b_eco = "0.00"
            else:
                b_name = ""
                b_ov_str = ""
                b_dots = ""
                b_runs = ""
                b_wkts = ""
                b_eco = ""

            self.send_to_vmix(15, f"BOWLERNTXT{i}.Text", b_name)
            self.send_to_vmix(15, f"BOWLEROVERTXT{i}.Text", b_ov_str)
            self.send_to_vmix(15, f"BOWDOTSTXT{i}.Text", b_dots)
            self.send_to_vmix(15, f"BOWRUNTXT{i}.Text", b_runs)
            self.send_to_vmix(15, f"BOWWICKETSTXT{i}.Text", b_wkts)
            self.send_to_vmix(15, f"BOWECONOMYTXT{i}.Text", b_eco)

        for w_idx in range(10):
            w_tag_num = w_idx + 1
            w_val_str = self.fall_of_wickets_list[w_idx] if w_idx < len(self.fall_of_wickets_list) else ""
            self.send_to_vmix(15, f"WICKFALLTXT{w_tag_num}.Text", w_val_str)

    def update_input_20_data(self, bowling_team, bowl_inputs, total_score, overs_str, extras_str, final_freeze=False):
        bowl_logo = self.logo_a_path if bowling_team == self.txt_team1.text().strip() else self.logo_b_path
        
        self.send_to_vmix(20, "TEAMBNAME6.Text", bowling_team)
        self.send_to_vmix(20, "2NDBOWLINGTEAM.Text", bowling_team)
        if bowl_logo:
            img_b = bowl_logo.replace("\\", "/")
            self.send_image_to_vmix(20, "BOWLINGTEAMLOGO.Source", img_b)
            self.send_image_to_vmix(20, "2NDBOWTLOGO13.Source", img_b)

        self.send_to_vmix(20, "OVERTOTALTXT.Text", overs_str)
        self.send_to_vmix(20, "TOTALWKTTXT.Text", total_score)
        self.send_to_vmix(20, "EXTRARUNTXT.Text", extras_str)

        current_active_bowl_stats = self.bowling_stats_t2

        active_bowlers = []
        for b_name, b_data in current_active_bowl_stats.items():
            if b_data["balls"] > 0 and b_name not in active_bowlers:
                active_bowlers.append(b_name)
        
        if self.current_bowler_name and self.current_bowler_name not in active_bowlers:
            active_bowlers.append(self.current_bowler_name)

        for idx in range(7):
            i = idx + 1
            if idx < len(active_bowlers):
                b_name = active_bowlers[idx]
                b_data = current_active_bowl_stats.get(b_name, {"balls": 0, "runs": 0, "wickets": 0})
                
                if b_name == self.current_bowler_name:
                    b_data["balls"] = self.bowler_balls
                    b_data["runs"] = self.bowler_runs
                    b_data["wickets"] = self.bowler_wickets

                b_balls_val = b_data["balls"]
                b_ov = b_balls_val // 6
                b_rem = b_balls_val % 6
                b_ov_str = f"{b_ov}.{b_rem}"
                b_dots = str(max(0, b_balls_val - b_data["runs"]))
                b_runs = str(b_data["runs"])
                b_wkts = str(b_data["wickets"])
                
                tot_ov_f = b_ov + (b_rem / 6.0)
                if tot_ov_f > 0:
                    eco_val = b_data["runs"] / tot_ov_f
                    b_eco = f"{eco_val:.2f}"
                else:
                    b_eco = "0.00"
            else:
                b_name = ""
                b_ov_str = ""
                b_dots = ""
                b_runs = ""
                b_wkts = ""
                b_eco = ""

            self.send_to_vmix(20, f"BOWLERNTXT{i}.Text", b_name)
            self.send_to_vmix(20, f"BOWLEROVERTXT{i}.Text", b_ov_str)
            self.send_to_vmix(20, f"BOWDOTSTXT{i}.Text", b_dots)
            self.send_to_vmix(20, f"BOWRUNTXT{i}.Text", b_runs)
            self.send_to_vmix(20, f"BOWWICKETSTXT{i}.Text", b_wkts)
            self.send_to_vmix(20, f"BOWECONOMYTXT{i}.Text", b_eco)

        for w_idx in range(10):
            w_tag_num = w_idx + 1
            w_val_str = self.fall_of_wickets_list[w_idx] if w_idx < len(self.fall_of_wickets_list) else ""
            self.send_to_vmix(20, f"WICKFALLTXT{w_tag_num}.Text", w_val_str)

    def update_input_21_data(self):
        try:
            t1_bat_name, t1_bowl_name, t1_bat_inps, t1_bowl_inps, t1_bat_logo, t1_bowl_logo = self.get_1st_innings_teams()

            self.send_to_vmix(21, "TEAMANAMETEXT.Text", t1_bat_name)
            self.send_to_vmix(21, "TEAMBNMETEXT.Text", t1_bowl_name)
            self.send_to_vmix(21, "TEAMAMANE.Text", t1_bat_name)
            self.send_to_vmix(21, "TEAMBNAME.Text", t1_bowl_name)

            if t1_bat_logo:
                self.send_image_to_vmix(21, "TEAMALOGO15.Source", t1_bat_logo.replace("\\", "/"))
                self.send_image_to_vmix(21, "TEAMLOGOA.Source", t1_bat_logo.replace("\\", "/"))
            if t1_bowl_logo:
                self.send_image_to_vmix(21, "TEAMBLOGO15.Source", t1_bowl_logo.replace("\\", "/"))
                self.send_image_to_vmix(21, "TEAMLOGOB.Source", t1_bowl_logo.replace("\\", "/"))

            t1_score_str = self.t1_total_score if self.first_innings_ended or self.current_innings == 2 else f"{self.runs}/{self.wickets}"
            t2_score_str = f"{self.runs}/{self.wickets}" if self.current_innings == 2 else "0/0"

            self.send_to_vmix(21, "1STTBATTRUNWTK.Text", t1_score_str)
            self.send_to_vmix(21, "2NDBATTRUNWKT.Text", t2_score_str)

            t1_ov_str = self.t1_overs if self.first_innings_ended or self.current_innings == 2 else f"{self.overs}.{self.balls}"
            t2_ov_str = f"{self.overs}.{self.balls}" if self.current_innings == 2 else "0.0"

            self.send_to_vmix(21, "OVER1STBATTINGT.Text", t1_ov_str)
            self.send_to_vmix(21, "OVER2NDBATTINGT.Text", t2_ov_str)

            result_str = "MATCH IN PROGRESS"
            if self.match_ended or (self.current_innings == 2 and self.runs >= self.target_runs):
                if self.runs >= self.target_runs:
                    winner = t1_bowl_name
                    wickets_left = 2 if self.is_super_over else 10 - self.wickets
                    result_str = f"{winner} WON BY {wickets_left} WICKETS"
                elif self.runs < self.target_runs - 1:
                    winner = t1_bat_name
                    diff = (self.target_runs - 1) - self.runs
                    result_str = f"{winner} WON BY {diff} RUNS"
                else:
                    result_str = "MATCH TIED"
            
            self.send_to_vmix(21, "RESULTWINTEXT1.Text", result_str)

            t1_bats = []
            for inp in t1_bat_inps:
                p_n = inp.text().strip()
                if p_n:
                    st = self.batting_stats_t1.get(p_n, {"runs": 0, "balls": 0, "dismissal": "DNB"})
                    if p_n == self.bat1_name and self.current_innings == 1:
                        st["runs"], st["balls"] = self.bat1_runs, self.bat1_balls
                    elif p_n == self.bat2_name and self.current_innings == 1:
                        st["runs"], st["balls"] = self.bat2_runs, self.bat2_balls
                    
                    if st["dismissal"] != "DNB" or p_n in [self.bat1_name, self.bat2_name]:
                        t1_bats.append((p_n, st["runs"], st["balls"]))
            t1_bats.sort(key=lambda x: (x[1], -x[2]), reverse=True)

            t1_bowls = []
            for inp in t1_bowl_inps:
                b_n = inp.text().strip()
                if b_n:
                    bst = self.bowling_stats_t1.get(b_n, {"balls": 0, "runs": 0, "wickets": 0})
                    if b_n == self.current_bowler_name and self.current_innings == 1:
                        bst["balls"], bst["runs"], bst["wickets"] = self.bowler_balls, self.bowler_runs, self.bowler_wickets
                    
                    if bst["balls"] > 0 or b_n == self.current_bowler_name:
                        t1_bowls.append((b_n, bst["wickets"], bst["runs"], bst["balls"]))
            t1_bowls.sort(key=lambda x: (x[1], -x[2]), reverse=True)

            t2_bats = []
            if self.current_innings == 2 or self.first_innings_ended:
                for inp in t1_bowl_inps:
                    p_n = inp.text().strip()
                    if p_n:
                        st = self.batting_stats_t2.get(p_n, {"runs": 0, "balls": 0, "dismissal": "DNB"})
                        if p_n == self.bat1_name and self.current_innings == 2:
                            st["runs"], st["balls"] = self.bat1_runs, self.bat1_balls
                        elif p_n == self.bat2_name and self.current_innings == 2:
                            st["runs"], st["balls"] = self.bat2_runs, self.bat2_balls
                        
                        if st["dismissal"] != "DNB" or p_n in [self.bat1_name, self.bat2_name]:
                            t2_bats.append((p_n, st["runs"], st["balls"]))
                t2_bats.sort(key=lambda x: (x[1], -x[2]), reverse=True)

            t2_bowls = []
            if self.current_innings == 2 or self.first_innings_ended:
                for inp in t1_bat_inps:
                    b_n = inp.text().strip()
                    if b_n:
                        bst = self.bowling_stats_t2.get(b_n, {"balls": 0, "runs": 0, "wickets": 0})
                        if b_n == self.current_bowler_name and self.current_innings == 2:
                            bst["balls"], bst["runs"], bst["wickets"] = self.bowler_balls, self.bowler_runs, self.bowler_wickets
                        
                        if bst["balls"] > 0 or b_n == self.current_bowler_name:
                            t2_bowls.append((b_n, bst["wickets"], bst["runs"], bst["balls"]))
                t2_bowls.sort(key=lambda x: (x[1], -x[2]), reverse=True)

            for idx in range(4):
                i = idx + 1
                b_name = t1_bats[idx][0] if idx < len(t1_bats) else ""
                b_run = str(t1_bats[idx][1]) if idx < len(t1_bats) else ""
                b_ball = str(t1_bats[idx][2]) if idx < len(t1_bats) else ""
                
                self.send_to_vmix(21, f"1STBATTPTEXT{i}.Text", b_name)
                self.send_to_vmix(21, f"1STBARUNTEXT{i}.Text", b_run)
                self.send_to_vmix(21, f"1STBABALLTEXT{i}.Text", b_ball)

                bw_name = t1_bowls[idx][0] if idx < len(t1_bowls) else ""
                bw_wkt = str(t1_bowls[idx][1]) if idx < len(t1_bowls) else ""
                bw_run = str(t1_bowls[idx][2]) if idx < len(t1_bowls) else ""
                bw_bl = t1_bowls[idx][3] if idx < len(t1_bowls) else 0
                bw_ov = f"{bw_bl // 6}.{bw_bl % 6}" if idx < len(t1_bowls) else ""

                self.send_to_vmix(21, f"1STBOWBOWTEXT{i}.Text", bw_name)
                self.send_to_vmix(21, f"1STBOWLWICTEXT{i}.Text", bw_wkt)
                self.send_to_vmix(21, f"1STBOWLRUNTEXT{i}.Text", bw_run)
                self.send_to_vmix(21, f"1STBOWLOVETEXT{i}.Text", bw_ov)

            for idx in range(4):
                i = idx + 1
                b_name = t2_bats[idx][0] if idx < len(t2_bats) else ""
                b_run = str(t2_bats[idx][1]) if idx < len(t2_bats) else ""
                b_ball = str(t2_bats[idx][2]) if idx < len(t2_bats) else ""
                
                self.send_to_vmix(21, f"2NDBATTPTEXT{i}.Text", b_name)
                self.send_to_vmix(21, f"2NDRUNTEXT{i}.Text", b_run)
                self.send_to_vmix(21, f"2NDBABALLTEXT{i}.Text", b_ball)

                bw_name = t2_bowls[idx][0] if idx < len(t2_bowls) else ""
                bw_wkt = str(t2_bowls[idx][1]) if idx < len(t2_bowls) else ""
                bw_run = str(t2_bowls[idx][2]) if idx < len(t2_bowls) else ""
                bw_bl = t2_bowls[idx][3] if idx < len(t2_bowls) else 0
                bw_ov = f"{bw_bl // 6}.{bw_bl % 6}" if idx < len(t2_bowls) else ""

                self.send_to_vmix(21, f"2NDBOWLBOLTEXT{i}.Text", bw_name)
                self.send_to_vmix(21, f"2NDBOWLWICTEXT{i}.Text", bw_wkt)
                self.send_to_vmix(21, f"2NDBOWLRUNTEXT{i}.Text", bw_run)
                self.send_to_vmix(21, f"2NDBOWLOVETEXT{i}.Text", bw_ov)

        except Exception as e:
            print(f"Error updating Input 21 Match Summary: {e}")

    def process_over_and_innings_end(self):
        max_overs_str = self.txt_match_overs.text().strip() or "1"
        
        try:
            if "." in max_overs_str:
                target_overs, target_balls = map(int, max_overs_str.split("."))
            else:
                target_overs, target_balls = int(max_overs_str), 0
        except ValueError:
            target_overs, target_balls = 1, 0

        over_finished = False
        if target_balls > 0:
            if self.overs == target_overs and self.balls >= target_balls:
                over_finished = True
        else:
            if self.balls == 6:
                over_finished = True

        if over_finished:
            if target_balls == 0:
                self.overs += 1
                self.balls = 0
            
            self.striker_slot = 2 if self.striker_slot == 1 else 1

            if self.over_runs_count == 0:
                self.bowler_maidens += 1

            current_bowl_stats = self.bowling_stats_t1 if self.current_innings == 1 else self.bowling_stats_t2
            if self.current_bowler_name in current_bowl_stats:
                current_bowl_stats[self.current_bowler_name]["balls"] = self.bowler_balls
                current_bowl_stats[self.current_bowler_name]["runs"] = self.bowler_runs
                current_bowl_stats[self.current_bowler_name]["wickets"] = self.bowler_wickets
                current_bowl_stats[self.current_bowler_name]["maidens"] = self.bowler_maidens

            self.over_runs_count = 0
            self.last_bowler_name = self.current_bowler_name

            match_overs_completed = (self.overs >= target_overs if target_balls == 0 else (self.overs > target_overs or (self.overs == target_overs and self.balls >= target_balls)))

            if self.current_innings == 1 and match_overs_completed:
                self.end_first_innings()
            elif self.current_innings == 2 and match_overs_completed:
                self.match_ended = True
                self.txt_sum_status.setText("MATCH COMPLETE")
                QMessageBox.information(self, "Match Completed!", f"2nd Innings Overs Finished! Match Complete. Click 'END MATCH' to update Points Table.")
                self.handle_end_match_action()
            else:
                self.over_completed_need_new_bowler = True
                QMessageBox.information(self, "Over Finished!", f"Over completed! Please select a NEW BOWLER using SELECT button.")

    def _push_undo_state(self):
        """Save a complete scoring snapshot before applying one scoring action."""
        state_names = [
            "runs", "wickets", "overs", "balls", "extras", "fours", "sixes",
            "current_innings", "first_innings_ended", "target_runs", "match_ended",
            "is_super_over", "super_over_target", "super_over_overlay_visible",
            "striker_slot", "batting_stats_t1", "batting_stats_t2",
            "bowling_stats_t1", "bowling_stats_t2",
            "bat1_name", "bat2_name", "current_bowler_name",
            "bat1_runs", "bat1_balls", "bat1_4s", "bat1_6s",
            "bat2_runs", "bat2_balls", "bat2_4s", "bat2_6s",
            "partnership_runs", "partnership_balls", "partnership_4s", "partnership_6s",
            "lw_player", "lw_fielder", "lw_bowler", "lw_run", "lw_ball", "lw_outtype",
            "bowler_balls", "bowler_runs", "bowler_wickets", "bowler_maidens",
            "over_runs_count", "last_bowler_name", "over_completed_need_new_bowler",
            "this_over_balls", "fall_of_wickets_list",
            "t1_total_score", "t1_overs", "t1_extras",
            "t1_bat_team_name", "t1_bowl_team_name",
            "_points_second_innings_saved", "_points_match_result_recorded",
            "points_table_data", "tournament_4s6s_data",
            "tournament_fours_count", "tournament_sixes_count"
        ]
        snapshot = {}
        for name in state_names:
            if hasattr(self, name):
                snapshot[name] = copy.deepcopy(getattr(self, name))

        snapshot["_ui"] = {
            "active_group_title": self.grp_active.title(),
            "end_inning_enabled": self.btn_end_inning.isEnabled(),
            "side_tab_index": self.tab_side.currentIndex(),
            "wicket_type": self.cmb_out_type.currentText(),
        }
        self._undo_stack.append(snapshot)
        if len(self._undo_stack) > self._undo_limit:
            self._undo_stack.pop(0)

        self.btn_undo.setEnabled(True)

    def undo_last_action(self):
        """Undo the most recent scoring action and refresh scorecard/Excel/vMix."""
        if not self._undo_stack:
            QMessageBox.information(self, "Undo", "There is no scoring action to undo.")
            self.btn_undo.setEnabled(False)
            return

        answer = QMessageBox.question(
            self,
            "Confirm Undo",
            "Undo the last scoring action?\n\nRuns, extras, wickets, balls and player/bowler statistics will be restored.",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.Yes
        )
        if answer != QMessageBox.Yes:
            return

        snapshot = self._undo_stack.pop()
        for name, value in snapshot.items():
            if name != "_ui":
                setattr(self, name, copy.deepcopy(value))

        ui_state = snapshot.get("_ui", {})
        self.grp_active.setTitle(ui_state.get("active_group_title", self.grp_active.title()))
        self.btn_end_inning.setEnabled(ui_state.get("end_inning_enabled", True))
        self.tab_side.setCurrentIndex(ui_state.get("side_tab_index", self.tab_side.currentIndex()))

        # Rebuild player selectors and all live score/scorecard/vMix outputs.
        self.on_batsman_change()
        self.update_score()

        # Restore wicket panel's selected dismissal type after selector refresh.
        wicket_type = ui_state.get("wicket_type", "")
        idx = self.cmb_out_type.findText(wicket_type)
        if idx >= 0:
            self.cmb_out_type.setCurrentIndex(idx)

        if hasattr(self, "update_points_table_display"):
            self.update_points_table_display()
        if hasattr(self, "save_points_data_to_file"):
            self.save_points_data_to_file()

        self.save_tournament_4s6s_data()
        self.update_tournament_4s6s_table()
        self.save_tournament_fours_counter()
        self.update_tournament_fours_vmix(trigger_overlay=False)
        self.save_tournament_sixes_counter()
        self.update_tournament_sixes_vmix(trigger_overlay=False)
        self.btn_undo.setEnabled(bool(self._undo_stack))
        QMessageBox.information(self, "Undo Complete", "Last scoring action has been undone.")

    def submit_detailed_wicket(self):
        if not self.check_match_limits(): return

        out_batsman = self.cmb_out_batsman.currentText().strip()
        out_type = self.cmb_out_type.currentText().strip()
        fielder = self.cmb_fielder.currentText().strip()
        bowler = self.txt_wkt_bowler.text().strip()

        if not out_batsman:
            QMessageBox.warning(self, "Wicket Error", "Please select OUT Batsman!")
            return

        self._push_undo_state()

        if out_type == "RETIRED HURT":
            out_desc = "retired hurt"
        elif out_type == "RETIRED OUT":
            out_desc = "retired out"
        elif out_type in ["CAUGHT", "STUMPED"]:
            out_desc = f"c {fielder} b {bowler}"
        elif out_type == "RUN OUT":
            out_desc = f"run out ({fielder})"
        elif out_type == "LBW":
            out_desc = f"lbw b {bowler}"
        else:
            out_desc = f"b {bowler}"

        current_bat_stats = self.batting_stats_t1 if self.current_innings == 1 else self.batting_stats_t2

        out_runs, out_balls, out_4s, out_6s = 0, 0, 0, 0

        if out_batsman == self.bat1_name:
            out_runs = self.bat1_runs
            out_balls = self.bat1_balls
            out_4s = self.bat1_4s
            out_6s = self.bat1_6s
        elif out_batsman == self.bat2_name:
            out_runs = self.bat2_runs
            out_balls = self.bat2_balls
            out_4s = self.bat2_4s
            out_6s = self.bat2_6s
        elif out_batsman in current_bat_stats:
            out_runs = current_bat_stats[out_batsman].get("runs", 0)
            out_balls = current_bat_stats[out_batsman].get("balls", 0)
            out_4s = current_bat_stats[out_batsman].get("4s", 0)
            out_6s = current_bat_stats[out_batsman].get("6s", 0)

        # FIX: Count this legal wicket delivery only for the striker who faced it.
        # A non-striker dismissed by Run Out must not receive a ball faced.
        if out_type not in ["RETIRED HURT", "RETIRED OUT"]:
            if self.striker_slot == 1 and out_batsman == self.bat1_name:
                self.bat1_balls += 1
                out_balls = self.bat1_balls
            elif self.striker_slot == 2 and out_batsman == self.bat2_name:
                self.bat2_balls += 1
                out_balls = self.bat2_balls


        if out_batsman not in current_bat_stats:
            current_bat_stats[out_batsman] = {}
        
        current_bat_stats[out_batsman]["runs"] = out_runs
        current_bat_stats[out_batsman]["balls"] = out_balls
        current_bat_stats[out_batsman]["4s"] = out_4s
        current_bat_stats[out_batsman]["6s"] = out_6s
        current_bat_stats[out_batsman]["out_by"] = bowler if out_type not in ["RETIRED HURT", "RETIRED OUT"] else "-"
        current_bat_stats[out_batsman]["dismissal"] = out_desc

        out_sr = f"{round((out_runs / out_balls) * 100, 2):.2f}" if out_balls > 0 else "0.00"

        self.send_to_vmix(6, "PlayerTxt.Text", out_batsman)
        self.send_to_vmix(6, "FielderBowlerTx.Text", out_desc)
        self.send_to_vmix(6, "RunTxt.Text", str(out_runs))
        self.send_to_vmix(6, "BallTxt.Text", str(out_balls))
        self.send_to_vmix(6, "FourTxt.Text", str(out_4s))
        self.send_to_vmix(6, "SixValue.Text", str(out_6s))
        self.send_to_vmix(6, "SrTxt.Text", str(out_sr))

        batting_team, _, _, _, bat_logo, _ = self.get_batting_bowling_teams()
        if bat_logo:
            img_path = bat_logo.replace("\\", "/")
            self.send_image_to_vmix(6, "TEAMLOGO.Source", img_path)

        self.trigger_timed_overlay(6, "Player Out Overlay (Input 6)", duration_ms=8000)
        
        if out_type != "RETIRED HURT":
            self.trigger_timed_overlay(22, "Wicket Animation (Input 22)", duration_ms=8000)

        self.lw_player = out_batsman
        self.lw_fielder = fielder if fielder else "-"
        self.lw_bowler = bowler if out_type not in ["RETIRED HURT", "RETIRED OUT"] else "-"
        self.lw_run = str(out_runs)
        self.lw_ball = str(out_balls)
        self.lw_outtype = out_desc

        self.txt_lw_player.setText(self.lw_player)
        self.txt_lw_fielder.setText(self.lw_fielder)
        self.txt_lw_bowler.setText(self.lw_bowler)
        self.txt_lw_run.setText(self.lw_run)
        self.txt_lw_ball.setText(self.lw_ball)
        self.txt_lw_outtype.setText(self.lw_outtype)

        self.partnership_runs = 0
        self.partnership_balls = 0
        self.partnership_4s = 0
        self.partnership_6s = 0

        if out_type == "RETIRED HURT":
            if out_batsman == self.bat1_name:
                self.bat1_name = ""
                self.striker_slot = 1
            elif out_batsman == self.bat2_name:
                self.bat2_name = ""
                self.striker_slot = 2
            
            self.update_score()
            QMessageBox.information(self, "Retired Hurt", f"{out_batsman} retired hurt and left the field.")
            self.on_batsman_change()
            return

        self.wickets += 1
        self.balls += 1
        self.bowler_balls += 1
        if out_type not in ["RUN OUT", "RETIRED OUT"]:
            self.bowler_wickets += 1

        self.this_over_balls.append("W" if out_type != "RETIRED OUT" else "ROut")
        
        fow_str = f"{self.runs}/{self.wickets} ({self.overs}.{self.balls})"
        self.fall_of_wickets_list.append(fow_str)

        if self.current_bowler_name and out_type not in ["RUN OUT", "RETIRED OUT"]:
            current_bowl_stats = self.bowling_stats_t1 if self.current_innings == 1 else self.bowling_stats_t2
            if self.current_bowler_name in current_bowl_stats:
                current_bowl_stats[self.current_bowler_name]["wickets"] = self.bowler_wickets
                current_bowl_stats[self.current_bowler_name]["balls"] = self.bowler_balls
                current_bowl_stats[self.current_bowler_name]["runs"] = self.bowler_runs
                self.check_bowler_milestone(
                    self.current_bowler_name, 
                    self.bowler_balls, 
                    self.bowler_runs, 
                    self.bowler_wickets, 
                    self.bowler_maidens
                )

        if out_batsman == self.bat1_name:
            self.bat1_runs = 0
            self.bat1_balls = 0
            self.bat1_4s = 0
            self.bat1_6s = 0
            self.bat1_name = ""
            self.striker_slot = 1
        elif out_batsman == self.bat2_name:
            self.bat2_runs = 0
            self.bat2_balls = 0
            self.bat2_4s = 0
            self.bat2_6s = 0
            self.bat2_name = ""
            self.striker_slot = 2

        self.update_score()

        if self.current_innings == 2 and self.runs >= self.target_runs:
            self.match_ended = True
            return

        max_wickets = 2 if self.is_super_over else 10
        if self.wickets >= max_wickets:
            if self.current_innings == 1: 
                self.end_first_innings()
            else: 
                self.match_ended = True
                QMessageBox.information(self, "All Out!", f"2nd Innings All Out!")
                self.handle_end_match_action()
            return

        self.process_over_and_innings_end()
        self.on_batsman_change()

    def add_runs(self, run):
        if not self.check_match_limits(): return
        self._push_undo_state()

        self.runs += run
        self.balls += 1
        self.bowler_balls += 1
        self.bowler_runs += run
        self.over_runs_count += run
        self.this_over_balls.append(str(run))

        if run == 4:
            self.fours += 1
            self.trigger_timed_overlay(7, "Four Animation (Input 7)")
            # Trigger Tournament Fours last so Input 33 is the visible Overlay 1 item.
            self.record_tournament_four()
        if run == 6:
            self.sixes += 1
            self.trigger_timed_overlay(8, "Six Animation (Input 8)")
            self.record_tournament_six()

        self.partnership_runs += run
        self.partnership_balls += 1
        if run == 4: self.partnership_4s += 1
        if run == 6: self.partnership_6s += 1

        if self.striker_slot == 1:
            self.bat1_runs += run
            self.bat1_balls += 1
            if run == 4: self.bat1_4s += 1
            if run == 6: self.bat1_6s += 1
            cur_name = self.bat1_name
            cur_runs = self.bat1_runs
            cur_balls = self.bat1_balls
            cur_4s = self.bat1_4s
            cur_6s = self.bat1_6s
        else:
            self.bat2_runs += run
            self.bat2_balls += 1
            if run == 4: self.bat2_4s += 1
            if run == 6: self.bat2_6s += 1
            cur_name = self.bat2_name
            cur_runs = self.bat2_runs
            cur_balls = self.bat2_balls
            cur_4s = self.bat2_4s
            cur_6s = self.bat2_6s

        if cur_name:
            self.record_tournament_batting(cur_name, runs=run, balls=1,
                                           fours=1 if run == 4 else 0,
                                           sixes=1 if run == 6 else 0)
            sr_val = round((cur_runs / cur_balls) * 100, 2) if cur_balls > 0 else 0.0
            self.check_batsman_milestone(cur_name, cur_runs, cur_balls, cur_4s, cur_6s, sr_val)

        if run in [1, 3]:
            self.striker_slot = 2 if self.striker_slot == 1 else 1

        self.update_score()
        
        if self.current_innings == 2 and self.runs >= self.target_runs:
            self.match_ended = True
            self.handle_end_match_action()
            return

        self.process_over_and_innings_end()

    def add_leg_bye(self, run):
        if not self.check_match_limits(): return
        self._push_undo_state()
        self.runs += run
        self.extras += run
        self.balls += 1
        self.bowler_balls += 1
        self.bowler_runs += run
        self.over_runs_count += run
        self.this_over_balls.append(f"{run}LB")

        self.partnership_balls += 1
        if self.striker_slot == 1:
            self.bat1_balls += 1
            self.record_tournament_batting(self.bat1_name, balls=1)
        else:
            self.bat2_balls += 1
            self.record_tournament_batting(self.bat2_name, balls=1)

        if run in [1, 3]: self.striker_slot = 2 if self.striker_slot == 1 else 1
        self.update_score()
        
        if self.current_innings == 2 and self.runs >= self.target_runs:
            self.match_ended = True
            self.handle_end_match_action()
            return
            
        self.process_over_and_innings_end()

    def add_bye(self, run):
        if not self.check_match_limits(): return
        self._push_undo_state()
        self.runs += run
        self.extras += run
        self.balls += 1
        self.bowler_balls += 1
        self.bowler_runs += run
        self.over_runs_count += run
        self.this_over_balls.append(f"{run}B")

        self.partnership_balls += 1
        if self.striker_slot == 1:
            self.bat1_balls += 1
            self.record_tournament_batting(self.bat1_name, balls=1)
        else:
            self.bat2_balls += 1
            self.record_tournament_batting(self.bat2_name, balls=1)

        if run in [1, 3]: self.striker_slot = 2 if self.striker_slot == 1 else 1
        self.update_score()
        
        if self.current_innings == 2 and self.runs >= self.target_runs:
            self.match_ended = True
            self.handle_end_match_action()
            return

        self.process_over_and_innings_end()

    def add_wide(self, run):
        if not self.check_match_limits(): return
        self._push_undo_state()
        
        self.trigger_timed_overlay(23, "Wide Ball Overlay (Input 23)")

        total_wide = 1 + run
        self.runs += total_wide
        self.extras += total_wide
        self.bowler_runs += total_wide
        self.over_runs_count += total_wide

        lbl_str = "WD" if run == 0 else f"{run}WD"
        self.this_over_balls.append(lbl_str)
        if run in [1, 3]: self.striker_slot = 2 if self.striker_slot == 1 else 1
        self.update_score()
        
        if self.current_innings == 2 and self.runs >= self.target_runs:
            self.match_ended = True
            self.handle_end_match_action()

    def add_no_ball(self, run):
        if not self.check_match_limits(): return
        self._push_undo_state()
        
        self.trigger_timed_overlay(11, "Free Hit Animation (Input 11)")

        total_nb = 1 + run
        self.runs += total_nb
        self.extras += 1
        self.bowler_runs += total_nb
        self.over_runs_count += total_nb

        lbl_str = "NB" if run == 0 else f"{run}NB"
        self.this_over_balls.append(lbl_str)

        if run == 4:
            self.fours += 1
            self.trigger_timed_overlay(7, "Four Animation (Input 7)")
            # Trigger Tournament Fours last so Input 33 is the visible Overlay 1 item.
            self.record_tournament_four()
        if run == 6:
            self.sixes += 1
            self.trigger_timed_overlay(8, "Six Animation (Input 8)")
            self.record_tournament_six()

        self.partnership_runs += run
        if run == 4: self.partnership_4s += 1
        if run == 6: self.partnership_6s += 1

        if self.striker_slot == 1:
            self.bat1_runs += run
            self.bat1_balls += 1
            if run == 4: self.bat1_4s += 1
            if run == 6: self.bat1_6s += 1
            cur_name = self.bat1_name
            cur_runs = self.bat1_runs
            cur_balls = self.bat1_balls
            cur_4s = self.bat1_4s
            cur_6s = self.bat1_6s
        else:
            self.bat2_runs += run
            self.bat2_balls += 1
            if run == 4: self.bat2_4s += 1
            if run == 6: self.bat2_6s += 1
            cur_name = self.bat2_name
            cur_runs = self.bat2_runs
            cur_balls = self.bat2_balls
            cur_4s = self.bat2_4s
            cur_6s = self.bat2_6s

        if cur_name:
            self.record_tournament_batting(cur_name, runs=run, balls=1,
                                           fours=1 if run == 4 else 0,
                                           sixes=1 if run == 6 else 0)
            sr_val = round((cur_runs / cur_balls) * 100, 2) if cur_balls > 0 else 0.0
            self.check_batsman_milestone(cur_name, cur_runs, cur_balls, cur_4s, cur_6s, sr_val)

        if run in [1, 3]: self.striker_slot = 2 if self.striker_slot == 1 else 1
        self.update_score()
        
        if self.current_innings == 2 and self.runs >= self.target_runs:
            self.match_ended = True
            self.handle_end_match_action()

    def reset_score(self):
        self._undo_stack.clear()
        self.btn_undo.setEnabled(False)
        self.runs = 0
        self.wickets = 0
        self.overs = 0
        self.balls = 0
        self.extras = 0
        self.fours = 0
        self.sixes = 0
        self.current_innings = 1
        self.first_innings_ended = False
        self.target_runs = 0
        self.match_ended = False
        self._points_second_innings_saved = False
        self._points_match_result_recorded = False
        self.is_super_over = False
        self.super_over_overlay_visible = False
        self.btn_toggle_so_overlay.setText("⚡ TOGGLE SUPER OVER OVERLAY (INPUT 32) [OFF]")
        self.btn_toggle_so_overlay.setStyleSheet("background-color: #e65100; color: white; font-weight: bold; padding: 12px; font-size: 13px;")
        
        self.lbl_1st_score.setText("0/0")
        self.lbl_1st_over.setText("0.0")
        self.lbl_1st_extra.setText("0")

        self.txt_lw_player.clear()
        self.txt_lw_fielder.clear()
        self.txt_lw_bowler.clear()
        self.txt_lw_run.setText("0")
        self.txt_lw_ball.setText("0")
        self.txt_lw_outtype.clear()

        self.partnership_runs = 0
        self.partnership_balls = 0
        self.partnership_4s = 0
        self.partnership_6s = 0

        self.batting_stats_t1.clear()
        self.batting_stats_t2.clear()
        self.bowling_stats_t1.clear()
        self.bowling_stats_t2.clear()

        self.bat1_name = ""
        self.bat2_name = ""
        self.current_bowler_name = ""
        self.bat1_runs = 0
        self.bat1_balls = 0
        self.bat1_4s = 0
        self.bat1_6s = 0
        self.bat2_runs = 0
        self.bat2_balls = 0
        self.bat2_4s = 0
        self.bat2_6s = 0
        
        self.bowler_balls = 0
        self.bowler_runs = 0
        self.bowler_wickets = 0
        self.bowler_maidens = 0
        self.over_runs_count = 0
        self.last_bowler_name = ""
        self.over_completed_need_new_bowler = False
        self.this_over_balls.clear()
        self.fall_of_wickets_list.clear()

        for table in [self.tbl_full_batting, self.tbl_full_bowling, self.tbl_full_batting2, self.tbl_full_bowling2, self.tbl_sum_t1_bat, self.tbl_sum_t2_bowl, self.tbl_sum_t2_bat, self.tbl_sum_t1_bowl]:
            table.clearContents()

        self.grp_active.setTitle("1st Innings Active Players & Live Scorecard Stats")
        self.btn_end_inning.setEnabled(True)
        self.refresh_active_players_dropdowns()
        self.tab_side.setCurrentIndex(0)
        self.update_score()
        QMessageBox.information(self, "Match Reset", "Match score has been successfully reset for a new match!")

    def update_score(self):
        try:
            batting_team, bowling_team, bat_inputs, bowl_inputs, bat_logo, bowl_logo = self.get_batting_bowling_teams()
            match_overs = self.txt_match_overs.text().strip() or "20"
            
            try:
                if "." in match_overs:
                    m_ov_part, m_bl_part = map(int, match_overs.split("."))
                    total_match_balls = (m_ov_part * 6) + m_bl_part
                else:
                    total_match_balls = int(match_overs) * 6
            except ValueError:
                total_match_balls = 6

            bat1_name = self.bat1_name or "Batsman 1"
            bat2_name = self.bat2_name or "Batsman 2"
            bowler_name = self.current_bowler_name or "Bowler"

            current_bat_stats = self.batting_stats_t1 if self.current_innings == 1 else self.batting_stats_t2
            current_bowl_stats = self.bowling_stats_t1 if self.current_innings == 1 else self.bowling_stats_t2

            if self.bat1_name and self.bat1_name in current_bat_stats and current_bat_stats[self.bat1_name]["dismissal"] not in ["CAUGHT", "BOWLED", "LBW", "RUN OUT", "STUMPED", "HIT WICKET", "RETIRED OUT", "RETIRED HURT"]:
                current_bat_stats[self.bat1_name]["dismissal"] = "NOT OUT"

            if self.bat2_name and self.bat2_name in current_bat_stats and current_bat_stats[self.bat2_name]["dismissal"] not in ["CAUGHT", "BOWLED", "LBW", "RUN OUT", "STUMPED", "HIT WICKET", "RETIRED OUT", "RETIRED HURT"]:
                current_bat_stats[self.bat2_name]["dismissal"] = "NOT OUT"

            if self.bat1_name and self.bat1_name in current_bat_stats and current_bat_stats[self.bat1_name]["dismissal"] in ["NOT OUT", "DNB"]:
                current_bat_stats[self.bat1_name]["runs"] = self.bat1_runs
                current_bat_stats[self.bat1_name]["balls"] = self.bat1_balls
                current_bat_stats[self.bat1_name]["4s"] = self.bat1_4s
                current_bat_stats[self.bat1_name]["6s"] = self.bat1_6s

            if self.bat2_name and self.bat2_name in current_bat_stats and current_bat_stats[self.bat2_name]["dismissal"] in ["NOT OUT", "DNB"]:
                current_bat_stats[self.bat2_name]["runs"] = self.bat2_runs
                current_bat_stats[self.bat2_name]["balls"] = self.bat2_balls
                current_bat_stats[self.bat2_name]["4s"] = self.bat2_4s
                current_bat_stats[self.bat2_name]["6s"] = self.bat2_6s

            if bowler_name in current_bowl_stats:
                current_bowl_stats[bowler_name]["balls"] = self.bowler_balls
                current_bowl_stats[bowler_name]["runs"] = self.bowler_runs
                current_bowl_stats[bowler_name]["wickets"] = self.bowler_wickets
                current_bowl_stats[bowler_name]["maidens"] = self.bowler_maidens

            self.update_wkt_preview_stats()

            self.txt_part_bat1.setText(bat1_name)
            self.txt_part_bat2.setText(bat2_name)
            self.txt_part_runs.setText(str(self.partnership_runs))
            self.txt_part_balls.setText(str(self.partnership_balls))
            self.txt_part_4s.setText(str(self.partnership_4s))
            self.txt_part_6s.setText(str(self.partnership_6s))

            sr1 = f"{round((self.bat1_runs / self.bat1_balls) * 100, 2):.2f}" if self.bat1_balls > 0 else "0.00"
            sr2 = f"{round((self.bat2_runs / self.bat2_balls) * 100, 2):.2f}" if self.bat2_balls > 0 else "0.00"

            p1_disp = f"> {bat1_name}" if self.striker_slot == 1 else bat1_name
            p2_disp = f"> {bat2_name}" if self.striker_slot == 2 else bat2_name

            self.tbl_batsmen.setItem(0, 0, QTableWidgetItem(p1_disp))
            self.tbl_batsmen.setItem(0, 1, QTableWidgetItem(str(self.bat1_runs)))
            self.tbl_batsmen.setItem(0, 2, QTableWidgetItem(str(self.bat1_balls)))
            self.tbl_batsmen.setItem(0, 3, QTableWidgetItem(str(self.bat1_4s)))
            self.tbl_batsmen.setItem(0, 4, QTableWidgetItem(str(self.bat1_6s)))
            self.tbl_batsmen.setItem(0, 5, QTableWidgetItem(sr1))

            self.tbl_batsmen.setItem(1, 0, QTableWidgetItem(p2_disp))
            self.tbl_batsmen.setItem(1, 1, QTableWidgetItem(str(self.bat2_runs)))
            self.tbl_batsmen.setItem(1, 2, QTableWidgetItem(str(self.bat2_balls)))
            self.tbl_batsmen.setItem(1, 3, QTableWidgetItem(str(self.bat2_4s)))
            self.tbl_batsmen.setItem(1, 4, QTableWidgetItem(str(self.bat2_6s)))
            self.tbl_batsmen.setItem(1, 5, QTableWidgetItem(sr2))

            b_ov = self.bowler_balls // 6
            b_rem = self.bowler_balls % 6
            b_overs_str = f"{b_ov}.{b_rem}"

            self.tbl_bowler.setItem(0, 0, QTableWidgetItem(bowler_name))
            self.tbl_bowler.setItem(0, 1, QTableWidgetItem(b_overs_str))
            self.tbl_bowler.setItem(0, 2, QTableWidgetItem(str(self.bowler_maidens)))
            self.tbl_bowler.setItem(0, 3, QTableWidgetItem(str(self.bowler_runs)))
            self.tbl_bowler.setItem(0, 4, QTableWidgetItem(str(self.bowler_wickets)))

            this_over_str = " ".join(self.this_over_balls)
            self.lbl_this_over.setText(f"THIS OVER:  {this_over_str}")

            tot_overs_float = self.overs + (self.balls / 6.0)
            crr_val = f"{round(self.runs / tot_overs_float, 2):.2f}" if tot_overs_float > 0 else "0.00"

            if self.current_innings == 1:
                self.lbl_1st_score.setText(f"{self.runs}/{self.wickets}")
                self.lbl_1st_over.setText(f"{self.overs}.{self.balls}")
                self.lbl_1st_extra.setText(str(self.extras))

            self.lbl_live_total.setText(str(self.runs))
            self.lbl_live_wickets.setText(str(self.wickets))
            self.lbl_live_over.setText(f"{self.overs}.{self.balls}")
            self.lbl_live_crr.setText(crr_val)
            self.lbl_live_4s.setText(str(self.fours))
            self.lbl_live_6s.setText(str(self.sixes))
            self.lbl_live_co.setText(b_overs_str)
            self.lbl_live_extra.setText(str(self.extras))

            if self.current_innings == 2:
                need_runs = self.target_runs - self.runs
                rem_balls = total_match_balls - ((self.overs * 6) + self.balls)
                rem_overs_float = rem_balls / 6.0
                rrr_val = f"{round(need_runs / rem_overs_float, 2):.2f}" if rem_overs_float > 0 else "0.00"

                self.lbl_2nd_total.setText(f"{self.runs}/{self.wickets}")
                self.lbl_2nd_over.setText(f"{self.overs}.{self.balls}")
                self.lbl_2nd_rrr.setText(rrr_val)
                self.lbl_2nd_need.setText(str(need_runs))
                self.lbl_2nd_from.setText(f"{rem_balls // 6}.{rem_balls % 6}")
                self.lbl_2nd_extras.setText(str(self.extras))

                self.lbl_teams.setText(f"{batting_team} (BAT) VS {bowling_team} (BOWL) - NEED {need_runs} RUNS")
            else:
                self.lbl_teams.setText(f"{batting_team} (BAT) VS {bowling_team} (BOWL) - {match_overs} OVERS")

            score_str = f"{self.runs}/{self.wickets} ({self.overs}.{self.balls})"
            self.lbl_score.setText(score_str)

            t1_bat_inps = self.t1_bat_player_inputs if self.first_innings_ended else self.get_1st_innings_teams()[2]
            t1_bowl_inps = self.t1_bowl_player_inputs if self.first_innings_ended else self.get_1st_innings_teams()[3]
            t1_name, t2_name, _, _, _, _ = self.get_1st_innings_teams()

            t_bat1_players = [inp.text().strip() for inp in t1_bat_inps if inp.text().strip()]
            row_idx = 0
            for idx, p_name in enumerate(t_bat1_players):
                if row_idx < self.tbl_full_batting.rowCount():
                    st = self.batting_stats_t1.get(p_name, {"runs": 0, "balls": 0, "4s": 0, "6s": 0, "out_by": "", "dismissal": "DNB"})
                    if st['dismissal'] != "DNB":
                        sr_val = f"{round((st['runs'] / st['balls']) * 100, 2):.2f}" if st['balls'] > 0 else "0.00"
                        self.tbl_full_batting.setItem(row_idx, 0, QTableWidgetItem(p_name))
                        self.tbl_full_batting.setItem(row_idx, 1, QTableWidgetItem(str(st['runs'])))
                        self.tbl_full_batting.setItem(row_idx, 2, QTableWidgetItem(str(st['balls'])))
                        self.tbl_full_batting.setItem(row_idx, 3, QTableWidgetItem(str(st['4s'])))
                        self.tbl_full_batting.setItem(row_idx, 4, QTableWidgetItem(str(st['6s'])))
                        self.tbl_full_batting.setItem(row_idx, 5, QTableWidgetItem(sr_val))
                        self.tbl_full_batting.setItem(row_idx, 6, QTableWidgetItem(st['out_by']))
                        self.tbl_full_batting.setItem(row_idx, 7, QTableWidgetItem(st['dismissal']))
                        row_idx += 1

            t_bowl1_players = [inp.text().strip() for inp in t1_bowl_inps if inp.text().strip()]
            bowl_row_idx = 0
            for idx, b_name in enumerate(t_bowl1_players):
                if bowl_row_idx < self.tbl_full_bowling.rowCount():
                    bst = self.bowling_stats_t1.get(b_name, {"balls": 0, "maidens": 0, "runs": 0, "wickets": 0})
                    if bst['balls'] > 0 or b_name == self.current_bowler_name:
                        b_ov_num = bst['balls'] // 6
                        b_rem_num = bst['balls'] % 6
                        b_ov_text = f"{b_ov_num}.{b_rem_num}"
                        tot_ov_float = b_ov_num + (b_rem_num / 6.0)
                        eco_text = f"{round(bst['runs'] / tot_ov_float, 2):.2f}" if tot_ov_float > 0 else "0.00"

                        self.tbl_full_bowling.setItem(bowl_row_idx, 0, QTableWidgetItem(b_name))
                        self.tbl_full_bowling.setItem(bowl_row_idx, 1, QTableWidgetItem(b_ov_text))
                        self.tbl_full_bowling.setItem(bowl_row_idx, 2, QTableWidgetItem(str(bst['maidens'])))
                        self.tbl_full_bowling.setItem(bowl_row_idx, 3, QTableWidgetItem(str(bst['runs'])))
                        self.tbl_full_bowling.setItem(bowl_row_idx, 4, QTableWidgetItem(str(bst['wickets'])))
                        self.tbl_full_bowling.setItem(bowl_row_idx, 5, QTableWidgetItem(eco_text))
                        bowl_row_idx += 1

            if self.current_innings == 2 or self.first_innings_ended:
                t_bat2_players = [inp.text().strip() for inp in bat_inputs if inp.text().strip()]
                r2_idx = 0
                for idx, p_name in enumerate(t_bat2_players):
                    if r2_idx < self.tbl_full_batting2.rowCount():
                        st = self.batting_stats_t2.get(p_name, {"runs": 0, "balls": 0, "4s": 0, "6s": 0, "out_by": "", "dismissal": "DNB"})
                        if st['dismissal'] != "DNB":
                            sr_val = f"{round((st['runs'] / st['balls']) * 100, 2):.2f}" if st['balls'] > 0 else "0.00"
                            self.tbl_full_batting2.setItem(r2_idx, 0, QTableWidgetItem(p_name))
                            self.tbl_full_batting2.setItem(r2_idx, 1, QTableWidgetItem(str(st['runs'])))
                            self.tbl_full_batting2.setItem(r2_idx, 2, QTableWidgetItem(str(st['balls'])))
                            self.tbl_full_batting2.setItem(r2_idx, 3, QTableWidgetItem(str(st['4s'])))
                            self.tbl_full_batting2.setItem(r2_idx, 4, QTableWidgetItem(str(st['6s'])))
                            self.tbl_full_batting2.setItem(r2_idx, 5, QTableWidgetItem(sr_val))
                            self.tbl_full_batting2.setItem(r2_idx, 6, QTableWidgetItem(st['out_by']))
                            self.tbl_full_batting2.setItem(r2_idx, 7, QTableWidgetItem(st['dismissal']))
                            r2_idx += 1

                t_bowl2_players = [inp.text().strip() for inp in bowl_inputs if inp.text().strip()]
                b2_idx = 0
                for idx, b_name in enumerate(t_bowl2_players):
                    if b2_idx < self.tbl_full_bowling2.rowCount():
                        bst = self.bowling_stats_t2.get(b_name, {"balls": 0, "maidens": 0, "runs": 0, "wickets": 0})
                        if bst['balls'] > 0 or b_name == self.current_bowler_name:
                            b_ov_num = bst['balls'] // 6
                            b_rem_num = bst['balls'] % 6
                            b_ov_text = f"{b_ov_num}.{b_rem_num}"
                            tot_ov_float = b_ov_num + (b_rem_num / 6.0)
                            eco_text = f"{round(bst['runs'] / tot_ov_float, 2):.2f}" if tot_ov_float > 0 else "0.00"

                            self.tbl_full_bowling2.setItem(b2_idx, 0, QTableWidgetItem(b_name))
                            self.tbl_full_bowling2.setItem(b2_idx, 1, QTableWidgetItem(b_ov_text))
                            self.tbl_full_bowling2.setItem(b2_idx, 2, QTableWidgetItem(str(bst['maidens'])))
                            self.tbl_full_bowling2.setItem(b2_idx, 3, QTableWidgetItem(str(bst['runs'])))
                            self.tbl_full_bowling2.setItem(b2_idx, 4, QTableWidgetItem(str(bst['wickets'])))
                            self.tbl_full_bowling2.setItem(b2_idx, 5, QTableWidgetItem(eco_text))
                            b2_idx += 1

            s_t1_name, s_t2_name, _, _, _, _ = self.get_1st_innings_teams()
            
            t1_score_str = self.t1_total_score if self.first_innings_ended or self.current_innings == 2 else f"{self.runs}/{self.wickets}"
            t1_over_str = self.t1_overs if self.first_innings_ended or self.current_innings == 2 else f"{self.overs}.{self.balls}"
            t1_extra_str = self.t1_extras if self.first_innings_ended or self.current_innings == 2 else str(self.extras)

            self.txt_sum_t1_name.setText(s_t1_name)
            self.txt_sum_t1_score.setText(t1_score_str)
            self.txt_sum_t1_overs.setText(t1_over_str)
            self.txt_sum_t1_extras.setText(t1_extra_str)

            t2_score_str = f"{self.runs}/{self.wickets}" if self.current_innings == 2 else "0/0"
            t2_over_str = f"{self.overs}.{self.balls}" if self.current_innings == 2 else "0.0"
            t2_extra_str = str(self.extras) if self.current_innings == 2 else "0"

            self.txt_sum_t2_name.setText(s_t2_name)
            self.txt_sum_t2_score.setText(t2_score_str)
            self.txt_sum_t2_overs.setText(t2_over_str)
            self.txt_sum_t2_extras.setText(t2_extra_str)

            t1_all_bat_stats = []
            active_t1_bat_inps = self.t1_bat_player_inputs if self.first_innings_ended else self.get_1st_innings_teams()[2]
            for inp in active_t1_bat_inps:
                p_n = inp.text().strip()
                if p_n:
                    st_d = self.batting_stats_t1.get(p_n, {"runs": 0, "balls": 0, "dismissal": "DNB"})
                    t1_all_bat_stats.append((p_n, st_d.get("runs", 0), st_d.get("balls", 0)))
            
            self.tbl_sum_t1_bat.clearContents()
            for r_i in range(11):
                if r_i < len(t1_all_bat_stats):
                    p_n, p_r, p_b = t1_all_bat_stats[r_i]
                    sr_v = f"{round((p_r / p_b) * 100, 2):.2f}" if p_b > 0 else "0.00"
                    self.tbl_sum_t1_bat.setItem(r_i, 0, QTableWidgetItem(p_n))
                    self.tbl_sum_t1_bat.setItem(r_i, 1, QTableWidgetItem(str(p_r)))
                    self.tbl_sum_t1_bat.setItem(r_i, 2, QTableWidgetItem(str(p_b)))
                    self.tbl_sum_t1_bat.setItem(r_i, 3, QTableWidgetItem(sr_v))

            t2_all_bowl_stats = []
            active_t2_bowl_inps = self.t1_bowl_player_inputs if self.first_innings_ended else self.get_1st_innings_teams()[3]
            for inp in active_t2_bowl_inps:
                b_n = inp.text().strip()
                if b_n:
                    bst_d = self.bowling_stats_t1.get(b_n, {"balls": 0, "runs": 0, "wickets": 0})
                    t2_all_bowl_stats.append((b_n, bst_d.get("balls", 0), bst_d.get("runs", 0), bst_d.get("wickets", 0)))

            self.tbl_sum_t2_bowl.clearContents()
            for r_i in range(11):
                if r_i < len(t2_all_bowl_stats):
                    b_n, b_bl, b_r, b_w = t2_all_bowl_stats[r_i]
                    ov_txt = f"{b_bl // 6}.{b_bl % 6}"
                    self.tbl_sum_t2_bowl.setItem(r_i, 0, QTableWidgetItem(b_n))
                    self.tbl_sum_t2_bowl.setItem(r_i, 1, QTableWidgetItem(ov_txt))
                    self.tbl_sum_t2_bowl.setItem(r_i, 2, QTableWidgetItem(str(b_r)))
                    self.tbl_sum_t2_bowl.setItem(r_i, 3, QTableWidgetItem(str(b_w)))

            t2_all_bat_stats = []
            _, _, t2_bat_inps_live, _, _, _ = self.get_batting_bowling_teams()
            for inp in t2_bat_inps_live:
                p_n = inp.text().strip()
                if p_n:
                    st_d = self.batting_stats_t2.get(p_n, {"runs": 0, "balls": 0, "dismissal": "DNB"})
                    t2_all_bat_stats.append((p_n, st_d.get("runs", 0), st_d.get("balls", 0)))

            self.tbl_sum_t2_bat.clearContents()
            for r_i in range(11):
                if r_i < len(t2_all_bat_stats):
                    p_n, p_r, p_b = t2_all_bat_stats[r_i]
                    sr_v = f"{round((p_r / p_b) * 100, 2):.2f}" if p_b > 0 else "0.00"
                    self.tbl_sum_t2_bat.setItem(r_i, 0, QTableWidgetItem(p_n))
                    self.tbl_sum_t2_bat.setItem(r_i, 1, QTableWidgetItem(str(p_r)))
                    self.tbl_sum_t2_bat.setItem(r_i, 2, QTableWidgetItem(str(p_b)))
                    self.tbl_sum_t2_bat.setItem(r_i, 3, QTableWidgetItem(sr_v))

            t1_all_bowl_stats = []
            _, _, _, t1_bowl_inps_live, _, _ = self.get_batting_bowling_teams()
            for inp in t1_bowl_inps_live:
                b_n = inp.text().strip()
                if b_n:
                    bst_d = self.bowling_stats_t2.get(b_n, {"balls": 0, "runs": 0, "wickets": 0})
                    t1_all_bowl_stats.append((b_n, bst_d.get("balls", 0), bst_d.get("runs", 0), bst_d.get("wickets", 0)))

            self.tbl_sum_t1_bowl.clearContents()
            for r_i in range(11):
                if r_i < len(t1_all_bowl_stats):
                    b_n, b_bl, b_r, b_w = t1_all_bowl_stats[r_i]
                    ov_txt = f"{b_bl // 6}.{b_bl % 6}"
                    self.tbl_sum_t1_bowl.setItem(r_i, 0, QTableWidgetItem(b_n))
                    self.tbl_sum_t1_bowl.setItem(r_i, 1, QTableWidgetItem(ov_txt))
                    self.tbl_sum_t1_bowl.setItem(r_i, 2, QTableWidgetItem(str(b_r)))
                    self.tbl_sum_t1_bowl.setItem(r_i, 3, QTableWidgetItem(str(b_w)))

            if self.current_innings == 2 or self.first_innings_ended:
                self.txt_sum_target.setText(str(self.target_runs))
                need_r = max(0, self.target_runs - self.runs)
                self.txt_sum_need.setText(str(need_r))
                
                rem_b = total_match_balls - ((self.overs * 6) + self.balls)
                rem_o_f = rem_b / 6.0
                rrr_f = f"{round(need_r / rem_o_f, 2):.2f}" if rem_o_f > 0 else "0.00"
                self.txt_sum_rrr.setText(rrr_f)
            else:
                self.txt_sum_target.setText("-")
                self.txt_sum_need.setText("-")
                self.txt_sum_rrr.setText("-")

            if self.current_innings == 2 and self.runs >= self.target_runs:
                self.match_ended = True
                self.txt_sum_result.setText(f"{s_t2_name} WON BY {10 - self.wickets} WICKETS")
                self.txt_sum_status.setText("MATCH COMPLETE")
            elif self.match_ended or (self.current_innings == 2 and (((self.overs * 6) + self.balls >= total_match_balls) or self.wickets >= (2 if self.is_super_over else 10))):
                if self.runs < self.target_runs - 1:
                    diff = (self.target_runs - 1) - self.runs
                    self.txt_sum_result.setText(f"{s_t1_name} WON BY {diff} RUNS")
                else:
                    self.txt_sum_result.setText("MATCH TIED")
                self.txt_sum_status.setText("MATCH COMPLETE")
            else:
                self.txt_sum_result.setText("MATCH IN PROGRESS")
                self.txt_sum_status.setText("LIVE")

            target_disp_val = str(self.target_runs) if self.first_innings_ended or self.current_innings == 2 else "-"
            
            if self.current_innings == 1 and not self.first_innings_ended:
                current_ov_disp_val = match_overs
                tot_ov_f = self.overs + (self.balls / 6.0)
                run_rate_disp = f"{round(self.runs / tot_ov_f, 2):.2f}" if tot_ov_f > 0 else "0.00"
            elif self.first_innings_ended and self.current_innings == 2 and self.overs == 0 and self.balls == 0:
                current_ov_disp_val = match_overs
                run_rate_disp = crr_val if crr_val != "0.00" else "0.00"
            else:
                current_ov_disp_val = f"{self.overs}.{self.balls}"
                tot_ov_f = self.overs + (self.balls / 6.0)
                run_rate_disp = f"{round(self.runs / tot_ov_f, 2):.2f}" if tot_ov_f > 0 else "0.00"

            self.send_to_vmix(16, "TEAMNAMETXT.Text", batting_team)
            self.send_to_vmix(16, "TARGETTXT.Text", target_disp_val)
            self.send_to_vmix(16, "OVERTXT.Text", current_ov_disp_val)
            self.send_to_vmix(16, "RUNRATETXT.Text", run_rate_disp)

            if bat_logo:
                self.send_image_to_vmix(16, "TEAMLOGO.Source", bat_logo.replace("\\", "/"))

            self.send_to_vmix(17, "TEAMNAMETXT.Text", batting_team)
            self.send_to_vmix(17, "TEAMNAMEVS.Text", f"VS {bowling_team}")
            self.send_to_vmix(17, "SCORETXT.Text", f"{self.runs}/{self.wickets}")
            self.send_to_vmix(17, "OVERSTXT.Text", f"{self.overs}.{self.balls}")
            
            t1_name_val = self.txt_team1.text().strip() or "TEAM A"
            active_bat_logo = self.logo_a_path if batting_team == t1_name_val else self.logo_b_path
            active_bowl_logo = self.logo_b_path if batting_team == t1_name_val else self.logo_a_path

            if active_bat_logo:
                img_bat = active_bat_logo.replace("\\", "/")
                self.send_image_to_vmix(17, "Team1logo.Source", img_bat)
                self.send_image_to_vmix(17, "TEAMALOGO.Source", img_bat)
                self.send_image_to_vmix(17, "TEAMALOGO3.Source", img_bat)
                self.send_image_to_vmix(17, "TEAMALOGO8.Source", img_bat)

            if active_bowl_logo:
                img_bowl = active_bowl_logo.replace("\\", "/")
                self.send_image_to_vmix(17, "Team2logo.Source", img_bowl)
                self.send_image_to_vmix(17, "TEAMBLOGO.Source", img_bowl)
                self.send_image_to_vmix(17, "TEAMBLOGO3.Source", img_bowl)
                self.send_image_to_vmix(17, "TEAMBLOGO8.Source", img_bowl)

            if self.current_innings == 2:
                need_runs_val = max(0, self.target_runs - self.runs)
                rem_b_val = total_match_balls - ((self.overs * 6) + self.balls)
                rem_o_num = rem_b_val // 6
                rem_b_num = rem_b_val % 6
                
                need_text_str = f"NEED {need_runs_val} RUNS FROM {rem_o_num}.{rem_b_num} OV" if need_runs_val > 0 else f"{batting_team} WON"
                self.send_to_vmix(17, "NEEDRUNFROMTEXT.Text", need_text_str)

                rem_o_f = rem_b_val / 6.0
                rrr_str = f"RRR: {round(need_runs_val / rem_o_f, 2):.2f}" if rem_o_f > 0 else "RRR: 0.00"
                self.send_to_vmix(17, "RUNRATEBATINTXT.Text", rrr_str)
            else:
                self.send_to_vmix(17, "NEEDRUNFROMTEXT.Text", f"TARGET: {self.target_runs if self.first_innings_ended else '1st INNINGS'}")
                tot_ov_f = self.overs + (self.balls / 6.0)
                crr_str = f"CRR: {round(self.runs / tot_ov_f, 2):.2f}" if tot_ov_f > 0 else "CRR: 0.00"
                self.send_to_vmix(17, "RUNRATEBATINTXT.Text", crr_str)

            self.send_to_vmix(17, "MATCHOVERTXT.Text", f"{match_overs} OVERS")

            self.send_to_vmix(18, "TEAMNAMETXT.Text", batting_team)
            self.send_to_vmix(18, "TEAMNAMEVS.Text", f"VS {bowling_team}")
            self.send_to_vmix(18, "SCORETXT.Text", f"{self.runs}/{self.wickets}")
            self.send_to_vmix(18, "OVERSTXT.Text", f"{self.overs}.{self.balls}")
            self.send_to_vmix(18, "MATCHOVERTXT.Text", f"{match_overs} OVERS")

            if self.current_innings == 2:
                need_runs_val = max(0, self.target_runs - self.runs)
                rem_b_val = total_match_balls - ((self.overs * 6) + self.balls)
                
                self.send_to_vmix(18, "TARGETTXT.Text", str(self.target_runs))
                self.send_to_vmix(18, "RUNSNEEDEDTXT.Text", str(need_runs_val))
                self.send_to_vmix(18, "BALLSLEFTTXT.Text", str(rem_b_val))

                rem_o_f = rem_b_val / 6.0
                rrr_str = f"{round(need_runs_val / rem_o_f, 2):.2f}" if rem_o_f > 0 else "0.00"
                self.send_to_vmix(18, "REQRATETXT.Text", rrr_str)
            else:
                self.send_to_vmix(18, "TARGETTXT.Text", str(self.target_runs) if self.first_innings_ended else "0")
                self.send_to_vmix(18, "RUNSNEEDEDTXT.Text", "0")
                self.send_to_vmix(18, "BALLSLEFTTXT.Text", str(total_match_balls))
                self.send_to_vmix(18, "REQRATETXT.Text", "0.00")

            if active_bat_logo:
                self.send_image_to_vmix(18, "TEAMALOGO10.Source", active_bat_logo.replace("\\", "/"))
            if active_bowl_logo:
                self.send_image_to_vmix(18, "TEAMBLOGO10.Source", active_bowl_logo.replace("\\", "/"))

            if self.current_innings == 2:
                _, _, t2_bat_inps, t2_bowl_inps, _, _ = self.get_batting_bowling_teams()
                self.update_input_19_data(batting_team, t2_bat_inps, f"{self.runs}/{self.wickets}", f"{self.overs}.{self.balls}", str(self.extras), final_freeze=False)
                self.update_input_20_data(bowling_team, t2_bowl_inps, f"{self.runs}/{self.wickets}", f"{self.overs}.{self.balls}", str(self.extras), final_freeze=False)

            self.send_to_vmix(17, "Player1name.Text", p1_disp)
            self.send_to_vmix(17, "Player1run.Text", str(self.bat1_runs))
            self.send_to_vmix(17, "Player1ball.Text", str(self.bat1_balls))

            self.send_to_vmix(17, "Player2name.Text", p2_disp)
            self.send_to_vmix(17, "Player2run.Text", str(self.bat2_runs))
            self.send_to_vmix(17, "Player2ball.Text", str(self.bat2_balls))

            self.send_to_vmix(17, "Bowlernamecurr.Text", bowler_name)
            self.send_to_vmix(17, "Bowlerlover.Text", b_overs_str)
            self.send_to_vmix(17, "bowlerRun.Text", str(self.bowler_runs))
            self.send_to_vmix(17, "bowlerWkt.Text", str(self.bowler_wickets))
            self.send_to_vmix(17, "thisoverrun.Text", this_over_str)

            if not self.first_innings_ended:
                t1_bat_name, t1_bowl_name, t1_bat_inps, t1_bowl_inps, _, _ = self.get_1st_innings_teams()
                self.update_input_14_data(t1_bat_name, t1_bat_inps, f"{self.runs}/{self.wickets}", f"{self.overs}.{self.balls}", str(self.extras), final_freeze=False)
                self.update_input_15_data(t1_bowl_name, t1_bowl_inps, f"{self.runs}/{self.wickets}", f"{self.overs}.{self.balls}", str(self.extras), final_freeze=False)

            self.update_input_21_data()

            t1_team_name = self.txt_team1.text().strip() or "TEAM A"
            t2_team_name = self.txt_team2.text().strip() or "TEAM B"
            toss_info_str = self.txt_toss_details.text().strip()

            self.send_to_vmix(2, "TEAMANAMETXT.Text", t1_team_name)
            self.send_to_vmix(2, "TEAMBNAMETXT.Text", t2_team_name)
            self.send_to_vmix(2, "TOSSTEXT.Text", toss_info_str)

            if self.logo_a_path: 
                img_a = self.logo_a_path.replace("\\", "/")
                self.send_image_to_vmix(2, "TEAMALOGO.Source", img_a)
                self.send_image_to_vmix(2, "TEAMALOGO3.Source", img_a)
                self.send_image_to_vmix(2, "Team1logo.Source", img_a)

            if self.logo_b_path: 
                img_b = self.logo_b_path.replace("\\", "/")
                self.send_image_to_vmix(2, "TEAMBLOGO.Source", img_b)
                self.send_image_to_vmix(2, "TEAMBLOGO3.Source", img_b)
                self.send_image_to_vmix(2, "Team2logo.Source", img_b)

            self.send_to_vmix(3, "TEAMATXT.Text", t1_team_name)
            self.send_to_vmix(3, "TEAMBTXT.Text", t2_team_name)
            self.send_to_vmix(3, "TEAMANAME.Text", t1_team_name)
            self.send_to_vmix(3, "TEAMBNAME.Text", t2_team_name)
            self.send_to_vmix(3, "TOSSINFO.Text", toss_info_str)

            if self.logo_a_path:
                img_a = self.logo_a_path.replace("\\", "/")
                self.send_image_to_vmix(3, "TEAMALOGO3.Source", img_a)
                self.send_image_to_vmix(3, "TEAMALOGO.Source", img_a)
                self.send_image_to_vmix(3, "Team1logo.Source", img_a)

            if self.logo_b_path:
                img_b = self.logo_b_path.replace("\\", "/")
                self.send_image_to_vmix(3, "TEAMBLOGO3.Source", img_b)
                self.send_image_to_vmix(3, "TEAMBLOGO.Source", img_b)
                self.send_image_to_vmix(3, "Team2logo.Source", img_b)

            for i in range(11):
                self.send_to_vmix(3, f"A{i+1}.Text", self.team1_inputs[i].text().strip())
                self.send_to_vmix(3, f"B{i+1}.Text", self.team2_inputs[i].text().strip())

            self.send_to_vmix(4, "LEAGUENAMETXT.Text", f"{t1_team_name} vs {t2_team_name}")
            self.send_to_vmix(4, "PARTNERSHIPRUN.Text", str(self.partnership_runs))
            self.send_to_vmix(4, "PARTNERSHIPBALL.Text", f"{self.partnership_balls} BALLS")
            self.send_to_vmix(4, "BATTER1NAMETXT.Text", bat1_name)
            self.send_to_vmix(4, "BATTERRUNTEXT1.Text", str(self.bat1_runs))
            self.send_to_vmix(4, "BATTERBALLTEXT1.Text", str(self.bat1_balls))
            self.send_to_vmix(4, "BATTER2NAMETXT.Text", bat2_name)
            self.send_to_vmix(4, "BATTERRUNTEXT2.Text", str(self.bat2_runs))
            self.send_to_vmix(4, "BATTERBALLTEXT2.Text", str(self.bat2_balls))
            
            self.auto_save_match_to_excel()

        except Exception as e:
            print(f"Error in update_score: {e}")

    def send_to_vmix(self, input_no, selected_name, text_value):
        try: requests.get(f"{self.get_base_url()}?Function=SetText&Input={input_no}&SelectedName={quote(selected_name)}&Value={quote(str(text_value))}", timeout=0.2)
        except: pass

    def send_image_to_vmix(self, input_no, selected_name, image_path):
        try: requests.get(f"{self.get_base_url()}?Function=SetImage&Input={input_no}&SelectedName={quote(selected_name)}&Value={quote(str(image_path))}", timeout=0.3)
        except: pass

if __name__ == "__main__":
    app = QApplication(sys.argv)
    win = SimpleCricketGUI()
    win.show()
    sys.exit(app.exec_())