import requests
import base64
import re

# GitHub API 令牌，GitHub Actions 中可通过环境变量传入
GITHUB_TOKEN = None

def get_headers():
    headers = {'Accept': 'application/vnd.github.v3+json'}
    token = GITHUB_TOKEN or ''
    if token:
        headers['Authorization'] = f'token {token}'
    return headers

def search_forks(page=1):
    query = 'fork:true repo:senshinya/MoonTV'
    url = f'https://api.github.com/search/repositories?q={query}&per_page=30&page={page}'
    response = requests.get(url, headers=get_headers())
    if response.status_code == 200:
        return response.json()
    else:
        print(f'请求失败: {response.status_code} {response.text}')
        return None

def get_readme_links(full_name):
    url = f'https://api.github.com/repos/{full_name}/readme'
    response = requests.get(url, headers=get_headers())
    if response.status_code == 200:
        content = response.json().get('content', '')
        readme_text = base64.b64decode(content).decode('utf-8')
        links = re.findall(r'https?://[^\s)]+', readme_text)
        filtered = [link for link in links if any(k in link.lower() for k in ['demo', 'vercel', 'deploy', 'shinya', 'netlify'])]
        return filtered
    return []

def main():
    forks = []
    for page in range(1, 5):  # 最多查4页，每页30个
        result = search_forks(page)
        if not result or 'items' not in result:
            break
        for repo in result['items']:
            full_name = repo['full_name']
            links = get_readme_links(full_name)
            print(f'仓库: {full_name}')
            if links:
                print('可能的部署链接:')
                for link in links:
                    print(f'  - {link}')
            else:
                print('无明显部署链接')
            print('-' * 40)

if __name__ == '__main__':
    import os
    GITHUB_TOKEN = os.getenv('MY_GITHUB_TOKEN')  # 你可以在GitHub Actions里设置此环境变量
    main()
