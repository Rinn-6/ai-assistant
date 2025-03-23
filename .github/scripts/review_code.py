import os
import requests
import openai

# Load GitHub and OpenAI credentials
TOKEN_GITHUB = os.getenv("TOKEN_GITHUB")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
GITHUB_REPO = os.getenv("GITHUB_REPOSITORY")
PR_NUMBER = os.getenv("GITHUB_REF").split("/")[-1]

HEADERS = {
    "Authorization": f"token {TOKEN_GITHUB}",
    "Accept": "application/vnd.github.v3+json",
}

# Step 1: Fetch PR Files
def get_pr_files():
    url = f"https://api.github.com/repos/{GITHUB_REPO}/pulls/{PR_NUMBER}/files"
    response = requests.get(url, headers=HEADERS)
    return response.json() if response.status_code == 200 else []

# Step 2: Extract Code Changes (Diff)
def get_code_diff():
    files = get_pr_files()
    code_changes = {}
    for file in files:
        code_changes[file["filename"]] = file["patch"]
    return code_changes

# Step 3: Send Code Diff to OpenAI API
def review_code_with_ai(code_changes):
    review_comments = {}
    for filename, diff in code_changes.items():
        prompt = f"Review the following code changes and suggest improvements:\n{diff}"
        response = openai.ChatCompletion.create(
            model="gpt-4-turbo",
            messages=[{"role": "system", "content": prompt}],
            api_key=OPENAI_API_KEY
        )
        review_comments[filename] = response["choices"][0]["message"]["content"]
    return review_comments

# Step 4: Post Review Comments on PR
def post_review_comments(review_comments):
    for filename, comment in review_comments.items():
        url = f"https://api.github.com/repos/{GITHUB_REPO}/pulls/{PR_NUMBER}/reviews"
        data = {
            "event": "COMMENT",
            "comments": [
                {
                    "path": filename,
                    "body": f"### AI Code Review:\n{comment}",
                    "position": 1
                }
            ]
        }
        response = requests.post(url, headers=HEADERS, json=data)
        print(f"GitHub API Response: {response.status_code}, {response.json()}")

# Execute Code Review
if __name__ == "__main__":
    code_changes = get_code_diff()
    review_comments = review_code_with_ai(code_changes)
    post_review_comments(review_comments)
