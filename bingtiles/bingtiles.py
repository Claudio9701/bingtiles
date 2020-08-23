import math

class TileSystem(object):
    EARTH_RADIUS = 6378137
    MIN_LATITUDE = -85.05112878
    MAX_LATITUDE = 85.05112878
    MIN_LONGITUDE = -180
    MAX_LONGITUDE = 180

    def clip(self, n, min_value, max_value):
        """
        Clips a number to the specified minimum and maximum values.

        Parameters
        ----------

        n : int
            The number to clip.
        minValue : int
            Minimum allowable value.
        maxValue : int
            Maximum allowable value.

        Returns
        -------

        The clipped value.
        """

        return min(max(n, min_value), max_value)

    def map_size(self, level_of_detail):
        """
        Determines the map width and height (in pixels) at a specified level of detail.

        Parameters
        ----------
        level_of_detail: Level of detail, from 1 (lowest detail) to 23 (highest detail).

        Returns
        -------

        The map width and height in pixels.
        """

        return 256 << level_of_detail

    def ground_resolution(self, latitude, level_of_detail):
        """
        Determines the ground resolution (in meters per pixel) at a specified latitude and level of detail.

        Parameters
        ----------

        latitude : float
            Latitude (in degrees) at which to measure the ground resolution.
        level_of_detail : int
            Level of detail, from 1 (lowest detail) to 23 (highest detail).

        Returns
        -------

        The ground resolution, in meters per pixel.
        """

        latitude = self.clip(latitude, self.MIN_LATITUDE, self.MAX_LATITUDE)
        return math.cos(latitude * math.pi / 180) * 2 * math.pi * self.EARTH_RADIUS / self.map_size(level_of_detail)

    def map_scale(self, latitude, level_of_detail, screen_dpi):
        """
        Determines the map scale at a specified latitude, level of detail, and screen resolution.

        Parameters
        ----------
        latitude : float
            Latitude (in degrees) at which to measure the map scale.
        level_of_detail : int
            Level of detail, from 1 (lowest detail) to 23 (highest detail).
        screen_dpi : int
            Resolution of the screen, in dots per inch.

        Returns
        -------

        The map scale, expressed as the denominator N of the ratio 1 : N.
        """

        return self.ground_resolution(latitude, level_of_detail) * screen_dpi / 0.0254

    def latlong_to_pixel_xy(self, latitude, longitude, level_of_detail):
        """
        Converts a point from latitude/longitude WGS-84 coordinates (in degrees) into pixel XY coordinates at a specified level of detail.

        Parameters
        ----------

        latitude : float
            Latitude of the point, in degrees.
        longitude : float
            Longitude of the point, in degrees.
        level_of_detail : int
            Level of detail, from 1 (lowest detail) to 23 (highest detail).

        Returns
        -------

        pixel_x : int
            Output parameter receiving the X coordinate in pixels.
        pixel_y : int
            Output parameter receiving the Y coordinate in pixels.
        """
        latitude = self.clip(latitude, self.MIN_LATITUDE, self.MAX_LATITUDE)
        longitude = self.clip(longitude, self.MIN_LONGITUDE, self.MAX_LONGITUDE)

        x = (longitude + 180) / 360
        sinLatitude = math.sin(latitude * math.pi / 180)
        y = 0.5 - math.log((1 + sinLatitude) / (1 - sinLatitude)) / (4 * math.pi)

        map_size = self.map_size(level_of_detail)
        pixel_x = self.clip(x * map_size + 0.5, 0, map_size - 1)
        pixel_y = self.clip(y * map_size + 0.5, 0, map_size - 1)

        return pixel_x, pixel_y

    def pixel_xy_to_latlong(self, pixel_x, pixel_y, level_of_detail):
        """
        Converts a pixel from pixel XY coordinates at a specified level of detail into latitude/longitude WGS-84 coordinates (in degrees).

        Parameters
        ----------

        pixel_x : int
            X coordinate of the point, in pixels.
        pixel_y : int
            Y coordinates of the point, in pixels.
        level_of_detail : Level of detail, from 1 (lowest detail) to 23 (highest detail).

        Returns
        -------

        latitude : float
            Output parameter receiving the latitude in degrees.
        longitude: float
            Output parameter receiving the longitude in degrees.
        """

        map_size = self.map_size(level_of_detail)
        x = (self.clip(pixel_x, 0, map_size - 1) / map_size) - 0.5;
        y = 0.5 - (self.clip(pixel_y, 0, map_size - 1) / map_size)

        latitude = 90 - 360 * math.atan(math.exp(-y * 2 * math.pi)) / math.pi
        longitude = 360 * x

        return latitude, longitude

    def pixel_xy_to_tile_xy(self, pixel_x, pixel_y):
        """
        Converts pixel XY coordinates into tile XY coordinates of the tile containing the specified pixel.

        Parameters
        ----------

        pixel_x : int
            Pixel X coordinate.
        pixel_y : int
            Pixel Y coordinate.

        Returns
        -------

        tile_x : int
            Output parameter receiving the tile X coordinate.
        tile_y : int
            Output parameter receiving the tile Y coordinate.
        """

        tile_x = pixel_x / 256
        tile_y = pixel_y / 256

        return tile_x, tile_y

    def tile_xy_to_pixel_xy(self, tile_x, tile_y):
        """
        Converts tile XY coordinates into pixel XY coordinates of the upper-left pixel of the specified tile.

        Parameters
        ----------

        tile_x: int
            Tile X coordinate.
        tile_y: int
            Tile Y coordinate.

        Returns
        -------

        pixel_x : int
            Output parameter receiving the pixel X coordinate.
        pixel_y : int
            Output parameter receiving the pixel Y coordinate.
        """

        pixel_x = tile_x * 256
        pixel_y = tile_y * 256

        return pixel_x, pixel_y

    def tile_xy_to_quadkey(self, tile_x, tile_y, level_of_detail):
        """
        Converts tile XY coordinates into a QuadKey at a specified level of detail.

        Parameters
        ----------

        tile_x : int
            Tile X coordinate.
        tile_y : int
            Tile Y coordinate.
        level_of_detail : int
            Level of detail, from 1 (lowest detail) to 23 (highest detail).

        Returns
        -------

        A string containing the QuadKey.
        """

        quadkey = ''

        for i in range(level_of_detail, 0, -1):
            digit = 0
            mask = 1 << (i - 1)
            if (tile_x & mask) != 0:
                digit += 1
            if (tile_y & mask) != 0:
                digit += 2

            quadkey += str(digit)

        return quadkey

    def quadkey_to_tile_xy(self, quadkey):
        """
        Converts a QuadKey into tile XY coordinates.

        Parameters
        ----------

        quadKey : str
            QuadKey of the tile.

        Returns
        -------

        tile_x : int
            Output parameter receiving the tile X coordinate.
        tile_y : int
            Output parameter receiving the tile Y coordinate.
        level_of_detail : int
            Output parameter receiving the level of detail.
        """

        tile_x = tile_y = 0
        level_of_detail = len(quadkey)

        for i in range(level_of_detail, 0, -1):
            mask = 1 << (i - 1)
            if quadkey[level_of_detail - i] == '0':
                pass
            elif quadkey[level_of_detail - i] == '1':
                tile_x |= mask
            elif quadkey[level_of_detail - i] == '2':
                tile_y |= mask
            elif quadkey[level_of_detail - i] == '3':
                tile_x |= mask
                tile_y |= mask
            else:
                raise ValueError('Invalid QuadKey digit sequence.')

        return tile_x, tile_y, level_of_detail
