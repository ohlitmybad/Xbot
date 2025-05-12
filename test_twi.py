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
from pathlib import Path


API_KEY = '9VG6eYAmiPw8mvRVUuN23BSee'
API_KEY_SECRET = 'O2r4p5hyCZ7ZYjsVK73RAnReH7GnZQKahswukRbOOSfUoLevGp'
ACCESS_TOKEN = '1389871650125094913-tHVJvdSksSHn89CCTQhgxfNpF1QENW'
ACCESS_TOKEN_SECRET = 'LWrKGzeokBFq7IxbA18gFsyE4bAGgeJYc6gTNDTIUJoV2'

class TestUntitled:
    def setup_method(self, method):
        chrome_options = Options()
        chrome_options.add_argument("--headless")
        chrome_options.add_argument("--disable-gpu")        
        # Set the download directory to the current directory
        self.screenshot_dir = os.path.dirname(os.path.abspath(__file__))
        
        # Set Chrome preferences to download files to the current directory
        prefs = {
            "download.default_directory": self.screenshot_dir,
            "download.prompt_for_download": False,
            "download.directory_upgrade": True,
            "safebrowsing.enabled": True
        }
        chrome_options.add_experimental_option("prefs", prefs)
        
        self.driver = webdriver.Chrome(options=chrome_options)

    def teardown_method(self):
        self.driver.quit()
    
    # Helper function to wait for download to complete
    def wait_for_download(self, timeout=30):
        """Wait for download to finish"""
        seconds = 0
        dl_wait = True
        while dl_wait and seconds < timeout:
            time.sleep(1)
            dl_wait = False
            files = os.listdir(self.screenshot_dir)
            for fname in files:
                if fname.endswith('.crdownload'):
                    dl_wait = True
            seconds += 1
        return seconds
    
    def run_test_iteration(self):
        urls_and_metrics = {
            "https://datamb.football/proplotgk24/": [ 
                "Prevented goals per 90", "Save percentage %", "Pass completion %", 
                 "Passes per 90", "Long passes per 90", "Short passes per 90", "Saves per 90"
            ],
            "https://datamb.football/proplotcb24/": [
                "Passes completed per 90", "Long passes completed per 90", "Through passes completed per 90", 
                "Progressive passes (PAdj)", "Forward pass ratio", "Ball-carrying frequency", 
                "Possessions won - lost per 90", "Possession +/-", "Progressive actions per 90", 
                "Progressive action rate", "Sliding tackles (PAdj)", "Interceptions (PAdj)", 
                "Defensive duels won %", "Aerial duels won %", "Defensive duels won per 90",
                "Possessions won per 90", "Defensive duels per 90", "Aerial duels won per 90",
        "Aerial duels per 90", "Sliding tackles per 90", 
        "Interceptions per 90",  
        "Progressive carries per 90", "Passes per 90", "Forward passes per 90", 
        "Long passes per 90", "Passes to final third per 90", 
        "Progressive passes per 90", "Pass completion %", "Forward pass completion %", 
        "Progressive pass accuracy %"
            ],
            "https://datamb.football/proplotfb24/": [
                "xA per 100 passes", "Chance creation ratio", "Goals + Assists per 90", "xG+xA per 90", 
                "Pre-assists per 90", "Passes completed per 90", "Progressive passes (PAdj)", 
                "Forward pass ratio", "Dribbles per 100 touches", "Successful dribbles per 90", "Ball-carrying frequency", 
                "Duels won %", "Duels won per 90", "Possessions won - lost per 90", "Possession +/-", 
                "Progressive actions per 90", "Progressive action rate", "Defensive duels won per 90",                
                "Possessions won per 90","Defensive duels per 90","Aerial duels per 90",
                "Sliding tackles per 90","Interceptions per 90",
                "xG per 90", "Goals per 90", "Assists per 90", "Crosses per 90",
                "Offensive duels per 90","Progressive carries per 90","Accelerations per 90",
                "Passes per 90","Forward passes per 90","Long passes per 90",
                "xA per 90","Shot assists per 90","Key passes per 90",
                "Passes to final third per 90","Passes to penalty box per 90","Through passes per 90",
                "Deep completions per 90","Progressive passes per 90","Defensive duels won %",
                "Aerial duels won %","Dribble success rate %","Offensive duels won %",
                "Pass completion %","Forward pass completion %","Progressive pass accuracy %"

            ],
            "https://datamb.football/proplotcm24/": [
                "xG per 100 touches", "Goals per 100 touches", "npxG per 90", "xA per 100 passes", 
                "Chance creation ratio", "Goals + Assists per 90", "xG+xA per 90", "Assists - xA per 90", 
                "Pre-assists per 90", "Passes completed per 90", "Long passes completed per 90", 
                "Through passes completed per 90", "Progressive passes (PAdj)", "Forward pass ratio", 
                "Successful dribbles per 90", "Dribbles per 100 touches", "Ball-carrying frequency", 
                "Duels won %", "Duels won per 90", "Possessions won - lost per 90", "Possession +/-", 
                "Progressive actions per 90", "Progressive action rate",
                "Possessions won per 90","Defensive duels per 90","Aerial duels per 90",
                "Sliding tackles per 90","Sliding tackles (PAdj)","Interceptions per 90",
                "Interceptions (PAdj)","Successful attacking actions per 90","xG per 90",
                "Goals per 90", "Assists per 90", "Crosses per 90","Progressive carries per 90",
                "Accelerations per 90","Fouls suffered per 90","Passes per 90","Forward passes per 90",
                "Long passes per 90","xA per 90","Shot assists per 90","Key passes per 90",
                "Passes to final third per 90","Passes to penalty box per 90","Through passes per 90",
                "Deep completions per 90","Progressive passes per 90","Defensive duels won %",
                "Pass completion %","Forward pass completion %",
                "Progressive pass accuracy %","Dribble success rate %"
            ],
            "https://datamb.football/proplotfw24/": [
                "xG/Shot", "Goals - xG per 90", "xG per 100 touches", "Shot frequency", 
                "Goals per 100 touches", "npxG per 90", "npxG/Shot", "xA per 100 passes", 
                "Chance creation ratio", "Goals + Assists per 90", "xG+xA per 90", "Assists - xA per 90", 
             "Successful dribbles per 90", "Dribbles per 100 touches", 
                "Ball-carrying frequency", "Duels won %", "Duels won per 90", "Progressive actions per 90", 
                "Progressive action rate",
             "Shots on target %","Goal conversion %","Cross accuracy %","Dribble success rate %",
             "Offensive duels won %","Successful attacking actions per 90","xG per 90",
             "Goals per 90", "Assists per 90", "Shots per 90","Crosses per 90",
             "Offensive duels per 90","Touches in box per 90","Progressive carries per 90",
             "Accelerations per 90","Fouls suffered per 90","xA per 90",
             "Shot assists per 90","Key passes per 90","Passes to final third per 90",
             "Passes to penalty box per 90","Deep completions per 90","Progressive passes per 90"
            ],
            "https://datamb.football/proplotst24/": [
                "xG/Shot", "Goals - xG per 90", "xG per 100 touches", "Shot frequency", 
                "Goals per 100 touches", "npxG per 90", "npxG/Shot",  
                "Chance creation ratio", "Goals + Assists per 90", "xG+xA per 90", "Dribbles per 100 touches", 
                "Successful dribbles per 90",
                "Duels won %",
                 "Aerial duels per 90","xG per 90","Shots per 90","Touches in box per 90",
                 "Goals per 90", "Assists per 90","xA per 90","Aerial duels won %",
                 "Shots on target %","Goal conversion %","Offensive duels won %","Pass completion %" 
            ],
            "https://datamb.football/proteamplot/": [
                "Goals per 90", "xG per 90", "Shots on target per 90", "Shots on target %", 
                "Passes completed", "Pass accuracy %", "Possession %", "Positional attacks per 90", 
                "Counter attacks per 90", "Touches in the box per 90", "Goals conceded per 90", 
                "SoT against per 90", "Defensive duels per 90", "Defensive duel %", 
                "Aerial duels per 90", "Aerial duels %", "Passes per possession", "PPDA"
            ]            
        }

        # Define groups of similar metrics that shouldn't be plotted together
        similar_metrics_groups = [
            ["xG/Shot", "npxG/Shot"],
            ["Shots on target %", "Goal conversion %"],
            ["xG per 90", "npxG per 90"],
            ["xG per 90", "xG per 100 touches"],
            ["npxG per 90", "xG per 100 touches"],
            ["Pass completion %","Forward pass completion %", "Progressive pass accuracy %"],
            ["Offensive duels won %", "Successful dribbles %"],
            ["xA per 90", "xA per 100 passes"],            
            ["Passes per 90", "Forward passes per 90"],
            ["Passes per 90", "Passes completed per 90"],
            ["Forward passes per 90", "Forward pass ratio"],
            ["Long passes per 90", "Long passes completed per 90"],
            ["Through passes per 90", "Through passes completed per 90"],
            ["Progressive passes per 90", "Progressive passes (PAdj)"],
            ["Progressive carries per 90", "Accelerations per 90", "Successful dribbles per 90", "Offensive duels per 90", "Sucessful attacking actions per 90"],
            ["Passes to final third per 90", "Passes to penalty box per 90", "Progressive passes per 90"],
            ["Progressive actions per 90", "Progressive passes per 90", "Progressive carries per 90"],
            ["Possessions won - lost per 90", "Possessions won per 90"],
            ["Possessions won - lost per 90", "Possession +/-"],
            ["Duels won %", "Offensive duels won %"],
            ["Duels won %", "Defensive duels won %"],
            ["Duels won %", "Aerial duels won %"],
            ["Ball-carrying frequency", "Progressive carries per 90"],
            ["Progressive actions", "Progressive action rate"],
            ["Progressive actions per 90", "Progressive action rate"],
            ["Dribbles per 100 touches", "Successful dribbles per 90"],
            ["Defensive duels per 90", "Defensive duels won per 90"],
            ["Aerial duels per 90", "Aerial duels won per 90"],
            ["Sliding tackles per 90", "Sliding tackles (PAdj)"],
            ["Interceptions per 90", "Interceptions (PAdj)"],
            ["SoT against per 90", "Shots on target %"],
            ["Passes per possession", "Passes completed"]
        ]
        
        # Function to filter out similar metrics
        def filter_similar_metrics(selected_metric, available_metrics, similar_groups):
            filtered_metrics = available_metrics.copy()
            
            # Find which group the selected metric belongs to
            for group in similar_groups:
                if selected_metric in group:
                    # Remove all metrics from the same group
                    for metric in group:
                        if metric in filtered_metrics and metric != selected_metric:
                            filtered_metrics.remove(metric)
            
            return filtered_metrics

        url_to_position = {
            "https://datamb.football/proplotgk24/": "Goalkeepers",
            "https://datamb.football/proplotcb24/": "Centre-backs",
            "https://datamb.football/proplotfb24/": "Full-backs",
            "https://datamb.football/proplotcm24/": "Midfielders",
            "https://datamb.football/proplotfw24/": "Wingers",
            "https://datamb.football/proplotst24/": "Strikers",
            "https://datamb.football/proteamplot/": "Teams" 
        }

        urls = list(urls_and_metrics.keys())
        weights2 = [0.06, 0.13, 0.06, 0.28, 0.22, 0.14, 0.11]  
        
        selected_url = random.choices(urls, weights=weights2, k=1)[0]                
        self.driver.get(selected_url)
        time.sleep(1)
        
        WebDriverWait(self.driver, 60).until(
            EC.presence_of_element_located((By.XPATH, "//input[@name='eml']"))
        ).send_keys("tombolivier@gmail.com")
        
        self.driver.find_element(By.NAME, "pwd").send_keys("password1")
        self.driver.find_element(By.CSS_SELECTOR, ".SFfrm button").click()
        self.driver.maximize_window()
        
        WebDriverWait(self.driver, 10).until(EC.element_to_be_clickable((By.ID, "select-all-button"))).click()
        
        # Get available metrics for the selected URL
        metric_options = urls_and_metrics[selected_url]
        
        # Select X metric randomly
        selected_metric_x = random.choice(metric_options)
        
        # Filter Y metric options to exclude similar metrics to X
        filtered_y_options = filter_similar_metrics(selected_metric_x, metric_options.copy(), similar_metrics_groups)
        
        # Remove the X metric from Y options
        if selected_metric_x in filtered_y_options:
            filtered_y_options.remove(selected_metric_x)
        
        # If we have filtered out all options, revert to using all metrics except the X metric
        if not filtered_y_options:
            filtered_y_options = [m for m in metric_options if m != selected_metric_x]
        
        # Select Y metric randomly from filtered options
        selected_metric_y = random.choice(filtered_y_options)

        if selected_url == "https://datamb.football/proteamplot/":
            league_options = ["Top 7 Leagues", "Top 5 Leagues", "Premier League", 
                             "La Liga", "Bundesliga", "Serie A", "Ligue 1", 
                             "Liga Portugal", "Eredivisie"]
            weights = [0.22, 0.42, 0.22, 0.06, 0.04, 0.04, 0, 0, 0]
        else:
            league_options = ["Top 7 Leagues", "Top 5 Leagues", "Premier League", 
                             "La Liga", "Bundesliga", "Serie A", "Ligue 1", 
                             "Liga Portugal", "Eredivisie"]
            weights = [0.32, 0.46, 0.14, 0.04, 0.02, 0.02, 0, 0, 0]

        assert len(weights) == len(league_options), "Weights length must match the league options length"
        selected_league = random.choices(league_options, weights=weights, k=1)[0]
        selected_position = url_to_position.get(selected_url, None)
        
        selected_age = "Age"  # Default
        if selected_url != "https://datamb.football/proteamplot/":
            if selected_league in ["Top 7 Leagues", "Top 5 Leagues"]:
                if selected_position != "Goalkeepers":
                    age_options = ["Age", "U19", "U20", "U21", "U22", "U23", "U24"]
                    selected_age = random.choice(age_options)
                else:
                    age_options = ["Age", "U24"]
                    selected_age = random.choice(age_options)

        self.driver.execute_script(f"""
            var selectX = document.getElementById('select-x');
            
            // Find the option with matching text and select it
            for (var i = 0; i < selectX.options.length; i++) {{
                if (selectX.options[i].text === '{selected_metric_x}') {{
                    selectX.selectedIndex = i;
                var event = new Event('change', {{ bubbles: true }});
                    selectX.dispatchEvent(event);
                var xTrigger = document.getElementById('x-metric-trigger');
                    if (xTrigger) {{
                        var span = xTrigger.querySelector('span');
                        if (span) span.textContent = '{selected_metric_x}';
                    }}
                    break;
                }}
            }}
        """)
        
        self.driver.execute_script(f"""
            var selectY = document.getElementById('select-y');
            for (var i = 0; i < selectY.options.length; i++) {{
                if (selectY.options[i].text === '{selected_metric_y}') {{
                    selectY.selectedIndex = i;
             var event = new Event('change', {{ bubbles: true }});
                    selectY.dispatchEvent(event);
             var yTrigger = document.getElementById('y-metric-trigger');
                    if (yTrigger) {{
                        var span = yTrigger.querySelector('span');
                        if (span) span.textContent = '{selected_metric_y}';
                    }}
                    break;
                }}
            }}
        """)
        
        self.driver.execute_script(f"""
            var selectLeague = document.getElementById('select-league');
            var leagueValue = '';
                
                if ('{selected_league}'.includes('Top 5')) leagueValue = 'Top 5 Leagues';
                else if ('{selected_league}'.includes('Top 7')) leagueValue = 'Top 7 Leagues';
                else if ('{selected_league}'.includes('Premier')) leagueValue = 'Premier League';
                else if ('{selected_league}'.includes('La Liga')) leagueValue = 'La Liga';
                else if ('{selected_league}'.includes('Bundesliga')) leagueValue = 'Bundesliga';
                else if ('{selected_league}'.includes('Serie A')) leagueValue = 'Serie A';
                else if ('{selected_league}'.includes('Ligue 1')) leagueValue = 'Ligue 1';
                
                if (leagueValue) {{
                    for (var i = 0; i < selectLeague.options.length; i++) {{
                        if (selectLeague.options[i].value === leagueValue) {{
                            selectLeague.selectedIndex = i;
                            var event = new Event('change', {{ bubbles: true }});
                            selectLeague.dispatchEvent(event);
                            break;
                        }}
                    }}
                }}
        """)
        
        if selected_url != "https://datamb.football/proteamplot/" and selected_age != "Age":
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
            
             
        WebDriverWait(self.driver, 10).until(
                EC.element_to_be_clickable((By.ID, "toggle-median-lines"))
            ).click()
       
        WebDriverWait(self.driver, 10).until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, ".toggle-icon"))
        ).click()
            
        time.sleep(2)
        
     
        dots = self.driver.find_elements(By.CSS_SELECTOR, ".team-label, .dot")
            
        if len(dots) < 15:
            return False  # Signal that we need to retry
        
        screenshot_button = WebDriverWait(self.driver, 10).until(
            EC.element_to_be_clickable((By.XPATH, "//button[@onclick='takeScreenshot()']"))
        )
        screenshot_button.click()
        
        # Wait for the download to complete
        self.wait_for_download(timeout=30)
        
    
        time.sleep(2)


        # Upload the screenshot to Twitter
        upload_url = "https://upload.twitter.com/1.1/media/upload.json"
        auth = OAuth1(API_KEY, API_KEY_SECRET, ACCESS_TOKEN, ACCESS_TOKEN_SECRET)
        
        with open('DataMB Screenshot.png', 'rb') as image_file:
            files = {'media': image_file}
            response = requests.post(upload_url, files=files, auth=auth)
        
        if response.status_code != 200:
            print("Failed to upload media:", response.status_code, response.text)
            return
        
        media_id = response.json()['media_id_string']

        # Add alt text to the uploaded image
        alt_text = "This is an automated tweet 🤖\n\nLeague and metrics were chosen randomly in the 2024/25 dataset.\n\nCompare and plot more team metrics for free on datamb.football"  # Add your alt text here
        if selected_url != "https://datamb.football/proteamplot/":
            alt_text = "This is an automated tweet 🤖\n\nPosition, league, age and metrics were chosen randomly in the 2024/25 dataset.\n\nPositions are determined via the player's average heat map.\n\nSubscribe to DataMB Pro for more leagues and tools!"  # Add your alt text here
        metadata_url = "https://upload.twitter.com/1.1/media/metadata/create.json"
        metadata_payload = {
    "media_id": media_id,
    "alt_text": {"text": alt_text}
}
        metadata_response = requests.post(metadata_url, json=metadata_payload, auth=auth)

        if metadata_response.status_code != 200:
            print("Failed to create metadata:", metadata_response.status_code, metadata_response.text)
            return
        
        selected_position = url_to_position[selected_url]
        selected_age = selected_age.replace("Age", "")

        


        # Create the tweet text dynamically
        if selected_url == "https://datamb.football/proteamplot/":
            tweet_text = f"{selected_league} : {selected_position}\n📈 {selected_metric_x} vs {selected_metric_y}\n\nPlot teams 👉 datamb.football"
        else:
            tweet_text = f"{selected_league} : {selected_age} {selected_position}\n📈 {selected_metric_x} vs {selected_metric_y}\n\nPlot more 👉 datamb.football"
        tweet_text = tweet_text.replace("  ", " ")
        tweet_text = tweet_text.replace("Top 7 Leagues", "🇪🇺 Top 7 Leagues")
        tweet_text = tweet_text.replace("Top 5 Leagues", "🇪🇺 Top 5 Leagues")
        tweet_text = tweet_text.replace("Premier League", "🏴󠁧󠁢󠁥󠁮󠁧󠁿 Premier League")
        tweet_text = tweet_text.replace("La Liga", "🇪🇸 La Liga")
        tweet_text = tweet_text.replace("Bundesliga", "🇩🇪 Bundesliga")
        tweet_text = tweet_text.replace("Serie A", "🇮🇹 Serie A")
        tweet_text = tweet_text.replace(" per 90", "")
        tweet_text = tweet_text.replace("Wingers", "Wingers & Att Mid")
        tweet_text = tweet_text.replace("PPDA", "Pressing")
        tweet_text = tweet_text.replace("completion %", " %")
        tweet_text = tweet_text.replace("accuracy %", " %")
        



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
            
            if selected_url == "https://datamb.football/proteamplot/":
                follow_up_text = "Compare and plot more team metrics ⤵️ datamb.football/teams"
                follow_up_payload = {
                    "text": follow_up_text,
                    "reply": {
                        "in_reply_to_tweet_id": first_tweet_id
                }
            }
            else:
                follow_up_text = "Compare Top 7 League players, or subscribe for more leagues and metrics ⤵️ datamb.football"
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

        return True  # Signal successful completion


    def test_untitled(self):
        max_retries = 2
        retry_count = 0
        
        while retry_count < max_retries:
            try:
                if self.run_test_iteration():
                    break 
                retry_count += 1
                if retry_count < max_retries:
                    time.sleep(2)  # Add a small delay between retries
                    self.driver.quit()  # Clean up the current driver
                    self.setup_method(None)  # Create a fresh driver instance
                else:
                    pytest.fail(f"Failed to find sufficient dots/labels after {max_retries} attempts")
            except Exception as e:
                retry_count += 1
                if retry_count >= max_retries:
                    raise  # Re-raise the exception if we've exhausted our retries
                time.sleep(2)
                self.driver.quit()
                self.setup_method(None)





if __name__ == "__main__":
    pytest.main()
