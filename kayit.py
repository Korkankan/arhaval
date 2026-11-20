import json
import os
import random
import time
from datetime import datetime, timezone
from selenium import webdriver
from selenium.common.exceptions import (
    ElementClickInterceptedException,
    NoSuchElementException,
    TimeoutException,
    WebDriverException,
)
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

DATA_DIR = os.environ.get("DATA_DIR", os.path.dirname(os.path.abspath(__file__)))
os.makedirs(DATA_DIR, exist_ok=True)

ACCOUNTS_FILE = os.path.join(DATA_DIR, "accounts.json")
USED_EMAILS_FILE = os.path.join(DATA_DIR, "used_emails.json")

HOME_URL = "https://arhaval.com/"
QUIZ_URL = "https://arhaval.com/oyunlar/cs2-quiz/oyna?kaynak=ana_sayfa"
RANK_URL = "https://arhaval.com/oyunlar/sirala?kaynak=ana_sayfa"
NEWS_URL = "https://arhaval.com/haberler"
PICKEM_URL = "https://arhaval.com/turnuva/pgl-major-singapore-2026/pickem"
FANTASY_URL = "https://arhaval.com/turnuva/pgl-major-singapore-2026/fantezi"
PREDICT_URL = "https://arhaval.com/turnuva/pgl-major-singapore-2026/tahmin"

# Giriş ve Profil XPath'leri
XPATH_HEADER_LOGIN_LINK = "/html/body/div[2]/div/header/div/div/div/a"
XPATH_EMAIL_INPUT = "/html/body/div[2]/main/div/form/input[1]"
XPATH_PASSWORD_INPUT = "/html/body/div[2]/main/div/form/input[2]"
XPATH_LOGIN_SUBMIT = "/html/body/div[2]/main/div/form/button"

XPATH_NICK_INPUT = "/html/body/div[2]/main/div/div[2]/form/div[1]/div[1]/div[2]/div[1]/input"
XPATH_TEAM_BTN = "/html/body/div[2]/main/div/div[2]/form/div[1]/div[2]/div[2]/button[1]"
XPATH_PROFILE_SUBMIT = "/html/body/div[2]/main/div/div[2]/form/button"

# Quiz XPath'i
XPATH_QUIZ_BTN = "/html/body/div[2]/main/div/div/div/div[2]/div[3]/div/button[1]"

# Sıralama Sayfası XPath'leri
RANK_SEQUENCE = [
    "/html/body/div[2]/main/div/div/button",
    "/html/body/div[2]/main/div/div/div[2]/div[2]/ol/li[3]/button",
    "/html/body/div[2]/main/div/div/div[2]/div[2]/ol/li[1]/div",
    "/html/body/div[2]/main/div/div/div[2]/div[2]/ol/li[4]/button",
    "/html/body/div[2]/main/div/div/div[2]/div[2]/ol/li[5]/button",
]

# Pick'em XPath'leri
XPATH_PICKEM_LIST = "/html/body/div[2]/main/div/div/div[2]/section/div/div[2]/ul"
PICKEM_SLOTS = [
    "/html/body/div[2]/main/div/div/div[2]/section/div/div[1]/div[1]/div[2]/div[1]/span",
    "/html/body/div[2]/main/div/div/div[2]/section/div/div[1]/div[1]/div[2]/div[2]/span",
    "/html/body/div[2]/main/div/div/div[2]/section/div/div[1]/div[2]/div[2]/div[1]/span",
    "/html/body/div[2]/main/div/div/div[2]/section/div/div[1]/div[2]/div[2]/div[2]/span",
    "/html/body/div[2]/main/div/div/div[2]/section/div/div[1]/div[2]/div[2]/div[3]/span",
    "/html/body/div[2]/main/div/div/div[2]/section/div/div[1]/div[2]/div[2]/div[4]/span",
    "/html/body/div[2]/main/div/div/div[2]/section/div/div[1]/div[2]/div[2]/div[5]/span",
    "/html/body/div[2]/main/div/div/div[2]/section/div/div[1]/div[2]/div[2]/div[6]/span",
    "/html/body/div[2]/main/div/div/div[2]/section/div/div[1]/div[3]/div[2]/div[1]/span",
    "/html/body/div[2]/main/div/div/div[2]/section/div/div[1]/div[3]/div[2]/div[2]/span",
]
XPATH_PICKEM_SAVE_BTN = "/html/body/div[2]/main/div/div/div[2]/div[1]/div/button"

# Fantezi XPath'leri
FANTASY_STEPS = [
    ("/html/body/div[2]/main/div/div/div[2]/div[3]/section[1]/ul/li[9]/button", 0),
    ("/html/body/div[2]/main/div/div/div[2]/div[3]/section[2]/ul/li[8]/button", 0),
    ("/html/body/div[2]/main/div/div/div[2]/div[3]/section[3]/ul/li[5]/button", 0),
    ("/html/body/div[2]/main/div/div/div[2]/div[3]/section[4]/ul/li[8]/button", 0),
    ("/html/body/div[2]/main/div/div/div[2]/div[3]/section[5]/ul/li[6]/button", 0),
    ("/html/body/div[2]/main/div/div/div[2]/div[5]/div/button", 3),
    ("/html/body/div[2]/main/div/div/div[2]/section/ul/li[1]/button", 0),
    ("/html/body/div[2]/main/div/div/div[2]/div[2]/div/button", 2),
    ("/html/body/div[3]/div/div[2]/button[2]", 2),
    ("/html/body/div[3]/div/div[2]/button", 2),
]

# Tahmin XPath'leri
PREDICT_STEPS = [
    ("/html/body/div[2]/main/div/div/div[2]/ul/li[1]/div[2]/div[1]/button[1]", 0),
    ("/html/body/div[2]/main/div/div/div[2]/ul/li[2]/div[2]/div[1]/button[1]", 0),
    ("/html/body/div[2]/main/div/div/div[2]/ul/li[3]/div[2]/div[1]/button[2]", 0),
    ("/html/body/div[2]/main/div/div/div[2]/ul/li[4]/div[2]/div[1]/button[1]", 0),
    ("/html/body/div[2]/main/div/div/div[2]/ul/li[5]/div[2]/div[1]/button[1]", 0),
    ("/html/body/div[2]/main/div/div/div[2]/ul/li[6]/div[2]/div[1]/button[1]", 0),
    ("/html/body/div[2]/main/div/div/div[2]/ul/li[7]/div[2]/div[1]/button[1]", 0),
    ("/html/body/div[2]/main/div/div/div[2]/ul/li[8]/div[2]/div[1]/button[1]", 0),
    ("/html/body/div[2]/main/div/div/div[2]/div[2]/div/button[2]", 3),
    ("/html/body/div[3]/div/div[3]/div/button[2]", 3),
    ("/html/body/div[3]/div/div[3]/div/button", 0),
]

CS_PRO_NICKS = [
    "s1mple", "ZywOo", "NiKo", "donk", "m0NESY", "ropz", "Twistzz", "device",
    "sh1ro", "b1t", "f0rest", "GeT_RiGhT", "coldzera", "kennyS", "XANTARES",
    "woxic", "Calyx", "MAJ3R", "karrigan", "gla1ve", "apEX", "electronic",
    "broky", "frozen", "rain", "NAF", "EliGE", "jl", "iM",
]

FOOTBALLERS = [
    "Ronaldo", "Messi", "Zidane", "Mbappe", "Haaland", "Bellingham", "Modric",
    "Neymar", "Pedri", "Salah", "Saka", "Vinicius", "Rodri", "DeBruyne",
    "Kimmich", "Griezmann", "Leao", "Yamal", "ArdaGuler", "KenanYildiz",
]

REAL_NAMES = [
    "Emirhan", "Kaan", "Deniz", "Kerem", "Mert", "Selin", "Ece", "Defne",
    "Zeynep", "Alperen", "Baran", "Eren", "Melis", "Irmak", "Cemre", "Doruk",
    "Adrian", "Lucas", "Mateo", "Elena", "Clara", "Julian", "Noah", "Liam",
]

REAL_SURNAMES = [
    "Kaya", "Yilmaz", "Demir", "Sahin", "Aydin", "Arslan", "Celik", "Koc",
    "Vance", "Sterling", "Mercer", "Hayes", "Brooks", "Bennett", "Parker",
]


def generate_realistic_nickname(used_nicks: set[str]) -> str:
    for _ in range(200):
        mode = random.choice(["cs", "football", "name", "combo"])
        if mode == "cs":
            base = random.choice(CS_PRO_NICKS)
            suffix = random.choice(["", "HQ", "TV", "GG", "Pro", "Aim", "Clutch", "Peak"])
            candidate = f"{base}{suffix}"
        elif mode == "football":
            base = random.choice(FOOTBALLERS)
            suffix = random.choice(["", "FC", "10", "09", "07", "Prime", "X"])
            candidate = f"{base}{suffix}"
        elif mode == "name":
            first = random.choice(REAL_NAMES)
            last = random.choice(REAL_SURNAMES)
            candidate = random.choice([f"{first}{last}", f"{first}.{last}", first, last])
        else:
            first = random.choice(REAL_NAMES)
            pro = random.choice(CS_PRO_NICKS)
            candidate = f"{first}{pro}"

        candidate = candidate.replace(" ", "")
        if 4 <= len(candidate) <= 20 and candidate not in used_nicks:
            used_nicks.add(candidate)
            return candidate

    fallback = f"Atlas{random.choice(REAL_SURNAMES)}"
    used_nicks.add(fallback)
    return fallback


def load_accounts() -> list[dict]:
    if not os.path.exists(ACCOUNTS_FILE):
        raise FileNotFoundError(f"accounts.json bulunamadı: {ACCOUNTS_FILE}")
    with open(ACCOUNTS_FILE, "r", encoding="utf-8") as f:
        data = json.load(f)
    if isinstance(data, dict) and isinstance(data.get("accounts"), list):
        return data["accounts"]
    raise ValueError("accounts.json formatı geçersiz ('accounts' listesi bekleniyor).")


def load_used_emails() -> set[str]:
    if not os.path.exists(USED_EMAILS_FILE):
        return set()
    try:
        with open(USED_EMAILS_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
            if isinstance(data, list):
                return {str(e).strip().lower() for e in data}
            if isinstance(data, dict) and isinstance(data.get("used"), list):
                return {str(e).strip().lower() for e in data["used"]}
    except Exception:
        pass
    return set()


def mark_email_as_used(email: str, used_set: set[str], extra_info: dict | None = None) -> None:
    norm = email.strip().lower()
    used_set.add(norm)

    records = []
    if os.path.exists(USED_EMAILS_FILE):
        try:
            with open(USED_EMAILS_FILE, "r", encoding="utf-8") as f:
                loaded = json.load(f)
                if isinstance(loaded, dict) and isinstance(loaded.get("records"), list):
                    records = loaded["records"]
        except Exception:
            records = []

    entry = {
        "email": email,
        "used_at": datetime.now(timezone.utc).isoformat(),
    }
    if extra_info:
        entry.update(extra_info)
    records.append(entry)

    payload = {
        "used": sorted(used_set),
        "records": records,
    }
    with open(USED_EMAILS_FILE, "w", encoding="utf-8") as f:
        json.dump(payload, f, indent=2, ensure_ascii=False)


def create_driver() -> webdriver.Chrome:
    options = Options()
    options.add_argument("--window-size=1920,1080")
    options.add_argument("--disable-blink-features=AutomationControlled")
    options.add_experimental_option("excludeSwitches", ["enable-automation"])
    options.add_experimental_option("useAutomationExtension", False)

    if os.name != "nt" or os.environ.get("HEADLESS", "").lower() in ("1", "true", "yes"):
        options.add_argument("--headless=new")
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")
        options.add_argument("--disable-gpu")

    chrome_bin = os.environ.get("CHROME_BIN")
    if chrome_bin:
        options.binary_location = chrome_bin

    driver = webdriver.Chrome(options=options)
    driver.set_page_load_timeout(30)
    return driver


def safe_click(driver: webdriver.Chrome, xpath: str, timeout: int = 12) -> bool:
    try:
        elem = WebDriverWait(driver, timeout).until(EC.element_to_be_clickable((By.XPATH, xpath)))
        driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", elem)
        time.sleep(0.2)
        try:
            elem.click()
        except ElementClickInterceptedException:
            driver.execute_script("arguments[0].click();", elem)
        return True
    except (NoSuchElementException, TimeoutException, WebDriverException) as exc:
        print(f"[!] Tıklanamadı ({xpath}): {exc.__class__.__name__}")
        return False


def click_header_login(driver: webdriver.Chrome) -> bool:
    """Önce tam XPath ile dener; olmazsa header içindeki giriş bağlantısını arar."""
    if safe_click(driver, XPATH_HEADER_LOGIN_LINK, timeout=10):
        return True

    fallback_xpaths = [
        "//header//a[contains(@href, 'giris') or contains(@href, 'login') or contains(@href, 'auth') or contains(@href, 'kayit')]",
        "//header//a[contains(translate(normalize-space(.), 'İIĞÜŞÖÇ', 'iigüsoç'), 'giris') or contains(translate(normalize-space(.), 'ABCDEFGHİIJKLMNOPQRSTUVWXYZ', 'abcdefghıijklmnopqrstuvwxyz'), 'login')]",
        "//header//button[contains(translate(normalize-space(.), 'İIĞÜŞÖÇ', 'iigüsoç'), 'giris') or contains(translate(normalize-space(.), 'ABCDEFGHİIJKLMNOPQRSTUVWXYZ', 'abcdefghıijklmnopqrstuvwxyz'), 'login')]",
        "//a[contains(@href, 'giris') or contains(@href, 'login') or contains(@href, 'auth')]",
    ]
    for xp in fallback_xpaths:
        try:
            elems = driver.find_elements(By.XPATH, xp)
            for el in elems:
                if el.is_displayed():
                    driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", el)
                    time.sleep(0.2)
                    try:
                        el.click()
                    except ElementClickInterceptedException:
                        driver.execute_script("arguments[0].click();", el)
                    print(f"[+] Header giriş elementi fallback ile tıklandı: {xp}")
                    return True
        except Exception:
            continue

    print(f"[!] Giriş butonu bulunamadı | URL: {driver.current_url} | Title: {driver.title}")
    return False


def check_nick_status(driver: webdriver.Chrome) -> str:
    time.sleep(5)
    try:
        red_spans = driver.find_elements(By.XPATH, "//span[contains(@class, 'text-red-400')]")
        for sp in red_spans:
            txt = (sp.text or "").strip().lower()
            if "nick alinmis" in txt or "alınmış" in txt or "alinmis" in txt:
                return "taken"
    except Exception:
        pass

    try:
        green_spans = driver.find_elements(By.XPATH, "//span[contains(@class, 'text-emerald-400')]")
        for sp in green_spans:
            txt = (sp.text or "").strip().lower()
            if "musait" in txt or "müsait" in txt:
                return "ok"
    except Exception:
        pass

    return "unknown"


def set_valid_nickname(driver: webdriver.Chrome, used_nicks: set[str]) -> str:
    while True:
        nick = generate_realistic_nickname(used_nicks)
        nick_input = WebDriverWait(driver, 15).until(
            EC.element_to_be_clickable((By.XPATH, XPATH_NICK_INPUT))
        )
        driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", nick_input)
        nick_input.click()
        nick_input.clear()
        nick_input.send_keys(nick)
        print(f"[~] Nick deneniyor: {nick}")

        status = check_nick_status(driver)
        if status == "taken":
            print(f"[!] '{nick}' alınmış, yeni nick deneniyor...")
            continue
        if status == "ok":
            print(f"[+] '{nick}' müsait olarak onaylandı.")
            return nick

        print(f"[+] '{nick}' için hata görünmedi, devam ediliyor.")
        return nick


def play_quiz_for_30_seconds(driver: webdriver.Chrome, total_duration: int = 30, interval: int = 5) -> None:
    driver.get(QUIZ_URL)
    start_time = time.time()
    click_count = 0

    while (time.time() - start_time) < total_duration:
        click_count += 1
        ok = safe_click(driver, XPATH_QUIZ_BTN, timeout=8)
        elapsed = int(time.time() - start_time)
        print(f"[+] Quiz butonu #{click_count} ({elapsed}/{total_duration}s) -> {'OK' if ok else 'Bekleniyor'}")

        remaining = total_duration - (time.time() - start_time)
        if remaining <= 0:
            break
        time.sleep(min(interval, remaining))

    extra_wait = max(0.0, total_duration - (time.time() - start_time))
    if extra_wait > 0:
        time.sleep(extra_wait)
    print("[.] 30 saniye bitti, 5 saniye daha bekleniyor...")
    time.sleep(5)


def run_ranking_flow(driver: webdriver.Chrome) -> None:
    print("[+] Sıralama sayfası açılıyor...")
    driver.get(RANK_URL)
    time.sleep(2)

    for idx, xp in enumerate(RANK_SEQUENCE, start=1):
        ok = safe_click(driver, xp, timeout=12)
        print(f"[+] Sıralama adımı {idx}/{len(RANK_SEQUENCE)} -> {'OK' if ok else 'Bulunamadı'}")
        if idx < len(RANK_SEQUENCE):
            time.sleep(3)

    time.sleep(3)


def scroll_down_and_up(driver: webdriver.Chrome) -> None:
    try:
        driver.execute_script("window.scrollTo({top: document.body.scrollHeight, behavior: 'smooth'});")
        time.sleep(1.5)
        driver.execute_script("window.scrollTo({top: 0, behavior: 'smooth'});")
        time.sleep(1.2)
    except WebDriverException:
        pass


def run_news_flow(driver: webdriver.Chrome, count: int = 2) -> None:
    print("[+] Haberler sayfası açılıyor...")
    driver.get(NEWS_URL)
    time.sleep(2)

    opened_hrefs: set[str] = set()
    for n_idx in range(1, count + 1):
        try:
            WebDriverWait(driver, 12).until(
                EC.presence_of_element_located((By.XPATH, "//a[contains(@href, '/haberler/')]"))
            )
            links = driver.find_elements(By.XPATH, "//a[contains(@href, '/haberler/')]")
            candidates = []
            for a in links:
                href = (a.get_attribute("href") or "").strip()
                if href and href.rstrip("/") != NEWS_URL.rstrip("/") and href not in opened_hrefs:
                    if a.is_displayed():
                        candidates.append((href, a))

            if not candidates:
                print(f"[!] {n_idx}. haber bağlantısı bulunamadı.")
                continue

            chosen_href, chosen_elem = random.choice(candidates)
            opened_hrefs.add(chosen_href)
            print(f"[+] {n_idx}. rastgele haber açılıyor: {chosen_href}")

            driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", chosen_elem)
            time.sleep(0.3)
            try:
                chosen_elem.click()
            except ElementClickInterceptedException:
                driver.execute_script("arguments[0].click();", chosen_elem)

            time.sleep(1.5)
            scroll_down_and_up(driver)

            driver.back()
            time.sleep(2)
        except Exception as exc:
            print(f"[!] Haber {n_idx} hatası: {exc}")
            driver.get(NEWS_URL)
            time.sleep(2)

    print("[.] Haber işlemleri bitti, 3 saniye bekleniyor...")
    time.sleep(3)


def run_pickem_flow(driver: webdriver.Chrome) -> None:
    print("[+] Pick'em sayfası açılıyor...")
    driver.get(PICKEM_URL)
    time.sleep(2)

    for idx, slot_xpath in enumerate(PICKEM_SLOTS, start=1):
        try:
            WebDriverWait(driver, 12).until(
                EC.presence_of_element_located((By.XPATH, XPATH_PICKEM_LIST))
            )
            team_buttons = driver.find_elements(
                By.XPATH, f"{XPATH_PICKEM_LIST}/li/span/span/button"
            )
            available = [b for b in team_buttons if b.is_displayed() and b.is_enabled()]
            if not available:
                print(f"[!] Pick'em {idx}. seçim için kalan takım kalmadı.")
                break

            chosen_team = random.choice(available)
            team_label = (chosen_team.text or chosen_team.get_attribute("aria-label") or "Takım").strip()
            driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", chosen_team)
            time.sleep(0.25)
            try:
                chosen_team.click()
            except ElementClickInterceptedException:
                driver.execute_script("arguments[0].click();", chosen_team)
            print(f"[+] Pick'em {idx}/10 takım seçildi (kalan aday: {len(available)}): {team_label}")
            time.sleep(0.8)

            slot_ok = safe_click(driver, slot_xpath, timeout=10)
            print(f"[+] Pick'em {idx}/10 slot tıklandı -> {'OK' if slot_ok else 'Bulunamadı'}")
            time.sleep(1)
        except Exception as exc:
            print(f"[!] Pick'em {idx}/10 adımında hata: {exc}")

    save_ok = safe_click(driver, XPATH_PICKEM_SAVE_BTN, timeout=12)
    print(f"[+] Pick'em kaydet butonu tıklandı -> {'OK' if save_ok else 'Bulunamadı'}")
    time.sleep(3)


def run_fantasy_flow(driver: webdriver.Chrome) -> None:
    print("[+] Fantezi sayfası açılıyor...")
    driver.get(FANTASY_URL)
    time.sleep(2)

    for step_idx, (xpath, wait_after) in enumerate(FANTASY_STEPS, start=1):
        ok = safe_click(driver, xpath, timeout=12)
        print(f"[+] Fantezi adım {step_idx}/{len(FANTASY_STEPS)} -> {'OK' if ok else 'Bulunamadı'}")
        if wait_after > 0:
            time.sleep(wait_after)
        else:
            time.sleep(1)


def run_predict_flow(driver: webdriver.Chrome) -> None:
    print("[+] Tahmin sayfası açılıyor...")
    driver.get(PREDICT_URL)
    time.sleep(2)

    for step_idx, (xpath, wait_after) in enumerate(PREDICT_STEPS, start=1):
        ok = safe_click(driver, xpath, timeout=12)
        print(f"[+] Tahmin adım {step_idx}/{len(PREDICT_STEPS)} -> {'OK' if ok else 'Bulunamadı'}")
        if wait_after > 0:
            time.sleep(wait_after)
        else:
            time.sleep(0.8)


def run_for_account(email: str, password: str, used_nicks: set[str]) -> str:
    driver = create_driver()
    chosen_nick = ""
    try:
        print(f"\n========== İŞLENEN HESAP: {email} ==========")
        driver.get(HOME_URL)
        WebDriverWait(driver, 15).until(
            lambda d: d.execute_script("return document.readyState") == "complete"
        )
        time.sleep(1.5)

        if not click_header_login(driver):
            raise RuntimeError(f"Giriş butonu bulunamadı/tıklanamadı (URL: {driver.current_url})")

        email_inp = WebDriverWait(driver, 15).until(
            EC.element_to_be_clickable((By.XPATH, XPATH_EMAIL_INPUT))
        )
        email_inp.click()
        email_inp.clear()
        email_inp.send_keys(email)

        pass_inp = WebDriverWait(driver, 15).until(
            EC.element_to_be_clickable((By.XPATH, XPATH_PASSWORD_INPUT))
        )
        pass_inp.click()
        pass_inp.clear()
        pass_inp.send_keys(password)

        if not safe_click(driver, XPATH_LOGIN_SUBMIT, timeout=15):
            raise RuntimeError("Giriş gönder butonu tıklanamadı.")

        chosen_nick = set_valid_nickname(driver, used_nicks)
        safe_click(driver, XPATH_TEAM_BTN, timeout=15)
        safe_click(driver, XPATH_PROFILE_SUBMIT, timeout=15)
        time.sleep(3)

        play_quiz_for_30_seconds(driver, total_duration=30, interval=5)
        run_ranking_flow(driver)
        run_news_flow(driver, count=2)
        run_pickem_flow(driver)
        run_fantasy_flow(driver)
        run_predict_flow(driver)

        return chosen_nick

    finally:
        try:
            driver.delete_all_cookies()
            driver.execute_script("window.localStorage.clear(); window.sessionStorage.clear();")
        except WebDriverException:
            pass
        try:
            driver.quit()
        except WebDriverException:
            pass
        print("[+] Cookie temizlendi ve tarayıcı kapatıldı.")


def main() -> None:
    accounts = load_accounts()
    used_emails = load_used_emails()
    used_nicks: set[str] = set()

    pending_accounts = [
        acc for acc in accounts
        if isinstance(acc, dict)
        and acc.get("email")
        and acc.get("password")
        and acc["email"].strip().lower() not in used_emails
    ]

    if not pending_accounts:
        print("[i] Kullanılmamış yeni hesap bulunamadı.")
        return

    print(f"[+] Toplam {len(pending_accounts)} adet kullanılmamış hesap bulundu.")

    for acc in pending_accounts:
        email = acc["email"].strip()
        password = acc["password"]

        mark_email_as_used(email, used_emails)

        try:
            nick = run_for_account(email, password, used_nicks)
            mark_email_as_used(email, used_emails, {"username": nick, "status": "completed"})
        except Exception as exc:
            print(f"[!] {email} hesabında hata oluştu: {exc}")
            mark_email_as_used(email, used_emails, {"status": "error", "error": str(exc)})

        time.sleep(2)


if __name__ == "__main__":
    main()