## Optimizer Class

The only requirements for an optimizer are to determine each hosts variable `<host_instance>.guests` and each guests variable `<guest_instance>.host`.

Your optimizer has to inherit from the abstract base class found in `__init__.py` and has to implement the static method `<Optimizer>.optimize()`.

In addition to that, if you want to use the image-export-functionality the optimizer has to assign each guest the values for `<guest_instance>.distance_to_hub` (the distance between him and his host).



## How to interpret the generated images

All green dots represent guests which are assigned to a host. All Red dots represent guests that didn't get assigned to a host (only occuring when there are not enough hosts).

All blue dots represent hosts. The numbers above each (group of) hosts indicate the number of guests each host is assigned with.

With this image you can actually see the optimization and also:
* See if there are not enough hosts in a specific area (Ask specific guests to be hosts)
* See if there are too many hosts in a specific area (Manually switch specific hosts to guests)



## What are HostHubs?

When a few hosts are located right next to each other (here: max. 500 meters apart) then it makes sense to combine these hosts in order to save computing power and get a better optimization in the same amount of time.

Each HostHub has a specific set of hosts which therefore determine each hubs `max_guests` count.

For simplicity I will just store one zip-code for each HostHub because nearly every HostHub only consists of hosts in one zip-code-region.



## Ideas for `OptimizerMoritz01` (not to be used - build-up-process)

Every Guest gets assigned it closest Host (Just as a starting point).



## Ideas for `OptimizerMoritz02` (not to be used - build-up-process)

Introduction of Host Hubs. Every Host gets assigned as many guests as possible without assigning more than its max. allowed guests starting with the closest guest. 



## Ideas for `OptimizerMoritz03`

1. Equal distribution of guests among hosts in a host hub!
2. For each guest, determine a list of all host hubs sorted by their distance to that guest:

```python
guest_instance.favorite_host_hubs = [
  {"hub": hub_object, "distance", distance_to_that_hub},
  {"hub": hub_object, "distance", distance_to_that_hub},
  ...
]
```

Each host hub has a variable `guests_taken` (array) where all guests that are confirmed to be with that host hub are stored and a second variable `max_guests_left` which stores how many guests can still be assigned at most.


This is the **Core-Optimization**:

```python
# Loop as long as there are host_spots AND unmatched_guests
while True:
	
  guests_without_hub = list(filter(lambda x: not x.assigned_to_hub, Guest.instances))
  hubs_with_free_spots = list(filter(lambda x: not x.filled_up, HostHub.instances))

  # End optimization if not guest-host-match can be created anymore
  if len(guests_without_hub) == 0 or len(hubs_with_free_spots) == 0:
    break
	
  # Iterate through hosts that have free spots left
  for host_hub in hubs_with_free_spots:
    guests_which_want_this_hub = []
    
    # Determine which guests have this hosthub listed as their favorite one
    guests_which_want_this_hub = list(filter(lambda x: x.favorite_host_hub() == host_hub, guests_without_hub))
    
    if len(guests_which_want_this_hub) <= host_hub.max_guests_left:
      # If there are enough spots for the guests that want this hub
      guests_to_be_assigned = guests_which_want_this_hub
    else:
      # If there are more guests that want this hub than spots left at this hub
      # (Take the closest ones possible)
      guests_which_want_this_hub = list(sorted(guests_which_want_this_hub, key=lambda x: x.favorite_host_hub_distance()))
      guests_to_be_assigned = guests_which_want_this_hub[0:host_hub.max_guests_left]
		
    # Assign all newly confirmed guests to this hub -> host_hub.guests_taken 	
    # AND host_hubs.max_guests_left BOTH get updated
    host_hub.append_guests(guests_to_be_assigned)

# Removing filled up hosts from each guests favorite_hos_hubs list -> Every Guest 
# now has the closest host WITH free spots at the first spot of this list
# In addition to that host_hub.filled_up gets updated
HostHub.update_hub_lists()
```



## Ideas for `OptimizerMoritz04` (efficiency!)

The whole goal of this build is to increase efficiency of the optimization! It is mainly about two things:

1. I initialize a lot of python `dictionaries` (e.g. each guests `favorite_host_hubs`-list). Creating dicts is costly! I could just use `lists` instead.
2. I pass a lot of objects inside my code: `Guests`-instances and `HostHub`-instance are being passed a lot as function parameters. I am not sure about the efficiency of that but I could also implement id’s for all instances of a class and a very efficient look-up-table/class-method (e.g one single python dictionary for each class) and just pass these id’s instead of objects. I don’t know exactly how much this will increase efficiency.

**Success! :)** The main factor slowing the program down was querying the database (not in memory …) So by caching the results inside a dictionary (hash table) I could resolve that issue. A few other minor tweaks to make the code more elegant.

**Result** for 400 participants: Moritz_03 (Overall about 42 seconds) -> Moritz_04 (Overall about 12 seconds).

**Important:** The optimizer v4 will produce exactly the same result as the optimizer v5. It’s just faster ;).



## Ideas for `OptimizerMoritz05`

1. Fully distribute the guests according to Optimizer Moritz_03/Moritz_04
2. Iterate through the longest routes (e.g. longer than 50% of the average distance):
    1. Is there a guest with whom I can switch hosts so that the overall travelled distance of the two of us is reduced

**Important:** This Brute-Forcing does not switch places between guests who do have a spot and guests who do not have a spot. 
**The reason for that decision** is that I want to handle the selection of people who get a spot (probably meaning they were first to the sign up) inside the first distribution of guests (optimizer v3/v4).


This is the **Core-Optimization**:

```python

round_number = 0
average_travel_distance = 0

while True:
  matched_guests = list(filter(lambda x: x.assigned_to_hub, Guest.instances))
  matched_guests = list(sorted(matched_guests, key=lambda x: x.distance_to_hub))

  
  new_average_travel_distance = 0
  for guest in matched_guests:
    new_average_travel_distance += guest.distance_to_hub
    new_average_travel_distance /= len(matched_guests)
	
  # Determine all guests to be possibly rematched
  guests_with_long_distances = list(filter(lambda x: x.distance_to_hub > 1.5 * new_average_travel_distance, matched_guests))
  
  # At least 10 itearations
  # stop iterating, when optimization is not converging anymore
  # At most 100 iterations
  if round_number > 10:
    if round_number >= 100 or round(new_average_travel_distance, 6) == round(average_travel_distance, 6):
      break
	
  # Using two variables for the average distance so we can detect the rate of convergence between iterations
  average_travel_distance = new_average_travel_distance
  round_number += 1
	
  # Prevent to switch one participant twice in one iteration -> Weird convergence
  switched_guests = []

  for unlucky_guest in guests_with_long_distances[::]:
    # Determine the partner where the switch is best
    saved_distance_when_switched = 0
    switch_partner = None

    if unlucky_guest in switched_guests:
      continue

    for lucky_guest in matched_guests:
      if unlucky_guest.hub == lucky_guest.hub or lucky_guest in switched_guests:
        continue
			
      # Compare distances how they are and how they would be if
      # 'unlucky_guest' and 'lucky_guest' were to switch places
      ...

      if (distance_before_switch - distance_after_switch) > saved_distance_when_switched:
      	switch_partner = lucky_guest
        saved_distance_when_switched = distance_before_switch - distance_after_switch

    if switch_partner is not None:
      # Actually switch spots

      # Prevent these two participants to take part in another switch this round
      switched_guests.append(unlucky_guest)
      switched_guests.append(switch_partner)

      # Change each guest's hub reference
      unlucky_guest.hub, switch_partner.hub = switch_partner.hub, unlucky_guest.hub

      # Changes each guest's hub's guest list
      unlucky_guest.hub.guests_taken.remove(switch_partner)
      unlucky_guest.hub.guests_taken.append(unlucky_guest)
      switch_partner.hub.guests_taken.remove(unlucky_guest)
      switch_partner.hub.guests_taken.append(switch_partner)

      # Change each guest's distance_to_hub value
      unlucky_guest.distance_to_hub = OptimizerMoritz05.zip_distances[unlucky_guest.zip_string][unlucky_guest.hub.zip_string]
      switch_partner.distance_to_hub = OptimizerMoritz05.zip_distances[switch_partner.zip_string][switch_partner.hub.zip_string]

```


Here is the optimized distribution **before** this brute-force approach:

![](45_comparison/brute_forcing_fine_trim_04.png)


Here is the optimized distribution **after** this brute-force approach:

![](45_comparison/brute_forcing_fine_trim_05.png)



## Ideas for `OptimizerMoritz06`

The thing is, the quality-measurement that is used most in optimization/approximation problems is the squared error (squared travelled distance) instead of the linear error. So I used the squared travelled distance in the Optimizer v6.


Here is the optimized distribution the brute-forcing with **minimized *linear* travel distance**:

![](56_comparison/linear_error.png)


Here is the optimized distribution the brute-forcing with **minimized *squared* travel distance**:

![](56_comparison/squared_error.png)




## Ideas for the Future

I could use the **API of the public transit company of munich (MVG)** to evaluate the distances between 
guests and host regarding travel time with public transit and not just the straight geometric distance.


