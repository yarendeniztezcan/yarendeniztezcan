import os
import requests
import re

GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")
USERNAME = os.getenv("GITHUB_ACTOR", "yarendeniztezcan")
README_FILE = "README.md"

# Simple grading logic (customize!)
def grade_for_language(lang, count):
    if count > 100:
        return "A"
    elif count > 50:
        return "B"
    elif count > 20:
        return "C+"
    elif count > 10:
        return "C"
    else:
        return "D"

def get_repos(username):
    url = f"https://api.github.com/users/{username}/repos?per_page=100"
    headers = {"Authorization": f"token {GITHUB_TOKEN}"}
    repos, page = [], 1
    while True:
        resp = requests.get(url + f"&page={page}", headers=headers)
        data = resp.json()
        if not data or resp.status_code != 200:
            break
        repos.extend(data)
        page += 1
    return repos

def get_language_stats(repos):
    lang_stats = {}
    for repo in repos:
        if repo.get("fork"):
            continue
        langs_url = repo["languages_url"]
        headers = {"Authorization": f"token {GITHUB_TOKEN}"}
        resp = requests.get(langs_url, headers=headers)
        if resp.status_code != 200:
            continue
        data = resp.json()
        for lang, count in data.items():
            lang_stats[lang] = lang_stats.get(lang, 0) + count
    return lang_stats

def update_readme_table(lang_stats):
    table = "| Language | Grade |\n|----------|-------|\n"
    for lang, count in sorted(lang_stats.items(), key=lambda x: -x[1]):
        grade = grade_for_language(lang, count)
        table += f"| {lang} | {grade} |\n"

    with open(README_FILE, "r", encoding="utf-8") as f:
        content = f.read()
    new_content = re.sub(
        r"(<!--START_LANG_SCORES-->)(.*?)(<!--END_LANG_SCORES-->)",
        r"\1\n" + table + r"\3",
        content,
        flags=re.DOTALL,
    )
    with open(README_FILE, "w", encoding="utf-8") as f:
        f.write(new_content)

def main():
    repos = get_repos(USERNAME)
    lang_stats = get_language_stats(repos)
    update_readme_table(lang_stats)

if __name__ == "__main__":
    main()
