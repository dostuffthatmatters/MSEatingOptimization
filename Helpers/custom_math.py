import math

class CustomMath:

    @staticmethod
    def haversine(origin, destination):
        # Implementation of the haversine formula
        # Author: Wayne Dyck
        # Source: https://gist.github.com/rochacbruno/2883505

        lat1, lng1 = origin
        lat2, lng2 = destination
        radius = 6371  # km

        dlat = math.radians(lat2 - lat1)
        dlon = math.radians(lng2 - lng1)
        a = math.sin(dlat / 2) * math.sin(dlat / 2) + math.cos(math.radians(lat1)) \
            * math.cos(math.radians(lat2)) * math.sin(dlon / 2) * math.sin(dlon / 2)
        c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
        distance = radius * c

        return distance
