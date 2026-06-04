import requests

def fetch_leetcode_stats(username: str) -> dict:
    url = "https://leetcode.com/graphql"
    query = """
    query getUserProfile($username: String!) {
      matchedUser(username: $username) {
        submitStats: submitStatsGlobal {
          acSubmissionNum {
            difficulty
            count
          }
        }
      }
    }
    """
    try:
        resp = requests.post(url, json={"query": query, "variables": {"username": username}}, timeout=10)
        if resp.status_code == 200:
            data = resp.json()
            user_data = data.get("data", {}).get("matchedUser")
            if user_data:
                stats = user_data["submitStats"]["acSubmissionNum"]
                return {item["difficulty"]: item["count"] for item in stats}
    except Exception:
        pass
    return {}

def fetch_stackoverflow_stats(username: str) -> dict:
    # This tries to match by display name, which might not be perfectly unique, but it's a best effort
    url = f"https://api.stackexchange.com/2.3/users?order=desc&sort=reputation&inname={username}&site=stackoverflow"
    try:
        resp = requests.get(url, timeout=10)
        if resp.status_code == 200:
            items = resp.json().get("items", [])
            if items:
                # Return the best match (highest reputation)
                best_match = items[0]
                return {
                    "reputation": best_match.get("reputation"),
                    "badges": best_match.get("badge_counts"),
                    "link": best_match.get("link")
                }
    except Exception:
        pass
    return {}
