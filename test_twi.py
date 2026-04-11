import time
import random
import pytest
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import requests
from requests_oauthlib import OAuth1
from selenium.webdriver.chrome.options import Options
import os
import re
from selenium.webdriver.common.action_chains import ActionChains
from PIL import Image


API_KEY = os.getenv('API_KEY')
API_KEY_SECRET = os.getenv('API_KEY_SECRET')
ACCESS_TOKEN = os.getenv('ACCESS_TOKEN')
ACCESS_TOKEN_SECRET = os.getenv('ACCESS_TOKEN_SECRET')
DATAMB_EMAIL = os.getenv('DATAMB_EMAIL')
DATAMB_PASSWORD = os.getenv('DATAMB_PASSWORD')

class TestUntitled:
    def setup_method(self, method):
        chrome_options = Options()
        chrome_options.add_argument("--headless")
        chrome_options.add_argument("--disable-gpu")
        chrome_options.add_argument("--force-device-scale-factor=2")
        self.driver = webdriver.Chrome(options=chrome_options)

    def teardown_method(self):
        self.driver.quit()
        
    def capture_first_five_lines(self):
        body_element = self.driver.find_element(By.TAG_NAME, "body")
        body_text = body_element.text
    # Split the text into lines and capture the first 5 lines
        lines = body_text.splitlines()
        specific_lines = "\n".join(lines[4:9])
    
    # Replace the specified text
        replacements = {
        "1. ": "🥇 ",
        "2. ": "🥈 ",
        "3. ": "🥉 ",
        "4. ": "🏅 ",
        "5. ": "🏅 ",
        ") ": ") — "
    }
    
        for old, new in replacements.items():
            specific_lines = specific_lines.replace(old, new)

        return specific_lines

    
    def test_untitled(self):
        self.driver.get("https://datamb.football/proindex/")
        time.sleep(1)
        self.driver.set_window_size(976, 797)
        assert DATAMB_EMAIL and DATAMB_PASSWORD, (
            "Set DATAMB_EMAIL and DATAMB_PASSWORD (e.g. GitHub repo secrets)."
        )
        WebDriverWait(self.driver, 10).until(
            EC.presence_of_element_located((By.NAME, "eml"))
        ).send_keys(DATAMB_EMAIL)

        self.driver.find_element(By.NAME, "pwd").send_keys(DATAMB_PASSWORD)
        self.driver.find_element(By.CSS_SELECTOR, ".SFfrm button").click()
        WebDriverWait(self.driver, 10).until(
            EC.presence_of_element_located((By.ID, "metric"))
        )



        position_options = ["Goalkeeper", "Centre-back", "Full-back", "Midfielder", "Winger", "Striker", "All positions"]
        weights2 = [0.03, 0.09, 0.09, 0.21, 0.18, 0.17, 0.23]  # Adjust position weights

        selected_position = random.choices(position_options, weights=weights2, k=1)[0]
        # Adjust metrics
        if selected_position == "Goalkeeper":
            metric_options = [
                "Possessions won per 90", "Sliding tackles per 90", "Sliding tackles (PAdj)",
                "Interceptions per 90", "Interceptions (PAdj)",
                "Aerial duels won %", "Defensive duels won per 90", "Progressive passes per 90",
                "Passes completed per 90", "Short passes completed per 90",
                "Pass completion %", "Short pass completion %", "Long pass accuracy %",
                "Aerial duels won per 90", "Saves per 90", "Shots conceded per 90",
                "xG conceded per 90", "Prevented goals per 90", "Save percentage %"
            ]
        elif selected_position == "Centre-back":
            metric_options = [
                "Possessions won per 90", "Sliding tackles per 90", "Sliding tackles (PAdj)",
                "Interceptions per 90", "Interceptions (PAdj)", "Defensive duels won %",
                "Aerial duels won %", "Defensive duels won per 90", "Aerial duels won per 90",
                "Possession +/-", "Possessions won - lost per 90", "Progressive actions per 90",
                "Progressive action rate", "Key passes per 90", "Progressive carries per 90",
                "Ball-carrying frequency", "Through passes per 90", "Passes to final third per 90",
                "Passes completed per 90", "Forward passes completed per 90", "Long passes completed per 90",
                "Progressive passes completed per 90", "Pass completion %", "Forward pass completion %",
                "Progressive pass accuracy %"
            ]
        elif selected_position == "Full-back":
            metric_options = [
                "Possessions won per 90", "Sliding tackles per 90", "Sliding tackles (PAdj)",
                "Interceptions per 90", "Interceptions (PAdj)", "Defensive duels won %",
                "Aerial duels won %", "Defensive duels won per 90", "Aerial duels won per 90",
                "xG per 90", "xG per 100 touches", "Duels won %", "Duels won per 90",
                "Possession +/-", "Possessions won - lost per 90", "Progressive actions per 90",
                "Touches per 90", "Progressive action rate", "xG+xA per 90", "npxG+xA per 90",
                "xA per 90", "xA per 100 passes", "Shot assists per 90", "Key passes per 90",
                "Deep completions per 90", "Chance creation ratio", "Crosses per 90",
                "Accurate crosses per 90", "Offensive duels won per 90", "Offensive duels won %",
                "Successful dribbles per 90", "Dribble success rate %", "Dribbles per 100 touches",
                "Progressive carries per 90", "Ball-carrying frequency", "Pass completion %",
                "Forward pass completion %", "Pass completion (to final third) %",
                "Pass completion (to penalty box) %", "Progressive pass accuracy %",
                "Progressive passes (PAdj)", "Passes to penalty box per 90", "Passes per 90",
                "Forward passes per 90", "Passes to final third per 90",
                "Progressive passes per 90", "Passes completed per 90", "Forward passes completed per 90",
                "Accurate passes to final third per 90",
                "Through passes completed per 90", "Progressive passes completed per 90"
            ]
        elif selected_position == "Midfielder":
            metric_options = [
                "Possessions won per 90", "Sliding tackles per 90", "Sliding tackles (PAdj)",
                "Interceptions per 90", "Interceptions (PAdj)", "Defensive duels won %",
                "Aerial duels won %", "Defensive duels won per 90", "Aerial duels won per 90",
                "Duels won %", "Duels won per 90", "Possession +/-", "Possessions won - lost per 90",
                "Progressive actions per 90", "Touches per 90", "Progressive action rate",
                "xG+xA per 90", "npxG+xA per 90", "xA per 90", "xA per 100 passes",
                "Shot assists per 90", "Key passes per 90", "Deep completions per 90",
                "Chance creation ratio", "Crosses per 90", "Accurate crosses per 90",
                "Assists - xA per 90", "Pre-assists per 90", "Fouls suffered per 90",
                "Successful dribbles per 90", "Dribble success rate %", "Progressive carries per 90",
                "Ball-carrying frequency", "xG per 90", "npxG per 90", "Goals per 100 touches",
                "NPG+A per 90", "Pass completion %", "Forward pass completion %",
                "Pass completion (to final third) %", "Pass completion (to penalty box) %",
                "Progressive pass accuracy %", "Forward pass ratio", "Backward pass ratio",
                "Progressive passes (PAdj)", "Passes to penalty box per 90", "Passes per 90",
                "Forward passes per 90", "Long passes per 90", "Passes to final third per 90",
                "Through passes per 90", "Progressive passes per 90", "Passes completed per 90",
                "Forward passes completed per 90", "Long passes completed per 90",
                "Accurate passes to final third per 90", "Through passes completed per 90",
                "Progressive passes completed per 90"
            ]
        elif selected_position == "Winger":
            metric_options = [
                "Progressive actions per 90", "Touches per 90", "Progressive action rate",
                "xG+xA per 90", "npxG+xA per 90", "xA per 90", "xA per 100 passes",
                "Shot assists per 90", "Key passes per 90", "Deep completions per 90",
                "Chance creation ratio", "Crosses per 90", "Accurate crosses per 90",
                "Assists - xA per 90", "Pre-assists per 90", "Fouls suffered per 90",
                "Offensive duels won per 90", "Offensive duels won %", "Successful dribbles per 90",
                "Dribble success rate %", "Dribbles per 100 touches", "Progressive carries per 90",
                "Ball-carrying frequency", "Passes to penalty box per 90", "Through passes per 90",
                "Progressive passes per 90", "Through passes completed per 90", "Progressive pass accuracy %",
                "Shots per 90", "Shots on target per 90", "xG per 90", "npxG per 90",
                "xG per 100 touches", "Goals per 100 touches",
                "NPG+A per 90", "Goals - xG per 90", "Shot frequency", "Touches in box per 90"
            ]
        elif selected_position == "Striker":
            metric_options = [
                "Aerial duels won %", "Aerial duels won per 90", "Duels won %",
                "xG+xA per 90", "npxG+xA per 90", "xA per 90", "xA per 100 passes",
                "Successful dribbles per 90", "Dribbles per 100 touches", "Progressive carries per 90",
                "Ball-carrying frequency", "Pass completion %", "Pass completion (to penalty box) %",
                "Shots per 90", "Shots on target per 90", "xG per 90", "npxG per 90",
                "xG per 100 touches", "xG/Shot", "npxG/Shot", "Goals per 100 touches",
                "NPG+A per 90", "Goal conversion %",
                "Goals - xG per 90", "Shot frequency", "Touches in box per 90"
            ]
        elif selected_position == "All positions":
            metric_options = [
                "Possessions won per 90","Sliding tackles per 90","Sliding tackles (PAdj)","Interceptions per 90","Interceptions (PAdj)","Defensive duels won per 90","Aerial duels won per 90","Duels won per 90","Possession +/-","Possessions won - lost per 90","Progressive actions per 90","Touches per 90","Progressive action rate","xG+xA per 90","npxG+xA per 90","Assists per 90","xA per 90","xA per 100 passes","Shot assists per 90","Key passes per 90","Deep completions per 90","Chance creation ratio","Crosses per 90","Accurate crosses per 90","Assists - xA per 90","Pre-assists per 90","Fouls suffered per 90","Offensive duels won per 90","Offensive duels won %","Successful dribbles per 90","Dribble success rate %","Dribbles per 100 touches","Progressive carries per 90","Ball-carrying frequency","Passes per 90","Forward passes per 90","Passes to penalty box per 90","Through passes per 90","Progressive passes per 90","Passes completed per 90","Forward passes completed per 90","Accurate passes to final third per 90","Through passes completed per 90","Progressive passes completed per 90","Pass completion %","Forward pass completion %","Progressive passes (PAdj)","Shots per 90","Shots on target per 90","xG per 90","npxG per 90","xG per 100 touches","Goals per 100 touches","NPG+A per 90","Goals - xG per 90","Shot frequency","Touches in box per 90"
            ]
            
        selected_metric = random.choice(metric_options)

        league_options = [
    "Top 7 Leagues",
    "Top 5 Leagues",
    "All Leagues",
    "Outside Top 7",
    "South America",
    "Premier League",
    "La Liga"
]

        weights = [0.28, 0.45, 0.16, 0, 0, 0.07, 0.04] # Adjust league weights
        assert len(weights) == len(league_options), "Weights length must match the league options length"
        selected_league = random.choices(league_options, weights=weights, k=1)[0]

        if selected_league in ["Top 7 Leagues", "Top 5 Leagues", "All Leagues", "Outside Top 7"]:
            if selected_league == "Top 5 Leagues" and selected_position == "Striker":
                age_options = ["Age", "U23"]
            elif selected_league in ["All Leagues", "Outside Top 7"]:
                if selected_position == "All positions":
                    age_options = ["Age", "U18", "U19", "U20", "U21", "U23"]
                elif selected_position != "Goalkeeper":
                    age_options = ["Age", "U19", "U20", "U21", "U23"]
                else:
                    age_options = ["Age", "U21", "U24"]
            else: 
                if selected_position == "All positions":
                    age_options = ["Age", "U19", "U20", "U21", "U23"]
                elif selected_position != "Goalkeeper":
                    age_options = ["Age", "U21", "U23"]
                else:
                    age_options = ["Age", "U24"]
        else:
            age_options = ["Age"]

        selected_age = random.choice(age_options)

        # Select metric using custom selector
        self.driver.execute_script(f"""
            var metricTrigger = document.getElementById('metric-select-trigger');
            if (metricTrigger) {{
                metricTrigger.click();
            }}
            setTimeout(function() {{
                var options = document.querySelectorAll('#metric-select-options .custom-select-option');
                for (var i = 0; i < options.length; i++) {{
                    if (options[i].textContent.trim() === '{selected_metric}') {{
                        options[i].click();
                        break;
                    }}
                }}
            }}, 100);
        """)

        self.driver.execute_script(f"""
            var positionTrigger = document.getElementById('position-select-trigger');
            if (positionTrigger) {{
                positionTrigger.click();
            }}
            setTimeout(function() {{
                var options = document.querySelectorAll('#position-select-options .custom-select-option');
                for (var i = 0; i < options.length; i++) {{
                    if (options[i].textContent.trim() === '{selected_position}') {{
                        options[i].click();
                        break;
                    }}
                }}
            }}, 100);
        """)

        # Select league using custom selector
        self.driver.execute_script(f"""
            var leagueTrigger = document.getElementById('league-select-trigger');
            if (leagueTrigger) {{
                leagueTrigger.click();
            }}
            setTimeout(function() {{
                var options = document.querySelectorAll('#league-select-options .custom-select-option');
                for (var i = 0; i < options.length; i++) {{
                    if (options[i].textContent.trim() === '{selected_league}') {{
                        options[i].click();
                        break;
                    }}
                }}
            }}, 100);
        """)

        # Select age using custom selector
        if selected_age != "Age":
            self.driver.execute_script(f"""
                var ageTrigger = document.getElementById('age-select-trigger');
                if (ageTrigger) {{
                    ageTrigger.click();
                }}
                setTimeout(function() {{
                    var options = document.querySelectorAll('#age-select-options .custom-select-option');
                    for (var i = 0; i < options.length; i++) {{
                        if (options[i].textContent.trim() === '{selected_age}') {{
                            options[i].click();
                            break;
                        }}
                    }}
                }}, 100);
            """)

        # Check if we need to handle the toggle sort checkbox
        if selected_metric in ["Goals - xG per 90", "Assists - xA per 90"]:
            # Randomly decide whether to click the toggle
            if random.choice([True, False]):
                try:
                    toggle_sort = WebDriverWait(self.driver, 10).until(
                        EC.presence_of_element_located((By.ID, "toggleSort"))
                    )
                    self.driver.execute_script("arguments[0].click();", toggle_sort)
                except Exception as e:
                    print(f"Could not click toggle sort: {e}")

        # Wait for the toggle metrics button to be visible and scroll into view
        toggle_metrics_btn = WebDriverWait(self.driver, 10).until(
            EC.visibility_of_element_located((By.ID, "toggleMetrics"))
        )
        self.driver.execute_script("arguments[0].scrollIntoView(true);", toggle_metrics_btn)

        # Use JavaScript to click the button
        try:
            self.driver.execute_script("arguments[0].click();", toggle_metrics_btn)
            time.sleep(0.5)  # Wait for the toggle state to update visually
        except Exception as e:
            raise e
        
        self.driver.execute_script("""
    document.documentElement.style.overflow = 'hidden';  // Hide horizontal and vertical scroll bars
    document.body.style.overflow = 'hidden';  // Hide scroll bars on body
    var resultContainer = document.querySelector('.result-container');
    if (resultContainer) {
        resultContainer.style.overflow = 'hidden';  // Hide scroll bars on result-container div
    }
""")

        # Inject a dummy div at the top left and move mouse to it to avoid hover effect
        self.driver.execute_script("""
            if (!document.getElementById('dummy-mouse-target')) {
                var d = document.createElement('div');
                d.id = 'dummy-mouse-target';
                d.style.position = 'fixed';
                d.style.left = '0px';
                d.style.top = '0px';
                d.style.width = '1px';
                d.style.height = '1px';
                d.style.zIndex = '99999';
                d.style.background = 'transparent';
                document.body.appendChild(d);
            }
        """)
        dummy = self.driver.find_element(By.ID, "dummy-mouse-target")
        ActionChains(self.driver).move_to_element(dummy).perform()

        # Hide the dark-mode-toggle before taking the screenshot
        self.driver.execute_script("""
            var dmt = document.querySelector('.dark-mode-toggle');
            if (dmt) dmt.style.display = 'none';
        """)

        # Save screenshot
        self.driver.save_screenshot('screenshot.png')
        specific_text = self.capture_first_five_lines()

        # Crop 5px from top, left, and right
        img = Image.open('screenshot.png')
        width, height = img.size
        cropped = img.crop((11, 0, width - 11, height - 5))
        cropped.save('screenshot.png')

        # Upload the screenshot to Twitter
        upload_url = "https://upload.twitter.com/1.1/media/upload.json"
        auth = OAuth1(API_KEY, API_KEY_SECRET, ACCESS_TOKEN, ACCESS_TOKEN_SECRET)
        
        with open('screenshot.png', 'rb') as image_file:
            files = {'media': image_file}
            response = requests.post(upload_url, files=files, auth=auth)
        
        if response.status_code != 200:
            print("Failed to upload media:", response.status_code, response.text)
            return
        
        media_id = response.json()['media_id_string']

        # Add alt text to the uploaded image
        alt_text = "This is an automated tweet 🤖\n\nPosition, league, age and metrics were chosen randomly in the 2025/26 dataset.\n\nPlayer age and team refer to their age and team during the season.\n\nPositions are determined via the player's average heat map.\n\nSubscribe for more leagues and tools!"  # Add your alt text here
        metadata_url = "https://upload.twitter.com/1.1/media/metadata/create.json"
        metadata_payload = {
    "media_id": media_id,
    "alt_text": {"text": alt_text}
}
        metadata_response = requests.post(metadata_url, json=metadata_payload, auth=auth)

        if metadata_response.status_code != 200:
            print("Failed to create metadata:", metadata_response.status_code, metadata_response.text)
            return
        
        selected_metric = selected_metric.replace(" per 90", "")
        selected_position = selected_position.replace("er", "ers")
        selected_position = selected_position.replace("ack", "acks")
        selected_position = selected_position.replace("All positions", "Players")
        selected_age = selected_age.replace("Age", "")
        tweet_text = f"{selected_league} {selected_age} {selected_position} : {selected_metric}\n\n{specific_text}\n\n📊 datamb.football"
        tweet_text = tweet_text.replace("  ", " ")
        tweet_text = tweet_text.replace(" Wanderers", "")
        tweet_text = tweet_text.replace("Borussia ", "")
        tweet_text = tweet_text.replace("Deportivo ", "")
        tweet_text = tweet_text.replace("Manchester", "Man")
        tweet_text = tweet_text.replace(" Hotspur", "")
        tweet_text = tweet_text.replace("West Ham United", "West Ham")
        tweet_text = tweet_text.replace("Celta de", "Celta")
        tweet_text = tweet_text.replace("Olympique Lyonnais", "Lyon")
        tweet_text = tweet_text.replace("Olympique Marseille", "Marseille")
        tweet_text = tweet_text.replace("Fortuna ", "")
        tweet_text = tweet_text.replace("Eintracht ", "")
        tweet_text = tweet_text.replace("Newcastle United", "Newcastle")
        tweet_text = tweet_text.replace("Wingers", "Wingers & Att Mid")
        tweet_text = tweet_text.replace("Goals - xG", "Goals minus xG")
        tweet_text = tweet_text.replace("All Leagues", "🌍 All Leagues")
        tweet_text = tweet_text.replace("Outside Top 7", "🌍 Outside Top 7")
        tweet_text = tweet_text.replace("South America", "🌎 South America")
        tweet_text = tweet_text.replace("Top 7 Leagues", "🇪🇺 Top 7 League")
        tweet_text = tweet_text.replace("Top 5 Leagues", "🇪🇺 Top 5 League")
        tweet_text = tweet_text.replace("Premier League", "🏴󠁧󠁢󠁥󠁮󠁧󠁿 Premier League")
        tweet_text = tweet_text.replace("La Liga", "🇪🇸 La Liga")
        tweet_text = tweet_text.replace("Bundesliga", "🇩🇪 Bundesliga")
        tweet_text = tweet_text.replace("Serie A", "🇮🇹 Serie A")
        
        time.sleep(170*60)

        # Create the tweet with the media attached
        tweet_url = "https://api.twitter.com/2/tweets"
        payload = {
            "text": tweet_text,
            "media": {
                "media_ids": [media_id]
            }
        }
        
        response = requests.post(tweet_url, json=payload, auth=auth)
        
        if response.status_code == 201:
            print("Tweet successfully sent!")
            first_tweet_id = response.json()['data']['id']
            
            # Create the follow-up tweet
            follow_up_text = "Compare Top 7 League players, or subscribe for more leagues, metrics, and tools ⤵️ datamb.football"
            follow_up_payload = {
                "text": follow_up_text,
                "reply": {
                    "in_reply_to_tweet_id": first_tweet_id
                }
            }

            
            # Send the follow-up tweet
            follow_up_response = requests.post(tweet_url, json=follow_up_payload, auth=auth)
            
            if follow_up_response.status_code == 201:
                print("Follow-up tweet successfully sent!")
            else:
                print("Failed to send follow-up tweet:", follow_up_response.status_code, follow_up_response.text)

        else:
            print("Failed to send tweet:", response.status_code, response.text)

        


if __name__ == "__main__":
    pytest.main()
