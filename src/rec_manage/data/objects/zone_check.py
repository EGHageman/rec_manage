
"""
zone_check.py
Zone checking utilities for rec_manage.
Author: Ethan Hageman
Version: 0.1
"""
class zonecheck:
    """Utility class for checking if a point is within a polygonal zone."""

    def point_in_polygon(self, lat, lon, polygon):
        """Checks if the given lat lon are within a polygon, adapted from the geeks for geeks point in polygon algorithm"""
        x, y = lon, lat
        n = len(polygon)
        inside = False

        for i in range(n):
            j = (i + 1) % n
            xi, yi = polygon[i]
            xj, yj = polygon[j]

           
            if ((yi > y) != (yj > y)):
                x_intersect = (xj - xi) * (y - yi) / (yj - yi + 1e-12) + xi
                if x < x_intersect:
                    inside = not inside

        return inside