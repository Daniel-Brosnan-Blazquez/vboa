"""
Concept proof for converting Azimuth and Elevation values
contained in the station mask to cartesian coordinates

Written by DEIMOS Space S.L. (dibb)

module vboa

Install the following packages to use this module:
pip3 install numpy
pip3 install matplotlib
pip3 install astropy
pip3 install lxml
pip3 install scipy

For obtaining the desired output to be inserted in a CZML for cesium, execute the script as follows:
python3 generate_cartesian_visibility_mask.py -s SEMIMAJOR_AXIS -p -f STATION_MASK_PATH|sed 's/(//g'|sed 's/)//g'
"""
# Import python utilities
import numpy as np
import matplotlib.pyplot as plt
import argparse
import os
import math

# Import xml parser
from lxml import etree

# Import astropy utilities
from astropy.coordinates import SkyCoord

# Import scipy utilities
from scipy.spatial.transform import Rotation as R

##########
# Configurations
##########
# Set the radius of the Earth in km
earth_radius = 6378.1370
# Set the orbit of the satellite in km
semimajor = earth_radius

class Transformation():
    '''
    Class to manage transformations of the set of points
    '''

    def __init__(self, title = ""):
        '''
        Method to initialize the object

        :param title: title of the figure showing the transformation
        :type title: str
        '''

        # XYZ vectors
        self.vectors = []
        # X, Y and Z values for drawing a line that joins all of the corresponding points
        self.x_line = []
        self.y_line = []
        self.z_line = []
        # Minimum and maximum values for X, Y and Z
        self.min_x = 0
        self.max_x = 0
        self.min_y = 0
        self.max_y = 0
        self.min_z = 0
        self.max_z = 0
        # Title of the figure showing the transformation
        self.title = title

    def insert_position(self, x, y, z, ox = 0, oy = 0, oz = 0):
        '''
        Method to populate the vector, line and set the minimum and maximum values

        :param x: X value
        :type x: float
        :param y: Y value
        :type y: float
        :param z: Z value
        :type z: float
        :param ox: value for X at origin
        :type ox: float
        :param oy: value for Y at origin
        :type oy: float
        :param oz: value for Z at origin
        :type oz: float
        '''        

        self.vectors.append([ox, oy, oz, x, y, z])
        self.x_line.append(x)
        self.y_line.append(y)
        self.z_line.append(z)
        self.min_x, self.min_y, self.min_z, self.max_x, self.max_y, self.max_z = get_max_min(x, y, z, self.min_x, self.min_y, self.min_z, self.max_x, self.max_y, self.max_z)

    def plot(self):
        """
        Method to plot the vectors and line of a transformation

        :return: Axes of the figure
        :rtype: plt.axes
        """
        
        # Creating an empty figure or plot
        fig = plt.figure()
        # Defining the axes as a 3D axes so that we can plot 3D data into it.
        ax = plt.axes(projection="3d")

        # Set title
        ax.set_title(self.title)

        # Defining the axes as a 3D axes so that we can plot 3D data into it.
        ax = plt.axes(projection="3d")

        soa = np.array(self.vectors)
        X, Y, Z, U, V, W = zip(*soa)
        ax.quiver(X, Y, Z, U, V, W, arrow_length_ratio = 0.03)

        ax.plot(self.x_line, self.y_line, self.z_line)

        min_x = self.min_x
        if min_x > -3:
            min_x = -3
        # end if
        max_x = self.max_x
        if max_x <= 0:
            max_x = -min_x
        # end if
        
        min_y = self.min_y
        if min_y > -3:
            min_y = -3
        # end if
        max_y = self.max_y
        if max_y <= 0:
            max_y = -min_y
        # end if
                
        min_z = self.min_z
        if min_z > -3:
            min_z = -3
        # end if
        max_z = self.max_z
        if max_z <= 0:
            max_z = -min_z
        # end if

        ax.quiver(-3, 0, 0, max_x, 0, 0, color='C1', arrow_length_ratio=0.05, label=r'$\vec{x}$') # x-axis
        ax.quiver(0, -3, 0, 0, max_y, 0, color='C2', arrow_length_ratio=0.05, label=r'$\vec{y}$') # y-axis
        ax.quiver(0, 0, -3, 0, 0, max_z, color='C3', arrow_length_ratio=0.1, label=r'$\vec{z}$') # z-axis

        plt.legend()
        # Set axist limits
        ax.set_xlim([min_x, max_x])
        ax.set_ylim([min_y, max_y])
        ax.set_zlim([min_z, max_z])

        return ax

def get_station_xyz(station_mask_path):
    '''
    Function to obtain the X, Y and Z values from the station mask

    :param station_mask_path: Path to the station mask
    :type station_mask_path: str

    :return: X, Y and Z values obtained from the station mask
    :rtype: tuple
    '''

    # Get X, Y and Z position of the station
    # Parse file
    parsed_xml = etree.parse(station_mask_path)
    xpath_xml = etree.XPathEvaluator(parsed_xml)

    ground_station = xpath_xml("/GroundConfigurationFile/GroundStation")[0]
    x = float(ground_station.get("PositionX"))
    y = float(ground_station.get("PositionY"))
    z = float(ground_station.get("PositionZ"))

    return x, y, z
    
def define_transformation_structure(key, title, transformations):
    '''
    Function to define the structure for a transformation
    :param key: key of the relevant transformation
    :type key: N/A
    :param title: title of the figure showing the transformation
    :type title: str
    :param transformations: structure containing the transformations
    :type transformations: dict

    :return: structure of the transformations
    :rtype: dict
    '''
    
    if not key in transformations:
        transformations[key] = Transformation(title)
    # end if

    return transformations

def display_position_station(station_mask_path):
    '''
    Function to display position of the station

    :param station_mask_path: Path to the station mask
    :type station_mask_path: str
    '''

    # Creating an empty figure or plot
    fig = plt.figure()

    # Defining the axes as a 3D axes so that we can plot 3D data into it.
    ax = plt.axes(projection="3d")

    # Set title
    ax.set_title("Station position")

    # Set axis limits
    ax.set_xlim([0, 2000])
    ax.set_ylim([0, 400])
    ax.set_zlim([0, 7000])

    # Get X, Y and Z position of the station
    x, y, z = get_station_xyz(station_mask_path)

    # Draw vector to the position of the station
    # Origin = [0,0,0]
    # Destination = [x, y, z] in kms
    soa = np.array([[0, 0, 0, x, y, z]])
    X, Y, Z, U, V, W = zip(*soa)
    ax.quiver(X, Y, Z, U, V, W, arrow_length_ratio = 0.03)

    return

def get_max_min(x, y, z, min_x, min_y, min_z, max_x, max_y, max_z):
    '''
    Function to obtain maximum X, Y and Z values from a set
    :param x: X value
    :type x: float
    :param y: Y value
    :type y: float
    :param z: Z value
    :type z: float
    :param min_x: Minimum previous value for X
    :type min_x: float
    :param min_y: Minimum previous value for Y
    :type min_y: float
    :param min_z: Minimum previous value for Z
    :type min_z: float
    :param max_x: Maximum previous value for X
    :type max_x: float
    :param max_y: Maximum previous value for Y
    :type max_y: float
    :param max_z: Maximum previous value for Z
    :type max_z: float

    :return: minimum and maximum values for X, Y and Z
    :rtype: tuple
    '''

    if x < min_x:
        min_x = x
    # end if
    if x > max_x:
        max_x = x
    # end if

    if y < min_y:
        min_y = y
    # end if
    if y > max_y:
        max_y = y
    # end if

    if z < min_z:
        min_z = z
    # end if
    if z > max_z:
        max_z = z
    # end if

    return min_x, min_y, min_z, max_x, max_y, max_z

def calculate_and_display_visibility_mask(station_mask_path):
    '''
    Function to calculate and display the position of the visibility mask of the station

    Reference system used is ITRS coordination frame. This frame has the axes defined as follows
                           |Z
                           |
                           |____ Y
                          /
                         / X

    :param station_mask_path: Path to the station mask
    :type station_mask_path: str

    :return: list of satellite positions
    :rtype: list
    '''

    # Creating an empty figure or plot
    fig = plt.figure()
    # Defining the axes as a 3D axes so that we can plot 3D data into it.
    ax = plt.axes(projection="3d")

    # Set title
    ax.set_title("Visibility mask positions")

    # Defining the axes as a 3D axes so that we can plot 3D data into it.
    ax = plt.axes(projection="3d")
    
    # Parse file
    parsed_xml = etree.parse(station_mask_path)
    xpath_xml = etree.XPathEvaluator(parsed_xml)

    points = xpath_xml("/GroundConfigurationFile/GroundStation/Antenna/VisibilityPattern/Point")

    satellite_positions = []
    x_line = []
    y_line = []
    z_line = []
    min_x = 0
    max_x = 0
    min_y = 0
    max_y = 0
    min_z = 0
    max_z = 0
    for point in points:
        # Get Azimuth and Elevation values (degress and radians)
        azimuth_deg = float(point.get("Azimuth"))
        azimuth = azimuth_deg*((2*math.pi)/360)
        elevation_deg = float(point.get("Elevation"))
        elevation = elevation_deg*((2*math.pi)/360)

        slant_range = earth_radius * (np.sqrt(((earth_radius + satellite_orbit)/earth_radius)**2 - math.cos(elevation)**2) - math.sin(elevation))

        # Get the satellite position in the "International terrestrial
        # reference system" using spherical coordinates:
        satellite_position = SkyCoord(phi=360-azimuth_deg, theta=(90-elevation_deg), r=slant_range, frame='itrs', unit=("deg", "deg", "km"), representation_type="physicsspherical")

        x = satellite_position.earth_location.x.value
        y = satellite_position.earth_location.y.value
        z = satellite_position.earth_location.z.value

        # Populate line to plot
        x_line.append(x)
        y_line.append(y)
        z_line.append(z)

        # Populate satellite positions
        satellite_positions.append([x, y, z])

        # print("Azimuth: {}, Elevation: {}, d: {}, x: {}, y: {}, z: {}".format(azimuth_deg, elevation_deg, slant_range, x, y, z))

        # Draw vector to the corresponding position of the satellite from the station
        # Origin = [0,0,0]
        soa = np.array([[0, 0, 0, x, y, z]])
        X, Y, Z, U, V, W = zip(*soa)
        ax.quiver(X, Y, Z, U, V, W, arrow_length_ratio = 0.03)

        min_x, min_y, min_z, max_x, max_y, max_z = get_max_min(x, y, z, min_x, min_y, min_z, max_x, max_y, max_z)

    # end for

    ax.plot(x_line, y_line, z_line)
    
    min_axis = min([min_x, min_y])
    max_axis = max([max_x, max_y])

    ax.quiver(-3, 0, 0, max_axis, 0, 0, color='C1', arrow_length_ratio=0.05, label=r'$\vec{x}$') # x-axis
    ax.quiver(0, -3, 0, 0, max_axis, 0, color='C2', arrow_length_ratio=0.05, label=r'$\vec{y}$') # y-axis
    ax.quiver(0, 0, -3, 0, 0, max_z, color='C3', arrow_length_ratio=0.1, label=r'$\vec{z}$') # z-axis

    plt.legend()
    # Set axist limits
    ax.set_xlim([min_axis, max_axis])
    ax.set_ylim([min_axis, max_axis])
    ax.set_zlim([0, max_z])
    
    return satellite_positions

def define_rotation_axis(axis, degrees):
    '''
    Function to define the rotation axis given the axis and the degrees to rotate

    :param axis: List of X, Y and Z values
    :type axis: list
    :param degrees: degrees to rotate
    :type degrees: float

    :return: rotation to apply
    :rtype: rotation
    '''

    rotation_vector = np.radians(degrees) * np.array(axis)

    return R.from_rotvec(rotation_vector)

def place_satellite_positions(satellite_positions, station_mask_path):
    '''
    Function to apply the different transformation to move the
    calculated satellite positions in the Earth Centered reference
    frame to the reference frame of the station

    :param satellite_positions: list of the satellite positions relative to the center of the Earth
    :type satellite_positions: list
    :param station_mask_path: Path to the station mask
    :type station_mask_path: str

    :return: list of satellite positions at the limits of the visibility mask of the station
    :rtype: list
    '''

    # Get X, Y and Z position of the station
    station_x, station_y, station_z = get_station_xyz(station_mask_path)

    # Get latitude and longitude of the station
    station_position = SkyCoord(x=station_x, y=station_y, z=station_z, frame='itrs', unit=("km", "km", "km"), representation_type="cartesian")
    latitude = station_position.earth_location.lat.value
    longitude = station_position.earth_location.lon.value

    # Rotations direction are anticlockwise
    rotation_180_z = define_rotation_axis([0, 0, 1], 180)
    rotation_90_y = define_rotation_axis([0, 1, 0], 90)
    rotation_lon_z = define_rotation_axis([0, 0, 1], longitude)

    # Obtain vector perpendicular to GSZ2
    rotation_90_z = define_rotation_axis([0, 0, 1], 90)
    gsz2 = rotation_lon_z.apply([1, 0, 0])
    pgsz2 = rotation_90_z.apply(gsz2)
    rotation_lat_pgsz2 = define_rotation_axis(pgsz2, -latitude)

    transformations = {}
    for position in satellite_positions:

        # Rotate 180 degress around z axis
        define_transformation_structure(1, "First transformation: Rotate 180º around Z", transformations)        
        new_position = rotation_180_z.apply(position)
        x = new_position[0]
        y = new_position[1]
        z = new_position[2]
        transformations[1].insert_position(x, y, z)

        # Rotate 90 degress around y axis
        define_transformation_structure(2, "Second transformation: Rotate -90º around Y", transformations)
        new_position = rotation_90_y.apply(new_position)
        x = new_position[0]
        y = new_position[1]
        z = new_position[2]
        transformations[2].insert_position(x, y, z)

        # Rotate lon degress around z axis
        define_transformation_structure(3, "Third transformation: Rotate longitude degrees around Z", transformations)
        new_position = rotation_lon_z.apply(new_position)
        x = new_position[0]
        y = new_position[1]
        z = new_position[2]
        transformations[3].insert_position(x, y, z)

        # Rotate lat degress around pgsz2 axis
        define_transformation_structure(4, "Forth transformation: Rotate latitude degrees around PGSZ2", transformations)
        new_position = rotation_lat_pgsz2.apply(new_position)
        x = new_position[0]
        y = new_position[1]
        z = new_position[2]
        transformations[4].insert_position(x, y, z)

        # Make a translation movement corresponding to the station position
        define_transformation_structure(5, "Fifth transformation: Make a translation movement corresponding to the station position", transformations)
        x = new_position[0] + station_x
        y = new_position[1] + station_y
        z = new_position[2] + station_z
        transformations[5].insert_position(x, y, z)

    # end for
    
    # Draw vectors of a selected transformation
    ax = transformations[1].plot()
    north = rotation_180_z.apply([1, 0, 0])
    gsz = rotation_180_z.apply([0, 0, 1])
    ax.quiver(0, 0, 0, north[0]*1000, north[1]*1000, north[2]*1000, color='C4', arrow_length_ratio=0.1, label=r'$\vec{north}$')
    ax.quiver(0, 0, 0, gsz[0]*1000, gsz[1]*1000, gsz[2]*1000, color='C5', arrow_length_ratio=0.1, label=r'$\vec{gsz}$')
    plt.legend()
    
    ax = transformations[2].plot()
    north = rotation_90_y.apply(north)
    gsz = rotation_90_y.apply(gsz)
    ax.quiver(0, 0, 0, north[0]*1000, north[1]*1000, north[2]*1000, color='C4', arrow_length_ratio=0.1, label=r'$\vec{north}$')
    ax.quiver(0, 0, 0, gsz[0]*1000, gsz[1]*1000, gsz[2]*1000, color='C5', arrow_length_ratio=0.1, label=r'$\vec{gsz}$')
    plt.legend()
    ax.set_xlim([-2000, 2000])
    ax.set_ylim([-2000, 2000])
    ax.set_zlim([-2000, 2000])

    ax = transformations[3].plot()
    gsz2 = rotation_lon_z.apply([1, 0, 0])
    ax.quiver(0, 0, 0, gsz2[0]*1000, gsz2[1]*1000, gsz2[2]*1000, color='C4', arrow_length_ratio=0.1, label=r'$\vec{gsz2}$')
    north = rotation_lon_z.apply(north)
    gsz = rotation_lon_z.apply(gsz)
    ax.quiver(0, 0, 0, north[0]*1000, north[1]*1000, north[2]*1000, color='C5', arrow_length_ratio=0.1, label=r'$\vec{north}$')
    ax.quiver(0, 0, 0, gsz[0]*1000, gsz[1]*1000, gsz[2]*1000, color='C6', arrow_length_ratio=0.1, label=r'$\vec{gsz}$')
    ax.set_xlim([-2000, 2000])
    ax.set_ylim([-2000, 2000])
    ax.set_zlim([-2000, 2000])

    plt.legend()
    
    ax = transformations[4].plot()
    ax.quiver(0, 0, 0, pgsz2[0]*1000, pgsz2[1]*1000, pgsz2[2]*1000, color='C4', arrow_length_ratio=0.1, label=r'$\vec{pgsz2}$')
    ax.quiver(0, 0, 0, station_x, station_y, station_z, color='C5', arrow_length_ratio=0.1, label=r'$\vec{gsp}$')
    north = rotation_lat_pgsz2.apply(north)
    gsz = rotation_lat_pgsz2.apply(gsz)
    ax.quiver(0, 0, 0, north[0]*1000, north[1]*1000, north[2]*1000, color='C6', arrow_length_ratio=0.1, label=r'$\vec{north}$')
    ax.quiver(0, 0, 0, gsz[0]*1000, gsz[1]*1000, gsz[2]*1000, color='C7', arrow_length_ratio=0.1, label=r'$\vec{gsz}$')
    ax.set_xlim([-7000, 7000])
    ax.set_ylim([-7000, 7000])
    ax.set_zlim([-1000, 1000])
    
    plt.legend()

    ax = transformations[5].plot()
    ax.quiver(0, 0, 0, pgsz2[0]*1000, pgsz2[1]*1000, pgsz2[2]*1000, color='C4', arrow_length_ratio=0.1, label=r'$\vec{pgsz2}$')
    ax.quiver(0, 0, 0, station_x, station_y, station_z, color='C5', arrow_length_ratio=0.1, label=r'$\vec{gsp}$')
    ax.set_xlim([-7000, 7000])
    ax.set_ylim([-7000, 7000])
    ax.set_zlim([-7000, 7000])
    
    plt.legend()

    return transformations[5].vectors
    
def main():

    args_parser = argparse.ArgumentParser(description="Concept proof for generating the 3D positions of the visibility mask of the station.")
    args_parser.add_argument('-f', dest='station_mask_path', type=str, nargs=1,
                             help='Path to the station mask definition', required=True)
    args_parser.add_argument('-s', dest='semimajor', type=float, nargs=1,
                             help='Semimajor axis of the orbit of the satellite', required=True)
    args_parser.add_argument("-p", "--print_output",
                             help="Print positions of the satellite at the limits of the visibility mask of the station", action="store_true")
    args_parser.add_argument("-d", "--display_figures",
                             help="Display figures showing the transformations done to obtain the positions of the satellite at the limits of the visibility mask of the station", action="store_true")

    args = args_parser.parse_args()

    # Station mask path
    station_mask_path = args.station_mask_path[0]
    # Check if file exists
    if not os.path.isfile(station_mask_path):
        logger.error("The specified file {} does not exist".format(station_mask_path))
        exit_code = -1
    # end if

    # Semimajor axis
    semimajor_input = args.semimajor[0]
    global semimajor
    semimajor = semimajor_input

    global satellite_orbit
    satellite_orbit = semimajor - earth_radius

    # # Display position of the station
    display_position_station(station_mask_path)

    # Calculate and display visibility mask of the station at the center of the Earth
    satellite_positions = calculate_and_display_visibility_mask(station_mask_path)

    # Place satellite positions
    vectors = place_satellite_positions(satellite_positions, station_mask_path)

    print_output = args.print_output
    if print_output:
        print([(vector[3]*1000,vector[4]*1000,vector[5]*1000) for vector in vectors])
    # end if

    # Showing the above plot
    display_figures = args.display_figures
    if display_figures:
        plt.show()
    # end if

if __name__ == "__main__":

    main()
