import requests
from bs4 import BeautifulSoup

# Returns domain names from given Google Scholar profile page as a string
def gscholar_scraper(url, 
                     headers={'User-Agent':'Mozilla/5.0 (Windows NT 11.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/109.0.5387.128 Safari/537.36'}
                        ):
    try:
        r = requests.get(url, headers = headers)
        r.raise_for_status()
    except:
        return ''   # Return empty string i cannot access given url
    else:
        webpage = r.text
        soup = BeautifulSoup(webpage,'lxml')
        domain = ', '.join([i.text for i in soup.find_all('a', class_="gsc_prf_inta")])
        return domain


# Returns text from read me files of some (maximum 3) pinned repositories of given user as list of strings 
def github_scraper(url, 
                   headers={'User-Agent':'Mozilla/5.0 (Windows NT 11.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/109.0.5387.128 Safari/537.36'}
                    ):
    try:
        r = requests.get(url, headers = headers)
        r.raise_for_status()
    except:
        return []        #Return empty list if cannot access given url
    else:
        profile = r.text
        soup = BeautifulSoup(profile,'lxml')
        
        pinned_items=soup.find_all('div', class_ = 'pinned-item-list-item-content')
        if not pinned_items:
            # No repositories in given profile. Return empty list
            return []
        
        repo_links=[]
        for item in pinned_items[:3]: 
            repo_name=item.find('span', class_='repo').text.strip()
            repo_links.append({"repo_name":repo_name,"repo_link":f"{url}/{repo_name}"})
        
        readme_content = []
        for repo in repo_links:
            try:
                r = requests.get(repo['repo_link'], headers = headers)
                r.raise_for_status()
            except:
                continue  # Ignore repository if cannot acces repo url
            else:
                repo_page = r.text
                repo_soup = BeautifulSoup(repo_page,'lxml')
                readme_span = repo_soup.find(attrs={'data-content':"README"})
                if not readme_span:
                    # Readme file cannot be found in repository. Ignore repository.
                    continue
                readme_text = readme_span.find_next('article', class_="markdown-body").get_text(separator='\n',strip=True)
                readme_content.append(readme_text)
        return readme_content
