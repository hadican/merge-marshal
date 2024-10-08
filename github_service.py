from typing import List, Dict, Any

import aiohttp


class GitHubService:
    BASE_URL = "https://api.github.com"

    def __init__(self, access_token: str):
        self.access_token = access_token
        self.headers = {
            "Authorization": f"token {self.access_token}",
            "Accept": "application/vnd.github.v3+json",
        }

    async def get_data(self, url: str, params: Dict[str, Any] = None) -> List[Dict[str, Any]]:
        async with aiohttp.ClientSession() as session:
            all_data = []
            while url:
                async with session.get(url, headers=self.headers, params=params) as response:
                    response.raise_for_status()
                    all_data.extend(await response.json())
                    url = response.links.get("next", {}).get("url")
                    params = None  # Clear params after first request
            return all_data

    async def list_private_repos(self, org_name: str) -> List[Dict[str, str]]:
        url = f"{self.BASE_URL}/orgs/{org_name}/repos"
        params = {"type": "private", "per_page": 100}
        repos = await self.get_data(url, params)
        return [{"name": repo["name"], "full_name": repo["full_name"]} for repo in repos]

    async def get_open_prs(self, repo: Dict[str, str]) -> List[Dict[str, Any]]:
        url = f"{self.BASE_URL}/repos/{repo['full_name']}/pulls"
        params = {"state": "open", "per_page": 100}
        return await self.get_data(url, params)

    async def get_pr_reviews(self, repo: Dict[str, str], pr_number: int) -> List[Dict[str, Any]]:
        url = f"{self.BASE_URL}/repos/{repo['full_name']}/pulls/{pr_number}/reviews"
        return await self.get_data(url)
