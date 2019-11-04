## Optimizer Class

The only requirements for an optimizer are to determine each `Host`-instance’s variable `<host>.guests` and each `Guest`-instance’s variable `<guest>.host`.

Your optimizer has to inherit from the abstract base class found in `__init__.py` and has to implement the static method `<Optimizer>.optimize()`.



## How to interpret the generated images

All green dots represent guests which are assigned to a host. All Red dots represent guests the didn't get assigned to a host (only occuring when there are not enough hosts).

All blue dots represent hosts. The numbers above each (group of) hosts indicate the number of guests each host is assigned with.



## What are HostHubs?



When a few hosts are located right next to each other (here: max. 500 meters apart) then it makes sense to combine these hosts in order to save computing power and get a better optimization in the same amount of time.

Each HostHub has a specific set of hosts which therefore determine each hubs `max_guests` count.



## Ideas for Optimizer Moritz_01 (not to be used)

Every Guest gets assigned it closest Host (Just as a starting point).



## Ideas for Optimizer Moritz_02 (not to be used)

Introduction of Host Hubs. Every Host gets assigned as many guests as possible without assigning more than its max. allowed guests starting with the closest guest. 



## Ideas for Optimizer Moritz_03

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
    guests_which_want_this_hub = list(filter(lambda x: x.favorite_host_hub() == 									host_hub, guests_without_hub))
    
    if len(guests_which_want_this_hub) <= host_hub.max_guests_left:
      # If there are enough spots for the guests that want this hub
      guests_to_be_assigned = guests_which_want_this_hub
    else:
      # If there are more guests that want this hub than spots left at this hub
      # (Take the closest ones possible)
      guests_which_want_this_hub = list(sorted(guests_which_want_this_hub, 												key=lambda x: x.favorite_host_hub_distance()))
      guests_to_be_assigned = 																																		guests_which_want_this_hub[0:host_hub.max_guests_left]
		
    # Assign all newly confirmed guests to this hub -> host_hub.guests_taken 	
    # AND host_hubs.max_guests_left BOTH get updated
		host_hub.append_guests(guests_to_be_assigned)

# Removing filled up hosts from each guests favorite_hos_hubs list -> Every Guest 
# now has the closest host WITH free spots at the first spot of this list
# In addition to that host_hub.filled_up gets updated
HostHub.update_hub_lists()
```



## Ideas for Optimizer Moritz_04 (efficiency!)

The whole goal of this build is to increase efficiency of the optimization! It is mainly about two things:

1. I initialize a lot of python `dictionaries` (e.g. each guests `favorite_host_hubs`-list). Creating dicts is costly! I could just use `lists` instead.

2. I pass a lot of objects inside my code: `Guests`-instances and `HostHub`-instance are being passed a lot as function parameters. I am not sure about the efficiency of that but I could also implement id’s for all instances of a class and a very efficient look-up-table/class-method (e.g one single python dictionary for each class) and just pass these id’s instead of objects. I don’t know exactly how much this will increase efficiency.



## Ideas for Optimizer Moritz_05

1. Fully distribute the guests according to Optimizer Moritz_03/Moritz_04
2. Iterate through the longest routes (e.g. longer than 2 * average distance):
    1. For all hosts closer to me than my current host: Is there a guest with whom I can switch hosts so that the overall travelled distance of the two of us is reduced (e.g. by at least 10%)





