import requests
from bs4 import BeautifulSoup

# URL to scrape
URL = "https://ecreationsmultimedia.com/"
SUMMARY_FILE = "agent/ecreations_summary.txt"


def fetch_and_summarize():
    response = requests.get(URL)
    response.raise_for_status()
    soup = BeautifulSoup(response.text, 'html.parser')

    summary = []

    # About Us
    about = soup.find('h2', string=lambda s: s and 'About us' in s)
    if about:
        about_section = about.find_next('div')
        if about_section:
            summary.append("About Us:\n" + about_section.get_text(strip=True))

    # Services
    services = soup.find_all('h4', string=lambda s: s and 'Solutions' in s or 'Animation' in s or 'Studio' in s or 'Presentation' in s)
    if services:
        summary.append("Services:")
        for service in services:
            desc = service.find_next('div')
            if desc:
                summary.append(f"- {service.get_text(strip=True)}: {desc.get_text(strip=True)}")

    # Why Animated Videos
    why_animated = soup.find('h4', string=lambda s: s and 'Why animated videos?' in s)
    if why_animated:
        why_section = why_animated.find_next('div')
        if why_section:
            summary.append("Why Animated Videos:\n" + why_section.get_text(strip=True))

    # Contact Details
    contact = soup.find('h4', string=lambda s: s and 'Contact Details' in s)
    if contact:
        contact_section = contact.find_next('div')
        if contact_section:
            summary.append("Contact Details:\n" + contact_section.get_text(strip=True))

    # Combine and write summary
    with open(SUMMARY_FILE, 'w', encoding='utf-8') as f:
        f.write('\n\n'.join(summary))
    print(f"Summary saved to {SUMMARY_FILE}")


if __name__ == "__main__":
    fetch_and_summarize() 