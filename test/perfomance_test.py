import asyncio
import httpx
import random
import matplotlib.pyplot as plt
import os
from load_balancer.utils import fetch_all_urls

REQUEST_COUNT = 10000
CHARTS_DIR = 'charts'

# Ensure the charts directory exists
os.makedirs(CHARTS_DIR, exist_ok=True)

# Function to generate random server names for testing
def generate_servers(count):
    return [f'Server_{i+1}' for i in range(count)]

# Function to simulate load balancing by sending requests to servers
async def send_requests(server_count, modified=False):
    servers = generate_servers(server_count)
    base_url = "http://localhost:5000/request" if not modified else "http://localhost:5000/request_mod"
    urls = [f"{base_url}?server={random.choice(servers)}" for _ in range(REQUEST_COUNT)]
    
    responses = await fetch_all_urls(urls)
    
    # Counting the requests handled by each server
    server_counts = {server: responses.count(server) for server in servers}
    
    return server_counts

# Function to plot the results
def plot_results(server_counts, server_count, modified=False):
    servers = list(server_counts.keys())
    counts = list(server_counts.values())
    
    plt.figure(figsize=(10, 6))
    plt.bar(servers, counts, color='skyblue')
    plt.xlabel('Server')
    plt.ylabel('Requests Handled')
    plt.title(f'Requests Handled by Each Server (server_count = {server_count}){" - Modified Hash" if modified else ""}')
    plt.xticks(rotation=45)
    
    chart_name = f'n{server_count}{"_mod" if modified else ""}.png'
    plt.savefig(os.path.join(CHARTS_DIR, chart_name))
    plt.close()

async def main():
    server_counts = [2, 3, 4, 5, 6]
    
    for count in server_counts:
        # Test with original hash function
        results = await send_requests(count, modified=False)
        plot_results(results, count, modified=False)
        
        # Test with modified hash function
        results_mod = await send_requests(count, modified=True)
        plot_results(results_mod, count, modified=True)

if __name__ == "__main__":
    asyncio.run(main())
