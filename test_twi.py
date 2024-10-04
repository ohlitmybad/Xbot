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

API_KEY = '9VG6eYAmiPw8mvRVUuN23BSee'
API_KEY_SECRET = 'O2r4p5hyCZ7ZYjsVK73RAnReH7GnZQKahswukRbOOSfUoLevGp'
ACCESS_TOKEN = '1389871650125094913-tHVJvdSksSHn89CCTQhgxfNpF1QENW'
ACCESS_TOKEN_SECRET = 'LWrKGzeokBFq7IxbA18gFsyE4bAGgeJYc6gTNDTIUJoV2'

class TestUntitled:
    def setup_method(self, method):
        chrome_options = Options()
        chrome_options.add_argument("--headless")
        chrome_options.add_argument("--disable-gpu")
        self.driver = webdriver.Chrome(options=chrome_options)

    def teardown_method(self):
        self.driver.quit()
    

    def test_untitled(self):
        urls_and_metrics = {
            "https://datamb.football/proplotgk24/": [ 
                "Prevented goals per 90", "Save rate %", "Accurate passes %", 
                 "Passes per 90", "Long passes per 90", "Short / medium passes per 90", "Successful defensive actions per 90"
            ],
            "https://datamb.football/proplotcb24/": [
                "Successful defensive actions per 90", "Defensive duels per 90", 
        "Aerial duels per 90", "Sliding tackles per 90", 
        "Interceptions per 90", "Dribbles per 90", 
        "Progressive runs per 90", "Passes per 90", "Forward passes per 90", 
        "Long passes per 90", "Passes to final third per 90", 
        "Progressive passes per 90", "Defensive duels won %", 
        "Aerial duels won %", "Accurate passes %", "Accurate forward passes %", 
        "Accurate progressive passes %"
            ],
            "https://datamb.football/proplotfb24/": [
                "Successful defensive actions per 90","Defensive duels per 90","Aerial duels per 90","Sliding tackles per 90","Interceptions per 90","Successful attacking actions per 90","xG per 90", "Goals per 90", "Assists per 90", "Crosses per 90","Dribbles per 90","Offensive duels per 90","Progressive runs per 90","Accelerations per 90","Passes per 90","Forward passes per 90","Long passes per 90","xA per 90","Shot assists per 90","Key passes per 90","Passes to final third per 90","Passes to penalty area per 90","Through passes per 90","Deep completions per 90","Progressive passes per 90","Defensive duels won %","Aerial duels won %","Successful dribbles %","Offensive duels won %","Accurate passes %","Accurate forward passes %","Accurate progressive passes %"
            ],
            "https://datamb.football/proplotcm24/": [
                "Successful defensive actions per 90","Defensive duels per 90","Aerial duels per 90","Sliding tackles per 90","PAdj Sliding tackles","Interceptions per 90","PAdj Interceptions","Successful attacking actions per 90","xG per 90", "Goals per 90", "Assists per 90", "Crosses per 90","Dribbles per 90","Offensive duels per 90","Progressive runs per 90","Accelerations per 90","Fouls suffered per 90","Passes per 90","Forward passes per 90","Long passes per 90","xA per 90","Shot assists per 90","Key passes per 90","Passes to final third per 90","Passes to penalty area per 90","Through passes per 90","Deep completions per 90","Progressive passes per 90","Defensive duels won %","Aerial duels won %","Accurate passes %","Accurate forward passes %","Accurate progressive passes %","Successful dribbles %","Offensive duels won %"
            ],
            "https://datamb.football/proplotfw24/": [
                "Shots on target %","Goal conversion %","Accurate crosses %","Successful dribbles %","Offensive duels won %","Successful attacking actions per 90","xG per 90","Goals per 90", "Assists per 90", "Shots per 90","Crosses per 90","Dribbles per 90","Offensive duels per 90","Touches in box per 90","Progressive runs per 90","Accelerations per 90","Fouls suffered per 90","Passes per 90","xA per 90","Shot assists per 90","Key passes per 90","Passes to final third per 90","Passes to penalty area per 90","Deep completions per 90","Progressive passes per 90"
            ],
            "https://datamb.football/proplotst24/": [
                "Aerial duels per 90","xG per 90","Shots per 90","Touches in box per 90","Goals per 90", "Assists per 90","xA per 90","Aerial duels won %","Shots on target %","Goal conversion %","Offensive duels won %","Accurate passes %"
            ],
            "https://datamb.football/plotteam/": [
                "Goals per 90","xG per 90","Shots on target per 90","Shots on target %","Passes completed","Pass accuracy %", "Possession %","Positional attacks per 90","Counter attacks per 90","Touches in the box per 90","Goals conceded per 90","SoT against per 90","Defensive duels per 90","Defensive duel %","Aerial duels per 90", "Aerial duels %", "Passes per possession", "PPDA"
            ]            
            
        }

        url_to_position = {
            "https://datamb.football/proplotgk24/": "Goalkeepers",
            "https://datamb.football/proplotcb24/": "Centre-backs",
            "https://datamb.football/proplotfb24/": "Full-backs",
            "https://datamb.football/proplotcm24/": "Midfielders",
            "https://datamb.football/proplotfw24/": "Wingers",
            "https://datamb.football/proplotst24/": "Strikers",
            "https://datamb.football/plotteam/": "Teams" 
        }

        urls = list(urls_and_metrics.keys())
        weights2 = [0.05, 0.17, 0.06, 0.26, 0.21, 0.11, 0.14]  # Adjust weights as needed

        # Select a URL based on weights
        selected_url = random.choices(urls, weights=weights2, k=1)[0]                
        self.driver.get(selected_url)
        time.sleep(1)
        self.driver.set_window_size(1080, 930)
        if selected_url != "https://datamb.football/plotteam/":
            WebDriverWait(self.driver, 60).until(
            EC.presence_of_element_located((By.XPATH, "//input[@name='eml']"))
            ).send_keys("tombolivier@gmail.com")
        
            self.driver.find_element(By.NAME, "pwd").send_keys("password")
            self.driver.find_element(By.CSS_SELECTOR, ".SFmfllog:nth-child(3) button").click()
            self.driver.set_window_size(1080, 960)
        circles = self.driver.find_elements(By.TAG_NAME, 'circle')
        for circle in circles:
            self.driver.execute_script("arguments[0].dispatchEvent(new MouseEvent('click', {bubbles: true, cancelable: true, view: window}));", circle)

        WebDriverWait(self.driver, 10).until(
            EC.presence_of_element_located((By.ID, "select-x"))
        )
        WebDriverWait(self.driver, 10).until(
            EC.presence_of_element_located((By.ID, "select-y"))
        )

        metric_options = urls_and_metrics[selected_url]
        selected_metric_x = random.choice(metric_options)
        metric_options.remove(selected_metric_x)
        selected_metric_y = random.choice(metric_options)

        if selected_url == "https://datamb.football/plotteam/":
            league_options = ["🇪🇺 Top 7 Leagues", "🇪🇺 Top 5 Leagues","🏴󠁧󠁢󠁥󠁮󠁧󠁿 Premier League","🇪🇸 La Liga", "🇩🇪 Bundesliga", "🇮🇹 Serie A", "🇫🇷 Ligue 1","🇵🇹 Liga Portugal", "🇳🇱 Eredivisie"]
            weights = [0.22, 0.42, 0.22, 0.06, 0.04, 0.04, 0, 0, 0]
        else:


            league_options = [
    "🇪🇺 Top 5 Leagues",
    "🇪🇺 Top 7 Leagues",
    "🏴󠁧󠁢󠁥󠁮󠁧󠁿 Premier League",
    "🇪🇸 La Liga",
    "🇩🇪 Bundesliga", 
    "🇮🇹 Serie A"        ]

            weights = [
    0.45,
    0.30,
    0.15,
    0.05, 
    0.025,
    0.025          ]

        assert len(weights) == len(league_options), "Weights length must match the league options length"
        selected_league = random.choices(league_options, weights=weights, k=1)[0]
        selected_position = url_to_position.get(selected_url, None)

        if selected_league in ["🇪🇺 Top 7 Leagues", "🇪🇺 Top 5 Leagues", "🌍 Select League", "🌍 Outside Top 7"]:
            if selected_position != "Goalkeepers":
                age_options = ["Age", "U19", "U21", "U22", "U23", "U24"]
                selected_age = random.choice(age_options)
            else:
                age_options = ["Age", "U24"]
                selected_age = random.choice(age_options)        
        else:
            selected_age = "Age"

        dropdown_x = self.driver.find_element(By.ID, "select-x")
        WebDriverWait(self.driver, 100).until(
            EC.element_to_be_clickable((By.XPATH, f"//select[@id='select-x']/option[. = '{selected_metric_x}']"))
        ).click()

        dropdown_y = self.driver.find_element(By.ID, "select-y")
        WebDriverWait(self.driver, 100).until(
            EC.element_to_be_clickable((By.XPATH, f"//select[@id='select-y']/option[. = '{selected_metric_y}']"))
        ).click()

        dropdown = self.driver.find_element(By.ID, "select-league")
        WebDriverWait(self.driver, 100).until(
            EC.element_to_be_clickable((By.XPATH, f"//option[. = '{selected_league}']"))
        ).click()

        if selected_url != "https://datamb.football/plotteam/":
            dropdown = self.driver.find_element(By.ID, "select-age")
            WebDriverWait(self.driver, 100).until(
                EC.element_to_be_clickable((By.XPATH, f"//option[. = '{selected_age}']"))
            ).click()



        WebDriverWait(self.driver, 100).until(
            EC.element_to_be_clickable((By.ID, "toggle-median-lines"))
        ).click()        

        

        self.driver.find_element(By.CSS_SELECTOR, ".toggle-icon").click()

        self.driver.execute_script("""
    document.documentElement.style.overflow = 'hidden';  // Hide horizontal and vertical scroll bars
    document.body.style.overflow = 'hidden';  // Hide scroll bars on body
""")
        time.sleep(4)
        self.driver.save_screenshot('screenshot.png')


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
        alt_text = "This is an automated tweet 🤖\n\nLeague and metrics were chosen randomly in the 2024/25 dataset.\n\nCompare and plot more team metrics for free on datamb.football"  # Add your alt text here
        if selected_url != "https://datamb.football/plotteam/":
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
        if selected_url == "https://datamb.football/plotteam/":
            tweet_text = f"{selected_league} : {selected_position}\n📈 {selected_metric_x} vs {selected_metric_y}\n\n👉 datamb.football"
        else:
            tweet_text = f"{selected_league} : {selected_age} {selected_position}\n📈 {selected_metric_x} vs {selected_metric_y}\n\n👉 datamb.football"
        tweet_text = tweet_text.replace("  ", " ")
        tweet_text = tweet_text.replace("Short / medium", "Short")
        tweet_text = tweet_text.replace("short / medium", "short")
        tweet_text = tweet_text.replace("Successful a", "A")
        tweet_text = tweet_text.replace("Successful d", "D")
        tweet_text = tweet_text.replace("🇧🇪 Belgium", "🇧🇪 Belgium Pro League")
        tweet_text = tweet_text.replace("🏴󠁧󠁢󠁳󠁣󠁴󠁿 Scotland", "🏴󠁧󠁢󠁳󠁣󠁴󠁿 Scottish Premiership")
        tweet_text = tweet_text.replace("🇦🇹 Austria", "🇦🇹 Austrian Bundesliga")
        tweet_text = tweet_text.replace("🇨🇭 Switzerland", "🇨🇭 Swiss Super League")
        tweet_text = tweet_text.replace("🇹🇷 Türkiye", "🇹🇷 Süper Lig")
        tweet_text = tweet_text.replace("🇩🇰 Denmark", "🇩🇰 Superliga")
        tweet_text = tweet_text.replace("🇸🇪 Sweden", "🇸🇪 Allsvenskan")
        tweet_text = tweet_text.replace("🇳🇴 Norway", "🇳🇴 Eliteserien")
        tweet_text = tweet_text.replace("🇭🇷 Croatia", "🇭🇷 Croatia HNL")
        tweet_text = tweet_text.replace("🇷🇸 Serbia", "🇷🇸 SuperLiga")
        tweet_text = tweet_text.replace("🇨🇿 Czech Republic", "🇨🇿 Czech First League")
        tweet_text = tweet_text.replace("🇵🇱 Poland", "🇵🇱 Ekstraklasa")
        tweet_text = tweet_text.replace("🇺🇦 Ukraine", "🇺🇦 Premier League")
        tweet_text = tweet_text.replace("🇷🇺 Russia", "🇷🇺 Premier League")
        tweet_text = tweet_text.replace("🇬🇷 Greece", "🇬🇷 Super League")
        tweet_text = tweet_text.replace("🇯🇵 Japan", "🇯🇵 J1 League")
        tweet_text = tweet_text.replace("🇰🇷 Korea", "🇰🇷 K League 1")
        tweet_text = tweet_text.replace("🇸🇦 Saudi Arabia", "🇸🇦 Saudi Pro League")
        tweet_text = tweet_text.replace("🇺🇸 United States", "🇺🇸 MLS")
        tweet_text = tweet_text.replace("🇲🇽 Mexico", "🇲🇽 Liga MX")
        tweet_text = tweet_text.replace("🇧🇷 Brazil", "🇧🇷 Série A")
        tweet_text = tweet_text.replace("🇦🇷 Argentina", "🇦🇷 Primera División")
        tweet_text = tweet_text.replace("🇺🇾 Uruguay", "🇺🇾 Primera División")
        tweet_text = tweet_text.replace("🇨🇱 Chile", "🇨🇱 Primera División")
        tweet_text = tweet_text.replace("🇨🇴 Colombia", "🇨🇴 Primera A")
        tweet_text = tweet_text.replace("🇪🇨 Ecuador", "🇪🇨 Serie A")
        tweet_text = tweet_text.replace("🇵🇾 Paraguay", "🇵🇾 Primera División")
        tweet_text = tweet_text.replace(" per 90", "")
        tweet_text = tweet_text.replace("Select League", "All Leagues")     
        tweet_text = tweet_text.replace("Wingers", "Wingers & Att Mid")
        tweet_text = tweet_text.replace("PPDA", "Pressing")
        






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
            
            if selected_url == "https://datamb.football/plotteam/":
                follow_up_text = "Compare and plot more team metrics ⤵️ datamb.football/teams"
                follow_up_payload = {
                    "text": follow_up_text,
                    "reply": {
                        "in_reply_to_tweet_id": first_tweet_id
                }
            }
            else:
                follow_up_text = "Compare Top 7 League players, or subscribe to access more leagues, metrics, and tools ⤵️ datamb.football"
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
