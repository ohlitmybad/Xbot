import base64
import os
import random
import re
import shutil
import subprocess
import sys
import tempfile
import time
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional, Tuple

import pytest
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

DATAMB_EMAIL = os.getenv("DATAMB_EMAIL")
DATAMB_PASSWORD = os.getenv("DATAMB_PASSWORD")


def _kill_stale_chrome() -> None:
    if sys.platform == "darwin":
        for proc in ("chromedriver", "Google Chrome for Testing"):
            try:
                subprocess.run(["pkill", "-9", "-f", proc], capture_output=True, timeout=5)
            except Exception:
                pass
    elif sys.platform.startswith("linux"):
        for proc in ("chromedriver", "chrome", "chromium"):
            try:
                subprocess.run(["pkill", "-9", "-f", proc], capture_output=True, timeout=5)
            except Exception:
                pass
    time.sleep(0.5)


def _make_fresh_driver(*, headless: bool = True, window_size: Tuple[int, int] = (950, 650),
                       download_dir: Optional[str] = None) -> webdriver.Chrome:
    _kill_stale_chrome()
    tmp_profile = tempfile.mkdtemp(prefix="selenium_buffer_")
    chrome_options = Options()
    chrome_options.add_argument(f"--user-data-dir={tmp_profile}")
    chrome_options.add_argument("--no-first-run")
    chrome_options.add_argument("--no-default-browser-check")
    chrome_options.add_argument("--disable-background-networking")
    chrome_options.add_argument("--disable-extensions")
    chrome_options.add_argument("--force-device-scale-factor=2")
    if headless:
        chrome_options.add_argument("--headless")
        chrome_options.add_argument("--disable-gpu")      
    if download_dir:
        prefs = {
            "download.default_directory": download_dir,
            "download.prompt_for_download": False,
            "download.directory_upgrade": True,
            "safebrowsing.enabled": True,
        }
        chrome_options.add_experimental_option("prefs", prefs)
    driver = webdriver.Chrome(options=chrome_options)
    driver.set_window_size(*window_size)
    driver._tmp_profile = tmp_profile
    return driver


def _quit_driver(driver) -> None:
    try:
        driver.quit()
    except Exception:
        pass
    tmp = getattr(driver, "_tmp_profile", None)
    if tmp and os.path.isdir(tmp):
        try:
            shutil.rmtree(tmp, ignore_errors=True)
        except Exception:
            pass


def buffer_schedule_datetime_plus_two_minutes() -> Tuple[str, str]:
    now = datetime.now() + timedelta(minutes=2)
    schedule_date = now.strftime("%Y-%m-%d")
    hours = now.hour
    minutes = now.strftime("%M")
    ampm = "PM" if hours >= 12 else "AM"
    h12 = hours % 12
    if h12 == 0:
        h12 = 12
    schedule_time = f"{h12}:{minutes} {ampm}"
    return schedule_date, schedule_time


def check_post_scheduled_success(driver, timeout: int = 90) -> Tuple[bool, Optional[str]]:
    deadline = time.time() + timeout
    while time.time() < deadline:
        try:
            result = driver.execute_script(
                """
                var body = document.body ? document.body.innerText.toLowerCase() : '';
                var keywords = ['are scheduled', 'is scheduled', 'has been sent',
                                'has been shared', 'has been published',
                                'added to queue', 'all done', 'hooray',
                                'post scheduled', 'post sent', 'post shared', 'post published',
                                'successfully scheduled', 'successfully sent',
                                'successfully shared', 'successfully published'];
                for (var i = 0; i < keywords.length; i++) {
                    if (body.indexOf(keywords[i]) !== -1) {
                        var link = document.querySelector('a[href*="/posts/"]');
                        var url = link ? link.getAttribute('href') : null;
                        return {success: true, url: url};
                    }
                }
                return null;
                """
            )
            if result and result.get("success"):
                view_post_url = result.get("url")
                if view_post_url and not view_post_url.startswith("http"):
                    view_post_url = "https://publish.buffer.com" + view_post_url
                return True, view_post_url
        except Exception:
            pass
        time.sleep(0.5)
    return False, None


def set_buffer_schedule_time_combobox_input(driver, time_input_el, time_str: str) -> None:
    cmd_key = Keys.COMMAND if sys.platform == "darwin" else Keys.CONTROL
    driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", time_input_el)
    WebDriverWait(driver, 5).until(EC.element_to_be_clickable(time_input_el))
    time_input_el.click()
    time.sleep(0.2)
    try:
        driver.execute_script(
            """
            var el = arguments[0];
            el.focus();
            var v = el.value || '';
            try { el.setSelectionRange(v.length, v.length); } catch (e) {}
            """,
            time_input_el,
        )
        prev = time_input_el.get_attribute("value") or ""
        n_erase = max(len(prev) + 12, 32)
        actions = ActionChains(driver)
        for _ in range(min(n_erase, 64)):
            actions.send_keys(Keys.BACKSPACE)
        actions.perform()
    except Exception:
        pass
    time.sleep(0.1)
    try:
        leftover = (time_input_el.get_attribute("value") or "").strip()
        if leftover:
            ac = ActionChains(driver)
            ac.click(time_input_el)
            ac.key_down(cmd_key).send_keys("a").key_up(cmd_key)
            for _ in range(48):
                ac.send_keys(Keys.BACKSPACE)
            ac.perform()
    except Exception:
        pass
    time.sleep(0.05)
    try:
        driver.execute_script(
            """
            var el = arguments[0];
            el.focus();
            try {
                var desc = Object.getOwnPropertyDescriptor(window.HTMLInputElement.prototype, 'value');
                if (desc && desc.set) { desc.set.call(el, ''); }
                else { el.value = ''; }
            } catch (e) { el.value = ''; }
            try {
                el.dispatchEvent(new InputEvent('input', { bubbles: true, inputType: 'deleteContentBackward', data: null }));
            } catch (e) {
                el.dispatchEvent(new Event('input', { bubbles: true }));
            }
            el.dispatchEvent(new Event('change', { bubbles: true }));
            """,
            time_input_el,
        )
    except Exception:
        pass
    time.sleep(0.1)
    time_input_el.click()
    time_input_el.send_keys(time_str)
    time.sleep(0.3)
    try:
        listbox_id = time_input_el.get_attribute("aria-controls") or ""
        option_clicked = False
        if listbox_id:
            try:
                options = driver.find_elements(By.CSS_SELECTOR, f"#{listbox_id} [role='option']")
                for opt in options:
                    if opt.is_displayed() and opt.text.strip() == time_str.strip():
                        opt.click()
                        option_clicked = True
                        break
            except Exception:
                pass
        if not option_clicked:
            options = driver.find_elements(By.CSS_SELECTOR, "[role='option']")
            for opt in options:
                if opt.is_displayed() and opt.text.strip() == time_str.strip():
                    opt.click()
                    option_clicked = True
                    break
        if not option_clicked:
            time_input_el.send_keys(Keys.ENTER)
    except Exception:
        try:
            time_input_el.send_keys(Keys.ENTER)
        except Exception:
            pass
    time.sleep(0.2)


_BUFFER_VERIFY_LINK_RE = re.compile(
    r"https://login\.buffer\.com/verify-login\?jwt=[^\s\"'<>]+",
    re.IGNORECASE,
)


def _buffer_gmail_token_path() -> str:
    return (
        os.environ.get("BUFFER_GMAIL_TOKEN", "").strip()
        or os.environ.get("GMAIL_TOKEN_PATH", "").strip()
    )


def _buffer_gmail_search_query() -> str:
    return os.environ.get(
        "BUFFER_GMAIL_QUERY",
        'from:hello@youraccount.buffer.com subject:"Confirm your recent login attempt"',
    ).strip()


_BUFFER_GMAIL_INSTALLED_CLIENT: Dict[str, Any] = {
    "installed": {
        "client_id": os.getenv("CLIENT_ID"),
        "project_id": "xbot-496214",
        "auth_uri": "https://accounts.google.com/o/oauth2/auth",
        "token_uri": "https://oauth2.googleapis.com/token",
        "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
        "client_secret": os.getenv("CLIENT_SECRET"),
        "redirect_uris": ["http://localhost"],
    }
}


def _gmail_service_for_buffer():
    from google.auth.transport.requests import Request
    from google.oauth2.credentials import Credentials
    from google_auth_oauthlib.flow import InstalledAppFlow
    from googleapiclient.discovery import build

    scopes = ["https://www.googleapis.com/auth/gmail.readonly"]
    token_path = _buffer_gmail_token_path()
    creds: Optional[Any] = None
    if token_path and os.path.isfile(token_path):
        creds = Credentials.from_authorized_user_file(token_path, scopes)
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
            if token_path:
                with open(token_path, "w", encoding="utf-8") as fh:
                    fh.write(creds.to_json())
        else:
            flow = InstalledAppFlow.from_client_config(_BUFFER_GMAIL_INSTALLED_CLIENT, scopes)
            creds = flow.run_local_server(port=0, access_type="offline", prompt="consent")
            if token_path:
                with open(token_path, "w", encoding="utf-8") as fh:
                    fh.write(creds.to_json())
    if not creds:
        raise RuntimeError("Buffer email verification: Gmail OAuth failed (no credentials).")
    return build("gmail", "v1", credentials=creds, cache_discovery=False)


def _gmail_collect_text_parts(payload: Dict[str, Any]) -> List[str]:
    out: List[str] = []
    mime = (payload.get("mimeType") or "").lower()
    if "parts" in payload:
        for part in payload["parts"]:
            out.extend(_gmail_collect_text_parts(part))
        return out
    body = payload.get("body") or {}
    data = body.get("data")
    if data and mime in ("text/html", "text/plain"):
        try:
            raw = base64.urlsafe_b64decode(data.encode("ascii"))
            out.append(raw.decode("utf-8", errors="replace"))
        except Exception:
            pass
    return out


def _extract_buffer_verify_link_from_bodies(bodies: List[str]) -> Optional[str]:
    joined = "\n".join(bodies)
    m = _BUFFER_VERIFY_LINK_RE.search(joined)
    if m:
        return m.group(0).rstrip(").,]}>'\"")
    m2 = re.search(
        r"https://login\.buffer\.com/verify-login\?[^\s\"'<>]+", joined, re.IGNORECASE
    )
    if m2:
        return m2.group(0).rstrip(").,]}>'\"")
    return None


def fetch_buffer_verify_link_from_gmail() -> Optional[str]:
    """Latest Buffer 'confirm login' email: extract https://login.buffer.com/verify-login?jwt=..."""
    service = _gmail_service_for_buffer()
    newer = os.environ.get("BUFFER_GMAIL_NEWER_THAN", "2h").strip() or "2h"
    base_q = _buffer_gmail_search_query()
    queries = [
        f"{base_q} newer_than:{newer}",
        f'from:buffer.com subject:"Confirm your recent login" newer_than:{newer}',
        f'from:buffer.com subject:"login attempt" newer_than:{newer}',
    ]
    messages: List[Dict[str, str]] = []
    for q in queries:
        result = service.users().messages().list(userId="me", q=q, maxResults=25).execute()
        messages = result.get("messages") or []
        if messages:
            break
    if not messages:
        return None
    best: Optional[Dict[str, Any]] = None
    best_ts = -1
    for ref in messages:
        mid = ref["id"]
        msg = service.users().messages().get(userId="me", id=mid, format="full").execute()
        ts = int(msg.get("internalDate") or 0)
        if ts >= best_ts:
            best_ts = ts
            best = msg
    if not best:
        return None
    bodies = _gmail_collect_text_parts(best["payload"])
    return _extract_buffer_verify_link_from_bodies(bodies)


def _complete_buffer_login_after_submit(driver) -> None:
    """Wait for Buffer publish, or resolve email MFA via Gmail API and open the verify link."""
    initial_wait = float(os.environ.get("BUFFER_LOGIN_PUBLISH_WAIT", "18"))
    try:
        WebDriverWait(driver, initial_wait).until(EC.url_contains("publish.buffer.com"))
        return
    except Exception:
        pass

    token_path = _buffer_gmail_token_path()
    if not token_path or not os.path.isfile(token_path):
        WebDriverWait(driver, 50).until(EC.url_contains("publish.buffer.com"))
        return

    poll_seconds = float(os.environ.get("BUFFER_GMAIL_POLL_SECONDS", "150"))
    interval = max(2, int(os.environ.get("BUFFER_GMAIL_POLL_INTERVAL", "4")))
    deadline = time.time() + poll_seconds

    while time.time() < deadline:
        try:
            if "publish.buffer.com" in driver.current_url:
                return
        except Exception:
            pass

        try:
            link = fetch_buffer_verify_link_from_gmail()
        except Exception as exc:
            raise RuntimeError(f"Buffer MFA: Gmail API failed: {exc}") from exc
        if link:
            driver.get(link)
            try:
                WebDriverWait(driver, 40).until(EC.url_contains("publish.buffer.com"))
                return
            except Exception:
                pass
        time.sleep(interval)

    WebDriverWait(driver, 20).until(EC.url_contains("publish.buffer.com"))


def _login_buffer(driver, email: str, password: str) -> None:
    driver.get("https://login.buffer.com/login")
    try:
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "body, input[name='email'], button"))
        )
    except Exception:
        pass

    # Nuke the entire CookieYes banner from the DOM
    driver.execute_script("""
        var selectors = [
            '.cky-consent-container',
            '.cky-consent-bar',
            '.cky-optout-action-area',
            '[data-cky-tag]',
            '#cky-consent',
            '.cky-overlay'
        ];
        selectors.forEach(function(sel) {
            document.querySelectorAll(sel).forEach(function(el) {
                el.parentNode && el.parentNode.removeChild(el);
            });
        });
    """)
    time.sleep(0.3)

    email_field = WebDriverWait(driver, 20).until(EC.presence_of_element_located((By.NAME, "email")))
    email_field.clear()
    driver.execute_script("arguments[0].click();", email_field)
    email_field.send_keys(email)

    password_field = WebDriverWait(driver, 15).until(EC.presence_of_element_located((By.NAME, "password")))
    password_field.clear()
    driver.execute_script("arguments[0].click();", password_field)
    password_field.send_keys(password)

    login_button = None
    for xpath in (
        "//button[@type='submit']",
        "//button[contains(text(), 'Log In')]",
        "//button[contains(text(), 'Log in')]",
    ):
        try:
            login_button = WebDriverWait(driver, 5).until(
                EC.presence_of_element_located((By.XPATH, xpath))
            )
            if login_button:
                break
        except Exception:
            continue
    if not login_button:
        raise RuntimeError("Buffer login button not found")
    
    # Nuke again in case banner re-injected itself, then JS click
    driver.execute_script("""
        document.querySelectorAll('[data-cky-tag], .cky-consent-container, .cky-optout-action-area').forEach(function(el) {
            el.parentNode && el.parentNode.removeChild(el);
        });
    """)
    driver.execute_script("arguments[0].click();", login_button)
    
    _complete_buffer_login_after_submit(driver)


def _open_composer(driver) -> None:
    if "publish.buffer.com" not in driver.current_url:
        driver.get("https://publish.buffer.com")
    try:
        WebDriverWait(driver, 15).until(
            EC.presence_of_element_located(
                (By.CSS_SELECTOR, "body, button, [data-testid*='new-post'], .new-post-button")
            )
        )
    except Exception:
        pass
    try:
        new_post = WebDriverWait(driver, 15).until(
            EC.element_to_be_clickable((By.XPATH, "//button[contains(text(), 'New Post')]"))
        )
        driver.execute_script(
            "arguments[0].scrollIntoView({behavior: 'smooth', block: 'center'});", new_post
        )
        time.sleep(0.3)
        new_post.click()
        WebDriverWait(driver, 20).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "button.publish_channelItem_BUVOd"))
        )
    except Exception:
        driver.get("https://publish.buffer.com/composer")
        WebDriverWait(driver, 15).until(
            EC.presence_of_element_located(
                (By.CSS_SELECTOR, "button.publish_channelItem_BUVOd, textarea, .composer")
            )
        )


def _select_twitter_only(driver) -> None:
    for btn in driver.find_elements(By.CSS_SELECTOR, "button.publish_channelItem_BUVOd[aria-pressed='true']"):
        try:
            btn.click()
        except Exception:
            pass
    time.sleep(0.2)
    channel_buttons = driver.find_elements(By.CSS_SELECTOR, "button.publish_channelItem_BUVOd")
    for button in channel_buttons:
        try:
            button.find_element(By.CSS_SELECTOR, "div[data-channel='twitter']")
            if button.get_attribute("aria-pressed") != "true":
                button.click()
                try:
                    WebDriverWait(driver, 2).until(
                        lambda d, b=button: b.get_attribute("aria-pressed") == "true"
                    )
                except Exception:
                    pass
            return
        except Exception:
            continue
    try:
        alt_btn = driver.find_element(By.CSS_SELECTOR, "button[aria-label='twitter channel']")
        if alt_btn.get_attribute("aria-pressed") != "true":
            alt_btn.click()
    except Exception as exc:
        raise RuntimeError("Could not select Twitter channel in Buffer") from exc


def _copy_text_to_clipboard(text: str, driver=None) -> bool:
    """
    Set clipboard contents so Ctrl+V triggers a real paste event.
    Primary: CDP command (works in headless CI with no OS clipboard).
    Fallback: OS clipboard tools (pbcopy/xclip/xsel).
    """
    if driver is not None:
        try:
            driver.execute_cdp_cmd(
                "Browser.setPermission",
                {"permission": {"name": "clipboard-read"}, "setting": "granted",
                 "origin": driver.execute_script("return window.location.origin")},
            )
            driver.execute_cdp_cmd(
                "Browser.setPermission",
                {"permission": {"name": "clipboard-write"}, "setting": "granted",
                 "origin": driver.execute_script("return window.location.origin")},
            )
        except Exception:
            pass
        try:
            driver.execute_script(
                "await navigator.clipboard.writeText(arguments[0]);", text
            )
            return True
        except Exception:
            pass
        try:
            driver.execute_cdp_cmd(
                "Runtime.evaluate",
                {"expression": f"navigator.clipboard.writeText({repr(text)})",
                 "awaitPromise": True},
            )
            return True
        except Exception:
            pass
    try:
        raw = text.encode("utf-8")
        if sys.platform == "darwin":
            subprocess.run(["pbcopy"], input=raw, check=True)
        elif sys.platform == "win32":
            subprocess.run(["clip"], input=text, text=True, shell=True, check=True)
        else:
            for argv in (["xclip", "-selection", "clipboard"], ["xsel", "--clipboard", "--input"]):
                try:
                    subprocess.run(argv, input=raw, check=True)
                    return True
                except FileNotFoundError:
                    continue
            return False
        return True
    except Exception:
        return False


def _composer_read_text(driver, el) -> str:
    return (
        driver.execute_script(
            """
            const root = arguments[0];
            function read(n) {
                if (!n) return '';
                if (n.tagName === 'TEXTAREA' || n.tagName === 'INPUT') return (n.value || '').trim();
                return (n.innerText || n.textContent || '').trim();
            }
            let t = read(root);
            if (t.length > 0) return t;
            const a = document.activeElement;
            if (a && root && (root === a || root.contains(a))) {
                const u = read(a);
                if (u.length > 0) return u;
            }
            return t;
            """,
            el,
        )
        or ""
    )


def _composer_text_looks_ok(driver, el, expected: str) -> bool:
    got = _composer_read_text(driver, el).strip()
    exp = expected.strip()
    if not exp:
        return True
    if len(exp) <= 12:
        return got == exp
    return len(got) >= max(12, int(0.35 * len(exp)))


def _find_primary_composer(driver):
    """Largest editable in/near composer; pierces shadow roots; prefers composer/editor ancestors."""
    el = driver.execute_script(
        """
        function badHint(el) {
            var p = ((el.getAttribute('placeholder') || '') + ' ' + (el.getAttribute('aria-label') || ''))
                .toLowerCase();
            return p.indexOf('search') >= 0 || p.indexOf('filter') >= 0;
        }
        function composerWeight(el) {
            var n = el;
            for (var i = 0; i < 18 && n; i++) {
                var cls = (n.className && String(n.className).toLowerCase()) || '';
                var tid = ((n.getAttribute && n.getAttribute('data-testid')) || '').toLowerCase();
                if (tid.indexOf('composer') >= 0 || cls.indexOf('composer') >= 0) return 4;
                if (cls.indexOf('draft') >= 0 || cls.indexOf('editor') >= 0 || cls.indexOf('slate') >= 0) return 3;
                if (cls.indexOf('publish') >= 0) return 2;
                n = n.parentElement;
            }
            return 1;
        }
        var nodes = [];
        document.querySelectorAll('textarea, [contenteditable="true"]').forEach(function(el) {
            if (badHint(el)) return;
            var r = el.getBoundingClientRect();
            if (r.width < 40 || r.height < 16) return;
            var st = window.getComputedStyle(el);
            if (st.display === 'none' || st.visibility === 'hidden' || parseFloat(st.opacity || '1') === 0) return;
            if (r.bottom <= 2 || r.top >= window.innerHeight - 2) return;
            var area = r.width * r.height;
            if (area < 300) return;
            var w = composerWeight(el);
            nodes.push({ el: el, score: area * w });
        });
        nodes.sort(function(a, b) { return b.score - a.score; });
        return nodes.length ? nodes[0].el : null;
        """
    )
    if el is not None:
        return el
    scored = []
    for sel in ("textarea", "[contenteditable='true']"):
        for cand in driver.find_elements(By.CSS_SELECTOR, sel):
            try:
                if not cand.is_displayed():
                    continue
                r = cand.rect
                area = r.get("height", 0) * r.get("width", 0)
                if area < 300:
                    continue
                scored.append((area, cand))
            except Exception:
                continue
    if not scored:
        raise RuntimeError("Buffer: could not find main composer text field")
    scored.sort(key=lambda x: -x[0])
    return scored[0][1]


def _set_native_textarea_react(driver, el, text: str) -> None:
    """React-controlled textareas ignore raw .value unless _valueTracker is synced."""
    driver.execute_script(
        """
        const el = arguments[0], value = arguments[1];
        const last = el.value;
        const desc = Object.getOwnPropertyDescriptor(window.HTMLTextAreaElement.prototype, 'value');
        if (desc && desc.set) { desc.set.call(el, value); }
        else { el.value = value; }
        try {
            const tracker = el._valueTracker;
            if (tracker) { tracker.setValue(last); }
        } catch (e) {}
        el.dispatchEvent(new Event('input', { bubbles: true }));
        el.dispatchEvent(new Event('change', { bubbles: true }));
        """,
        el,
        text,
    )


def _js_synthetic_paste(driver, el, text: str) -> bool:
    """Fire a synthetic paste event with DataTransfer — works in headless without OS clipboard."""
    try:
        driver.execute_script(
            """
            const el = arguments[0], text = arguments[1];
            el.focus();
            const dt = new DataTransfer();
            dt.setData('text/plain', text);
            const pe = new ClipboardEvent('paste', {
                bubbles: true, cancelable: true, clipboardData: dt
            });
            el.dispatchEvent(pe);
            """,
            el,
            text,
        )
        return True
    except Exception:
        return False


def _set_composer_text(driver, post_text: str) -> None:
    el = _find_primary_composer(driver)
    driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", el)
    WebDriverWait(driver, 20).until(EC.element_to_be_clickable(el))
    cmd = Keys.COMMAND if sys.platform == "darwin" else Keys.CONTROL

    def focus_clear() -> None:
        el.click()
        time.sleep(0.35)
        ActionChains(driver).click(el).key_down(cmd).send_keys("a").key_up(cmd).pause(0.1).send_keys(Keys.BACKSPACE).perform()
        time.sleep(0.2)

    focus_clear()

    # Method 1: CDP clipboard + Ctrl/Cmd+V
    if _copy_text_to_clipboard(post_text, driver=driver):
        driver.execute_script("arguments[0].focus(); arguments[0].click();", el)
        time.sleep(0.15)
        ActionChains(driver).key_down(cmd).send_keys("v").key_up(cmd).perform()
        time.sleep(0.55)
        if _composer_text_looks_ok(driver, el, post_text):
            return

    # Method 2: synthetic paste event (headless-friendly, no OS clipboard needed)
    focus_clear()
    _js_synthetic_paste(driver, el, post_text)
    time.sleep(0.4)
    if _composer_text_looks_ok(driver, el, post_text):
        return

    # Method 3: execCommand insertText (works for contenteditable)
    focus_clear()
    driver.execute_script(
        """
        const el = arguments[0], t = arguments[1];
        el.focus();
        document.execCommand('selectAll', false, null);
        document.execCommand('insertText', false, t);
        """,
        el,
        post_text,
    )
    time.sleep(0.3)
    if _composer_text_looks_ok(driver, el, post_text):
        return

    # Method 4: React textarea setter
    tag = (el.tag_name or "").lower()
    if tag == "textarea":
        focus_clear()
        _set_native_textarea_react(driver, el, post_text)
        time.sleep(0.3)
        if _composer_text_looks_ok(driver, el, post_text):
            return

    # Method 5: direct send_keys
    focus_clear()
    el.send_keys(post_text)
    time.sleep(0.35)
    if not _composer_text_looks_ok(driver, el, post_text):
        raise RuntimeError(
            "Buffer: main composer text did not stick after all methods; "
            "check composer selectors or run with visible Chrome to see focus."
        )


def _upload_single_image(driver, image_path: str) -> None:
    abs_path = os.path.abspath(image_path)
    if not os.path.isfile(abs_path):
        raise FileNotFoundError(abs_path)
    file_input = None
    for sel in (
        "input[type='file']",
        "[data-testid*='media-upload'] input[type='file']",
        "[data-testid*='image-upload'] input[type='file']",
    ):
        try:
            for el in driver.find_elements(By.CSS_SELECTOR, sel):
                if el.get_attribute("type") == "file":
                    file_input = el
                    break
            if file_input:
                break
        except Exception:
            continue
    if not file_input:
        raise RuntimeError("Buffer: no file input found for image upload")
    file_input.send_keys(abs_path)
    time.sleep(2.5)
    try:
        WebDriverWait(driver, 20).until(
            EC.any_of(
                EC.presence_of_element_located((By.XPATH, "//button[.//span[contains(text(), 'Add description')]]")),
                EC.presence_of_element_located((By.CSS_SELECTOR, "img[src*='blob'], img[src*='buffer']")),
            )
        )
    except Exception:
        pass


def _add_alt_text(driver, alt_text: str) -> None:
    if not alt_text.strip():
        return
    try:
        target_image = None
        for selector in (
            "img[src*='blob']", "img[src*='data:']", "img[src*='buffer']",
            ".publish_mediaContainer img", "[class*='media'] img", "img",
        ):
            try:
                for img in driver.find_elements(By.CSS_SELECTOR, selector):
                    if img.is_displayed() and img.size.get("width", 0) > 50 and img.size.get("height", 0) > 50:
                        target_image = img
                        break
                if target_image:
                    break
            except Exception:
                continue
        if not target_image:
            return

        driver.execute_script("arguments[0].scrollIntoView({behavior:'smooth',block:'center'});", target_image)
        time.sleep(0.3)

        driver.execute_script(
            """
            var img = arguments[0];
            var container = img.closest('[class*="media"], [class*="Media"], [class*="publish_media"]');
            if (!container) container = img.parentElement;
            ['mouseenter','mouseover','mousemove'].forEach(function(t){
                var ev = new MouseEvent(t,{bubbles:true,cancelable:true,view:window});
                container.dispatchEvent(ev);
                img.dispatchEvent(ev);
            });
            """,
            target_image,
        )
        time.sleep(0.5)

        alt_button = driver.execute_script(
            """
            var allButtons = document.querySelectorAll('button.publish_action_ZlY7D');
            for (var i = 0; i < allButtons.length; i++) {
                var btn = allButtons[i];
                var span = btn.querySelector('span.publish_base_D9VRM');
                if (span && span.textContent.includes('Add description')) {
                    var st = window.getComputedStyle(btn);
                    if (st.display !== 'none' && st.visibility !== 'hidden' && st.opacity !== '0') return btn;
                }
            }
            return null;
            """
        )
        if not alt_button:
            for b in driver.find_elements(By.XPATH, "//button[.//span[contains(text(), 'Add description')]]"):
                try:
                    vis = driver.execute_script(
                        "var s=window.getComputedStyle(arguments[0]);"
                        "return s.display!=='none'&&s.visibility!=='hidden'&&s.opacity!=='0';",
                        b,
                    )
                    if vis:
                        alt_button = b
                        break
                except Exception:
                    continue
        if not alt_button:
            for b in driver.find_elements(By.CSS_SELECTOR, "button[aria-label*='Alt'], button[aria-label*='alt'], button.publish_actionButton_hpIK-"):
                if b.is_displayed():
                    alt_button = b
                    break
        if not alt_button:
            return

        driver.execute_script("arguments[0].scrollIntoView({block:'center'});", alt_button)
        try:
            WebDriverWait(driver, 3).until(EC.element_to_be_clickable(alt_button))
            alt_button.click()
        except Exception:
            driver.execute_script("arguments[0].click();", alt_button)
        time.sleep(0.5)

        cmd = Keys.COMMAND if sys.platform == "darwin" else Keys.CONTROL
        alt_input = None
        try:
            alt_input = WebDriverWait(driver, 5).until(
                EC.presence_of_element_located((
                    By.CSS_SELECTOR,
                    "textarea[placeholder*='description'], textarea[placeholder*='alt'], "
                    "input[placeholder*='description'], input[placeholder*='alt'], "
                    "[aria-label*='alt'] textarea, [aria-label*='description'] textarea"
                ))
            )
        except Exception:
            pass
        if not alt_input:
            try:
                alt_input = WebDriverWait(driver, 3).until(
                    EC.element_to_be_clickable((
                        By.XPATH,
                        "//div[@role='dialog']//textarea | "
                        "//div[@role='dialog']//*[@contenteditable='true']"
                    ))
                )
            except Exception:
                pass

        if alt_input:
            alt_input.click()
            time.sleep(0.15)
            try:
                alt_input.clear()
            except Exception:
                pass
            typed = False
            if _copy_text_to_clipboard(alt_text, driver=driver):
                driver.execute_script("arguments[0].focus(); arguments[0].click();", alt_input)
                time.sleep(0.1)
                ActionChains(driver).key_down(cmd).send_keys("v").key_up(cmd).perform()
                time.sleep(0.4)
                typed = True
            if not typed:
                _js_synthetic_paste(driver, alt_input, alt_text)
                time.sleep(0.3)
                typed = True
            got = driver.execute_script(
                "return (arguments[0].value || arguments[0].textContent || '').trim();",
                alt_input,
            )
            if not got:
                _set_native_textarea_react(driver, alt_input, alt_text)
                time.sleep(0.2)
            got = driver.execute_script(
                "return (arguments[0].value || arguments[0].textContent || '').trim();",
                alt_input,
            )
            if not got:
                alt_input.send_keys(alt_text)
        else:
            ActionChains(driver).send_keys(alt_text).perform()

        time.sleep(0.3)

        for selector_type, selector in (
            (By.CSS_SELECTOR, "button.publish_saveButton_iFO4s"),
            (By.CSS_SELECTOR, "button[class*='publish_saveButton']"),
            (By.XPATH, "//button[contains(text(), 'Save')]"),
        ):
            try:
                save_btn = WebDriverWait(driver, 4).until(EC.element_to_be_clickable((selector_type, selector)))
                if save_btn and save_btn.is_displayed():
                    driver.execute_script("arguments[0].scrollIntoView({block:'center'});", save_btn)
                    save_btn.click()
                    time.sleep(0.5)
                    return
            except Exception:
                continue
        ActionChains(driver).send_keys(Keys.ENTER).perform()
    except Exception:
        pass


def _add_thread_reply(driver, reply_text: str) -> None:
    if not reply_text.strip():
        return
    thread_button = None
    for sel in (
        (By.CSS_SELECTOR, "button[data-testid='add-post-to-thread-button']"),
        (By.XPATH, "//button[contains(., 'Start Thread')]"),
        (By.XPATH, "//button[contains(., 'Add another post')]"),
    ):
        try:
            thread_button = driver.find_element(sel[0], sel[1])
            if thread_button.is_displayed():
                break
        except Exception:
            thread_button = None
    if not thread_button:
        return
    driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", thread_button)
    WebDriverWait(driver, 10).until(EC.element_to_be_clickable(thread_button))
    try:
        thread_button.click()
    except Exception:
        driver.execute_script("arguments[0].click();", thread_button)
    time.sleep(0.65)
    tboxes = [t for t in driver.find_elements(By.CSS_SELECTOR, "textarea") if t.is_displayed()]
    if len(tboxes) >= 2:
        thread_el = tboxes[-1]
    elif tboxes:
        thread_el = tboxes[0]
    else:
        boxes = [b for b in driver.find_elements(By.CSS_SELECTOR, "[contenteditable='true']") if b.is_displayed()]
        thread_el = boxes[-1] if boxes else None
    if not thread_el:
        return
    driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", thread_el)
    thread_el.click()
    time.sleep(0.2)
    thread_el.send_keys(reply_text)
    time.sleep(0.2)


def _publish_now(driver) -> None:
    """Click 'Next Available' dropdown → 'Now' → then 'Publish Now' button."""
    dd = driver.execute_script(
        """
        var btns = document.querySelectorAll('button');
        for (var i = 0; i < btns.length; i++) {
            var t = (btns[i].innerText || '').trim();
            if (t.indexOf('Next Available') >= 0) {
                var r = btns[i].getBoundingClientRect();
                if (r.width > 0 && r.height > 0) return btns[i];
            }
        }
        return null;
        """
    )
    if not dd:
        for xp in (
            "//button[contains(., 'Next Available')]",
            "//*[@role='button'][contains(., 'Next Available')]",
        ):
            try:
                for el in driver.find_elements(By.XPATH, xp):
                    if el.is_displayed():
                        dd = el
                        break
                if dd:
                    break
            except Exception:
                continue
    if not dd:
        raise RuntimeError("Buffer: 'Next Available' dropdown not found")
    driver.execute_script("arguments[0].scrollIntoView({block:'center'});", dd)
    dd.click()
    time.sleep(0.6)

    now_btn = None
    for xp in (
        "//button[normalize-space(.)='Now']",
        "//div[normalize-space(.)='Now' and not(descendant::div)]",
        "//span[normalize-space(.)='Now']",
        "//*[normalize-space(.)='Now' and string-length(normalize-space(.))<=4]",
        "//button[contains(., 'Share now')]",
        "//button[contains(., 'right away')]",
    ):
        try:
            for el in driver.find_elements(By.XPATH, xp):
                if el.is_displayed():
                    now_btn = el
                    break
            if now_btn:
                break
        except Exception:
            continue
    if not now_btn:
        raise RuntimeError("Buffer: 'Now' option not found in schedule dropdown")
    now_btn.click()
    time.sleep(0.6)

    pub = driver.execute_script(
        """
        var btns = document.querySelectorAll('button');
        var targets = ['Publish Now', 'Share Now', 'Send Now', 'Post Now'];
        for (var i = 0; i < btns.length; i++) {
            var t = (btns[i].innerText || '').trim();
            for (var j = 0; j < targets.length; j++) {
                if (t === targets[j]) {
                    var r = btns[i].getBoundingClientRect();
                    if (r.width > 0 && r.height > 0) return btns[i];
                }
            }
        }
        return null;
        """
    )
    if not pub:
        for xp in (
            "//button[contains(text(), 'Publish Now')]",
            "//button[contains(text(), 'Share Now')]",
            "//button[contains(text(), 'Send Now')]",
            "//button[contains(text(), 'Post Now')]",
            "//button[contains(text(), 'Publish')]",
        ):
            try:
                el = driver.find_element(By.XPATH, xp)
                if el and el.is_displayed():
                    pub = el
                    break
            except Exception:
                continue
    if not pub:
        raise RuntimeError("Buffer: 'Publish Now' button not found")
    driver.execute_script("arguments[0].scrollIntoView({block:'center'});", pub)
    try:
        WebDriverWait(driver, 10).until(EC.element_to_be_clickable(pub))
        pub.click()
    except Exception:
        driver.execute_script("arguments[0].click();", pub)
    time.sleep(1)


def schedule_twitter_post_via_buffer(
    driver,
    post_text: str,
    image_path: str,
    alt_text: Optional[str] = None,
    reply_text: Optional[str] = None,
) -> None:
    email = os.environ.get("BUFFER_EMAIL", "").strip()
    password = os.environ.get("BUFFER_PASSWORD", "").strip()
    if not email or not password:
        raise RuntimeError("Set BUFFER_EMAIL and BUFFER_PASSWORD for Buffer posting")

    _login_buffer(driver, email, password)
    _open_composer(driver)
    _select_twitter_only(driver)
    _upload_single_image(driver, image_path)
    _set_composer_text(driver, post_text)
    if alt_text:
        _add_alt_text(driver, alt_text)
    if reply_text:
        _add_thread_reply(driver, reply_text)
    _publish_now(driver)

    ok, _url = check_post_scheduled_success(driver, timeout=90)
    if not ok:
        raise RuntimeError("Buffer: success confirmation not detected after scheduling")


class TestUntitled:
    def setup_method(self, method):
        self.screenshot_dir = os.path.dirname(os.path.abspath(__file__))
        self.driver = _make_fresh_driver(
            headless=True,
            window_size=(950, 650),
            download_dir=self.screenshot_dir,
        )

    def teardown_method(self):
        _quit_driver(self.driver)
    
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
        # Adjust metrics
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
            ["xG+xA per 90", "xG per 90"],
            ["xG+xA per 90", "xA per 90"],
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
        weights2 = [0.07, 0.14, 0.07, 0.22, 0.20, 0.13, 0.17]  # Adjust weights for position
        
        selected_url = random.choices(urls, weights=weights2, k=1)[0]                
        self.driver.get(selected_url)
        time.sleep(1)

        assert DATAMB_EMAIL and DATAMB_PASSWORD, (
            "Set DATAMB_EMAIL and DATAMB_PASSWORD (e.g. GitHub repo secrets)."
        )
        WebDriverWait(self.driver, 60).until(
            EC.presence_of_element_located((By.XPATH, "//input[@name='eml']"))
        ).send_keys(DATAMB_EMAIL)

        self.driver.find_element(By.NAME, "pwd").send_keys(DATAMB_PASSWORD)
        self.driver.find_element(By.CSS_SELECTOR, ".SFfrm button").click()
        self.driver.set_window_size(950, 650)
        
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
            weights = [0.22, 0.42, 0.22, 0.06, 0.04, 0.04, 0, 0, 0] # Adjust weights for league
        else:
            league_options = ["Top 7 Leagues", "Top 5 Leagues", "Premier League", 
                             "La Liga", "All Leagues"]
            weights = [0.25, 0.43, 0.05, 0.02, 0.25] # Adjust weights for league

        assert len(weights) == len(league_options), "Weights length must match the league options length"
        selected_league = random.choices(league_options, weights=weights, k=1)[0]
        selected_position = url_to_position.get(selected_url, None)
        
        selected_age = "Age"  # Default
        age_options = ["Age"]  # Default age options
        
        if selected_url != "https://datamb.football/proteamplot/":
            if selected_league == "All Leagues":
                if selected_position != "Goalkeeper":
                    age_options = ["U18", "U19", "U20", "U21", "U23", "U24"]
                else:
                    age_options = ["U19", "U21", "U23", "U24"]
            elif selected_league in ["Top 7 Leagues", "Top 5 Leagues"]:
                if selected_position != "Goalkeeper":
                    age_options = ["Age", "U21", "U23"]
                else:
                    age_options = ["Age", "U24"]
            else:
                age_options = ["Age"]
            
        
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
            
        if len(dots) < 35:
            return False  # Signal that we need to retry
        if len(dots) > 800:
            return False  # Signal that we need to retry
        
        
        screenshot_button = WebDriverWait(self.driver, 10).until(
            EC.element_to_be_clickable((By.XPATH, "//button[@onclick='takeScreenshot()']"))
        )
        screenshot_button.click()
        
        # Wait for the download to complete
        self.wait_for_download(timeout=30)
        
    
        time.sleep(2)

        
        selected_position = url_to_position[selected_url]
        selected_age = selected_age.replace("Age", "")

        # Create the tweet text dynamically
        if selected_url == "https://datamb.football/proteamplot/":
            tweet_text = f"{selected_league} : {selected_position}\n📈 {selected_metric_x} vs {selected_metric_y}\n\nPlot teams 👉 datamb.football"
        else:
            tweet_text = f"{selected_league} : {selected_age} {selected_position}\n📈 {selected_metric_x} vs {selected_metric_y}\n\nPlot more 👉 datamb.football"
        tweet_text = tweet_text.replace("  ", " ")
        tweet_text = tweet_text.replace("All Leagues", "🌍 All Leagues")
        tweet_text = tweet_text.replace("Top 7 Leagues", "🇪🇺 Top 7 Leagues")
        tweet_text = tweet_text.replace("Top 5 Leagues", "🇪🇺 Top 5 Leagues")
        tweet_text = tweet_text.replace("Premier League", "🏴󠁧󠁢󠁥󠁮󠁧󠁿 Premier League")
        tweet_text = tweet_text.replace("La Liga", "🇪🇸 La Liga")
        tweet_text = tweet_text.replace("Bundesliga", "🇩🇪 Bundesliga")
        tweet_text = tweet_text.replace("Serie A", "🇮🇹 Serie A")
        tweet_text = tweet_text.replace(" per 90", "")
        tweet_text = tweet_text.replace("Wingers", "Wingers & Att Mid")
        tweet_text = tweet_text.replace("PPDA", "Pressing")
        tweet_text = tweet_text.replace("completion %", "%")
        tweet_text = tweet_text.replace("accuracy %", "%")
        



        alt_text = (
            "This is an automated tweet 🤖\n\nLeague and metrics were chosen randomly in the 2025/26 dataset.\n\nCompare and plot more team metrics for free on datamb.football"
            if selected_url == "https://datamb.football/proteamplot/"
            else "This is an automated tweet 🤖\n\nPosition, league, age and metrics were chosen randomly in the 2025/26 dataset.\n\nPositions are determined via the player's average heat map.\n\nSubscribe for more leagues and tools!"
        )
        if selected_url == "https://datamb.football/proteamplot/":
            follow_up_text = "Compare and plot more team metrics ⤵️ datamb.football/teams"
        else:
            follow_up_text = "Compare Top 7 League players, or subscribe to plot more leagues and metrics ⤵️ datamb.football"

        screenshot_path = os.path.join(self.screenshot_dir, "DataMB Screenshot.png")
        self._buffer_post_text = tweet_text
        self._buffer_image_path = screenshot_path
        self._buffer_alt_text = alt_text
        self._buffer_reply_text = follow_up_text

        return True

    def test_untitled(self):
        max_retries = 2
        retry_count = 0

        while retry_count < max_retries:
            if self.run_test_iteration():
                break
            retry_count += 1
            if retry_count < max_retries:
                time.sleep(2)
                _quit_driver(self.driver)
                self.setup_method(None)
            else:
                pytest.fail(f"Failed to find sufficient dots/labels after {max_retries} attempts")

        schedule_twitter_post_via_buffer(
            self.driver,
            self._buffer_post_text,
            self._buffer_image_path,
            alt_text=self._buffer_alt_text,
            reply_text=self._buffer_reply_text,
        )
        print("Post scheduled in Buffer (~2 minutes).")





if __name__ == "__main__":
    pytest.main()
