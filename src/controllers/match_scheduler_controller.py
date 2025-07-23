from datetime import datetime, timedelta
import random

class MatchSchedulerService:
    @staticmethod
    def generateRoundRobinMatches(teams, options):
        if not isinstance(teams, list) or len(teams) < 4:
            raise ValueError("At least 4 teams are required to generate league matches.")
        
        required_option_keys = ["league_id","division_id"]
        for key in required_option_keys:
            if key not in options:
                raise ValueError(f"Missing required scheduling option: {key}")
            
        if any("league_team_id" not in t for t in teams):
            raise ValueError("Each team must have a 'league_team_id' field.")
        
        if len(set(t["league_team_id"] for t in teams)) != len(teams):
            raise ValueError("Duplicate team IDs found. All teams must be unique.")
        
        teamList = list(teams)
        random.shuffle(teamList)

        matches = []
        totalRounds = len(teamList) - 1 if len(teamList) % 2 == 0 else len(teamList)
        n = len(teamList)
        half = n // 2
        # currentDate = datetime.fromisoformat(options["startDate"])

        for round_num in range(totalRounds):
            side = "left" if round_num % 2 == 0 else "right"
            for i in range(half):
                home = teamList[i]
                away = teamList[n - 1 - i]

                match = {
                    "home_team_id": home["league_team_id"],
                    "away_team_id": away["league_team_id"],
                    "duration_minutes": options.get("durationMinutes", 40),
                    "category": options.get("category"),
                    "division_id": options.get("division_id"),
                    "league_id": options["league_id"],
                    "round_number": round_num + 1,
                    "bracket_side": side,
                    "bracket_position": f"{round_num + 1}-{i + 1}",
                }

                matches.append(match)
                # currentDate += timedelta(minutes=options.get("intervalMinutes", 60))

            fixed = teamList[0]
            rotating = teamList[1:]
            rotating = [rotating[-1]] + rotating[:-1]
            teamList = [fixed] + rotating

        return matches