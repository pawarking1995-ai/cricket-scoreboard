class MatchEngine:
    def __init__(self):
        self.team_score = 0
        self.wickets = 0
        self.current_over = 0
        self.current_ball = 0
        self.current_innings = 1
        
        self.bat1_runs = 0
        self.bat1_balls = 0
        self.bat2_runs = 0
        self.bat2_balls = 0
        self.striker_slot = 1  # 1 or 2
        
        self.bowler_name = ""
        self.bowler_balls = 0
        self.bowler_runs = 0
        self.bowler_wickets = 0
        
        self.this_over_balls = []

    def add_runs(self, runs):
        self.team_score += runs
        self.bowler_runs += runs
        self.bowler_balls += 1
        self.current_ball += 1
        
        # Striker Runs Update
        if self.striker_slot == 1:
            self.bat1_runs += runs
            self.bat1_balls += 1
        else:
            self.bat2_runs += runs
            self.bat2_balls += 1
            
        self.this_over_balls.append(str(runs))
        
        # Strike Change on Odd Runs
        if runs in [1, 3]:
            self.swap_strike()

        # Over Finish Logic
        if self.current_ball == 6:
            self.current_over += 1
            self.current_ball = 0
            self.this_over_balls.clear()
            self.swap_strike() # Over à¤¸à¤‚à¤ªà¤²à¥à¤¯à¤¾à¤µà¤° à¤¸à¥à¤Ÿà¥à¤°à¤¾à¤‡à¤• à¤¬à¤¦à¤²à¤¤à¥‹

    def swap_strike(self):
        self.striker_slot = 2 if self.striker_slot == 1 else 1

    def get_crr(self):
        total_legal_balls = (self.current_over * 6) + self.current_ball
        if total_legal_balls == 0:
            return "0.00"
        return f"{round((self.team_score / total_legal_balls) * 6, 2):.2f}"
