import requests
import time
import os
import sys
import subprocess
import logging

# Global variable to store found subdomains
found_subdomains = set()  # Change to a set to avoid duplicates

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Function to check if Python is installed
def check_python():
    try:
        subprocess.check_output(["python", "--version"])
        return True
    except Exception:
        logging.error("Python is not installed. Please install Python to run this tool.")
        sys.exit(1)

# Function to handle API responses
def handle_response(api_name, response):
    try:
        if api_name == "HackerTarget":
            results = response.text.splitlines()
            for entry in results:
                found_subdomains.add(entry.split(",")[0])
        elif api_name == "AlienVault":
            data = response.json()["passive_dns"]
            for item in data:
                found_subdomains.add(item["hostname"])
        elif api_name == "Urlscan":
            data = response.json()["results"]
            for res in data:
                found_subdomains.add(res["task"]["domain"])
        elif api_name == "crt.sh":
            data = response.json()
            for entry in data:
                found_subdomains.add(entry["common_name"])
                found_subdomains.add(entry["name_value"])
    except Exception as e:
        logging.error(f"Error processing data from {api_name} API: {e}")

# Function to fetch subdomains
def fetch_subdomains(api_name, url):
    try:
        response = requests.get(url)
        response.raise_for_status()  # Raise an error for bad responses
        handle_response(api_name, response)
    except requests.RequestException as e:
        logging.error(f"Request failed for {api_name}: {e}")

# Function to run subdomain scan
def run_subdomain_scan(target_domain):
    if not target_domain:
        logging.warning("Please enter a domain.")
        return
    
    found_subdomains.clear()  # Clear previous results
    logging.info("Scanning for subdomains...")

    urls = {
        "HackerTarget": f"https://api.hackertarget.com/hostsearch/?q={target_domain}",
        "AlienVault": f"https://otx.alienvault.com/api/v1/indicators/domain/{target_domain}/passive_dns",
        "Urlscan": f"https://urlscan.io/api/v1/search/?q=domain:{target_domain}",
        "crt.sh": f"https://crt.sh/?q={target_domain}&output=json"
    }

    # Fetch subdomains
    for api_name, url in urls.items():
        fetch_subdomains(api_name, url)

    # Display found subdomains
    print("\nFound Subdomains:")
    for subdomain in found_subdomains:
        print(subdomain)

    print(f"\nSubdomain Count: {len(found_subdomains)}")  # Update subdomain count

def save_results(filename):
    count = 1
    base_filename = filename
    while os.path.exists(f"{filename}.txt"):
        filename = f"{base_filename}({count})"
        count += 1

    with open(f"{filename}.txt", 'w') as file:
        for subdomain in found_subdomains:
            file.write(subdomain + '\n')

    logging.info(f"[+] Results saved to: {filename}.txt")

def clear():
    os.system('cls' if os.name == 'nt' else 'clear')

def banner():
    yellow = "\033[93m"  # Using yellow for the banner
    reset = "\033[0m"
    
    banner_text = f"""{yellow}
  
  ███████ ██    ██ ██████        ███    ███  █████  ███████ ████████ ███████ ██████  
  ██      ██    ██ ██   ██       ████  ████ ██   ██ ██         ██    ██      ██   ██ 
  ███████ ██    ██ ██████  █████ ██ ████ ██ ███████ ███████    ██    █████   ██████  
       ██ ██    ██ ██   ██       ██  ██  ██ ██   ██      ██    ██    ██      ██   ██ 
  ███████  ██████  ██████        ██      ██ ██   ██ ███████    ██    ███████ ██   ██ 
                                                                                 {reset}
=====================================================================================  
[*] coded by ROOT@ANONYMIZER                                                      [*] 
[*] Copyright 2024 HACKINTER                                                      [*] 
[*] just simple tools to make your life easier                                    [*] 
[*] Thanks to ALLAH, Free Palestine                                               [*] 
[*] https://github.com/hackinter (Hacking is Creative problem solving)            [*] 
===================================================================================== {reset}
    """
    print(banner_text)  # Directly print the banner

# Main execution
if __name__ == "__main__":
    check_python()  # Check for Python
    clear()
    banner()  # Show banner
    
    target_domain = input("[*] Enter your target domain (e.g., google.com): ")
    
    run_subdomain_scan(target_domain)  # Start subdomain scan

    save_choice = input("[?] Do you want to save the tool result (Y/N): ").strip().upper()
    
    if save_choice == 'Y':
        filename = input("[!] Enter the filename (without extension): ")
        save_results(filename)  # Save results
    else:
        logging.info("Exiting without saving.")
        print("=====================================================================================")
