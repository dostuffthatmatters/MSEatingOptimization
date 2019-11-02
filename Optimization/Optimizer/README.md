## What are HostHubs?



When a few hosts are located right next to each other (max. n (here: 500) meters apart) then it makes sense to combine these hosts in order to save computing power and get a better opitimzation in the same amount of time.

Each HostHubs has a specific set of hosts which therefore determine each hubs `max_guests` count.



## Idea of Optimizer Moritz 04



1. For each guest, determine a list of all host hubs sorted by their distance to that guest:

```python
guest_instance.favorite_host_hubs = [
  {"hub": hub_object, "distance", distance_to_that_hub},
  {"hub": hub_object, "distance", distance_to_that_hub},
  ...
]
```



2. For each host hub, determine a list of all guests sorted by their distance to that host hub:

```python
host_hub_instance.favorite_guests = [
  {"guest": guest_object, "distance", distance_to_that_guest},
  {"guest": guest_object, "distance", distance_to_that_guest},
  ...
]
```



Each host hub has a variable `guests_taken` (array) where all guests that are confirmed to be with that host hub are stored. 