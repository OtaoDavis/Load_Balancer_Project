# Load Balancer Performance Analysis

# Evaluation:

A Python script was used to send 10,000 requests to the API endpoint. The responses were analyzed to extract the server number handling each request, providing insights into the request distribution across servers.

### Experiment 1:

10,000 asynchronous requests were launched on **server_count = 3** server containers, and the request count handled by each server instance is shown below.

<img src=charts/n3.png>

The chart reveals that server 3 handled more than 50% of the total requests. The hash function in the load balancer distributes requests unevenly across servers, resulting in an imbalanced distribution.

When launched on **server_count = 2** server containers, the bar chart showed that server 1 handled over 80% of the requests.

<img src=charts/n2.png>


For **server_count = 4** servers, the chart indicates that servers 1 and 2 handled over 80% of the requests collectively.

<img src=charts/n4.png>

With **server_count = 5** servers, the chart showed that servers 1, 2, 3, and 4 handled a similar number of requests, while server 5 handled less than 10% of the total.

<img src=charts/n5.png>

Finally, when launched on **server_count = 6** server containers, the bar chart revealed that all servers handled a similar percentage of the total requests.

<img src=charts/n6.png>

### Conclusion:
The results demonstrate that as the number of servers increases, the hash function in the load balancer distributes the requests more evenly across servers, reducing the imbalance.

### Experiment 2:

10,000 asynchronous requests were launched on **server_count = 3** server containers using a modified hash function, and the request distribution is presented below.

<img src=charts/n3_mod.png>

The chart shows that server 2 handled more than 50% of the requests, indicating an uneven distribution.

With **server_count = 2** servers, a line chart revealed that server 1 handled over 80% of the requests.

<img src=charts/n2_mod.png>

When launched on **server_count = 4** server containers, the chart below shows that servers 1 and 2 handled over 80% of the requests collectively.

<img src=charts/n4_mod.png>

With **server_count = 5** servers, the line chart indicated that servers 1, 2, 3, and 4 handled a similar number of requests, while server 5 handled less than 10% of the total.

<img src=charts/n5_mod.png>

Finally, for **server_count = 6** servers, the chart reveales that all servers handled a similar percentage of the total requests.

<img src=charts/n6_mod.png>

The results suggest that while the modified hash function distributes the load evenly for a smaller number of servers, the distribution becomes skewed as the number of servers increases, with some servers handling significantly fewer requests than others.
