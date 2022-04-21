"""
Concept proof for generating the footprint of a satellite using
the aperture angle of the instrument and the attitude of the
satellite (roll, pitch and yaw)

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

def plot_vector(ax, x, y, z, color = "C1", label = None):
    soa = np.array([[0, 0, 0, x, y, z]])
    X, Y, Z, U, V, W = zip(*soa)
    ax.quiver(X, Y, Z, U, V, W, color=color, arrow_length_ratio = 0.03, label=label)

def display_satellite_footprint(satellite_positions, alpha, roll, pitch, yaw, ax = None):
    '''
    Function to display the satellite footprint

    :param satellite_positions: list of satellite positions [x1, y1, z1, ..., xn, yn, zn]
    :type satellite_positions: list
    '''

    print("Genearing footprint with the following configuration:\n\t- alpha: {}\n\t- roll: {}\n\t- pitch: {}\n\t- yaw: {}\n".format(alpha, roll, pitch, yaw))
    
    create_figure = False
    # Creating an empty figure or plot
    if not ax:
        create_figure = True
        fig = plt.figure()

        # Defining the axes as a 3D axes so that we can plot 3D data into it.
        ax = plt.axes(projection="3d")

        # Set title
        ax.set_title("Satellite footprint")
    # end if

    # Set axis limits
    ax.set_xlim([-7000, 7000])
    ax.set_ylim([-7000, 7000])
    ax.set_zlim([-7000, 7000])

    # Calculate angles corresponding to the aperture of the instrument seen from ground
    alpha_radians = (alpha*2*math.pi)/360
    roll_radians = (roll*2*math.pi)/360
    a1_radians = math.asin(((semimajor)*math.sin(roll_radians-alpha_radians))/earth_radius)
    a1_degrees = 180-(a1_radians*360)/(2*math.pi)
    a2_radians = math.asin(((semimajor)*math.sin(roll_radians))/earth_radius)
    a2_degrees = 180-(a2_radians*360)/(2*math.pi)
    a3_radians = math.asin(((semimajor)*math.sin(roll_radians+alpha_radians))/earth_radius)
    a3_degrees = 180-(a3_radians*360)/(2*math.pi)
    b1 = 180-a1_degrees-roll+alpha
    b2 = 180-a2_degrees-roll
    b3 = 180-a3_degrees-roll-alpha

    print("a angles in radians -> a1: {}, a2: {}, a3: {}".format(a1_radians, a2_radians, a3_radians))
    print("a angles in degrees -> a1: {}, a2: {}, a3: {}".format(a1_degrees, a2_degrees, a3_degrees))
    print("Aperture angles from ground -> b1: {}, b2: {}, b3: {}".format(b1, b2, b3))
    
    x_satellite_line = []
    y_satellite_line = []
    z_satellite_line = []
    x_satellite_projection_line = []
    y_satellite_projection_line = []
    z_satellite_projection_line = []
    x_left_line = []
    y_left_line = []
    z_left_line = []
    x_right_line = []
    y_right_line = []
    z_right_line = []
    i = 0
    satellite_coordinates = []
    right_coordinates = []
    left_coordinates = []
    while i < len(satellite_positions):
        # Get X, Y and Z position of the satellite
        satellite_x = satellite_positions[i]
        satellite_y = satellite_positions[i+1]
        satellite_z = satellite_positions[i+2]

        plot_vector(ax, satellite_x, satellite_y, satellite_z, color = "C4")
        # Populate line to plot
        x_satellite_line.append(satellite_x)
        y_satellite_line.append(satellite_y)
        z_satellite_line.append(satellite_z)


        satellite_position = SkyCoord(x=satellite_x, y=satellite_y, z=satellite_z, frame='itrs', unit=("km", "km", "km"), representation_type="cartesian")
        latitude = satellite_position.earth_location.lat.value
        longitude = satellite_position.earth_location.lon.value
        satellite_projection = SkyCoord(lat=latitude, lon=longitude, distance=earth_radius, frame='itrs', unit=("deg", "deg", "km"), representation_type="spherical")

        satellite_projection_x = satellite_projection.earth_location.x.value
        satellite_projection_y = satellite_projection.earth_location.y.value
        satellite_projection_z = satellite_projection.earth_location.z.value

        satellite_coordinates.append("{} {}".format(satellite_projection.earth_location.lon.value, satellite_projection.earth_location.lat.value))

        plot_vector(ax, satellite_projection_x, satellite_projection_y, satellite_projection_z, color = "C5", label=r'$\vec{PROJ}$')
        x_satellite_projection_line.append(satellite_projection_x)
        y_satellite_projection_line.append(satellite_projection_y)
        z_satellite_projection_line.append(satellite_projection_z)

        i += 3

        # Set the positions in the array of the sibling satellite position
        x_position_sibling = i
        y_position_sibling = i+1
        z_position_sibling = i+2
        rotation_axis_sign = 1
        if i >= len(satellite_positions):
            x_position_sibling = i-6
            y_position_sibling = i-5
            z_position_sibling = i-4
            rotation_axis_sign = -1
        # end if

        # Get X, Y and Z position for the following set
        satellite_sibling_x = satellite_positions[x_position_sibling]
        satellite_sibling_y = satellite_positions[y_position_sibling]
        satellite_sibling_z = satellite_positions[z_position_sibling]

        # Get perpendicular vector to satellite positions
        x_roll = np.cross([satellite_x, satellite_y, satellite_z], [satellite_sibling_x, satellite_sibling_y, satellite_sibling_z])*rotation_axis_sign

        plot_vector(ax, x_roll[0]/10000, x_roll[1]/10000, x_roll[2]/10000, color="C6", label=r'$\vec{xroll}$')

        # Get the other vector to build the orthogonal system
        y_roll = np.cross([satellite_x, satellite_y, satellite_z], [x_roll[0], x_roll[1], x_roll[2]])

        plot_vector(ax, y_roll[0]/10000000, y_roll[1]/10000000, y_roll[2]/10000000, color="C7", label=r'$\vec{yroll}$')

        # Define rotations for roll + alpha
        y_roll_unit = y_roll / np.linalg.norm(y_roll)

        rotation_roll_alpha_b1 = define_rotation_axis([y_roll_unit[0], y_roll_unit[1], y_roll_unit[2]], b1)
        rotation_roll_alpha_b3 = define_rotation_axis([y_roll_unit[0], y_roll_unit[1], y_roll_unit[2]], b3)

        satellite_projection_roll_b1 = rotation_roll_alpha_b1.apply([satellite_projection_x, satellite_projection_y, satellite_projection_z])
        satellite_projection_roll_b3 = rotation_roll_alpha_b3.apply([satellite_projection_x, satellite_projection_y, satellite_projection_z])

        plot_vector(ax, satellite_projection_roll_b1[0], satellite_projection_roll_b1[1], satellite_projection_roll_b1[2], color="C8", label=r'$\vec{ROLLB1}$')
        plot_vector(ax, satellite_projection_roll_b3[0], satellite_projection_roll_b3[1], satellite_projection_roll_b3[2], color="C9", label=r'$\vec{ROLLB3}$')

        # Populate lines to plot
        x_right_line.append(satellite_projection_roll_b1[0])
        y_right_line.append(satellite_projection_roll_b1[1])
        z_right_line.append(satellite_projection_roll_b1[2])

        x_left_line.append(satellite_projection_roll_b3[0])
        y_left_line.append(satellite_projection_roll_b3[1])
        z_left_line.append(satellite_projection_roll_b3[2])

        # Obtain latitude and longitudes of the footprint
        footprint_right_position = satellite_projection_roll_b1
        footprint_left_position = satellite_projection_roll_b3

        footprint_right_position = SkyCoord(x=satellite_projection_roll_b1[0], y=satellite_projection_roll_b1[1], z=satellite_projection_roll_b1[2], frame='itrs', unit=("km", "km", "km"), representation_type="cartesian")
        right_coordinates.append("{} {}".format(footprint_right_position.earth_location.lon.value, footprint_right_position.earth_location.lat.value))

        footprint_left_position = SkyCoord(x=satellite_projection_roll_b3[0], y=satellite_projection_roll_b3[1], z=satellite_projection_roll_b3[2], frame='itrs', unit=("km", "km", "km"), representation_type="cartesian")
        left_coordinates.append("{} {}".format(footprint_left_position.earth_location.lon.value, footprint_left_position.earth_location.lat.value))

        
    # end while

    if create_figure:
        ax.quiver(-3, 0, 0, 7000, 0, 0, color='C1', arrow_length_ratio=0.05, label=r'$\vec{x}$') # x-axis
        ax.quiver(0, -3, 0, 0, 7000, 0, color='C2', arrow_length_ratio=0.05, label=r'$\vec{y}$') # y-axis
        ax.quiver(0, 0, -3, 0, 0, 7000, color='C3', arrow_length_ratio=0.1, label=r'$\vec{z}$') # z-axis
    # end if

    plt.legend()
    ax.plot(x_satellite_line, y_satellite_line, z_satellite_line)
    ax.plot(x_satellite_projection_line, y_satellite_projection_line, z_satellite_projection_line)
    ax.plot(x_right_line, y_right_line, z_right_line)
    ax.plot(x_left_line, y_left_line, z_left_line)

    # Print coordinates
    satellite_coordinates_to_reverse = satellite_coordinates.copy()
    satellite_coordinates_to_reverse.reverse()
    print("\nSATELLITE COORDINATES: {}".format(", ".join(satellite_coordinates) + ", " + ", ".join(satellite_coordinates_to_reverse)))

    # Reverse left coordinates to join with right coordinates
    left_coordinates.reverse()    
    print("\nFOOTPRINT COORDINATES: {}".format(", ".join(right_coordinates) + ", " + ", ".join(left_coordinates) + ", " + right_coordinates[0]))

    return ax

def main():

    args_parser = argparse.ArgumentParser(description="Concept proof for generating the footprint of a satellite using the aperture angle of the instrument and the attitude of the satellite (roll, pitch and yaw).")
    args_parser.add_argument('-s', dest='semimajor', type=float, nargs=1,
                             help='Semimajor axis of the orbit of the satellite', required=True)
    args_parser.add_argument("-p", "--print_output",
                             help="Print positions of the satellite at the limits of the visibility mask of the station", action="store_true")
    args_parser.add_argument("-d", "--display_figures",
                             help="Display figures showing the transformations done to obtain the positions of the satellite at the limits of the visibility mask of the station", action="store_true")

    args = args_parser.parse_args()

    # Semimajor axis
    semimajor_input = args.semimajor[0]
    global semimajor
    semimajor = semimajor_input

    global satellite_orbit
    satellite_orbit = semimajor - earth_radius

    ############
    # TO CHANGE
    ############
    # Satellite positions to extract the footprint
    satellite_positions = [4116.4252784963965, 538.0266314184722, 5432.194461466122, 4297.5005885873, 505.3103680398974, 5293.470446356712, 4644.859880553402, 435.83463574374537, 4997.870033415377, 5125.7071730974985, 322.511890734203, 4512.100420156531, 5683.728487148855, 157.38304626969443, 3793.9918086159964, 6233.11228293895, -64.77305959268692, 2802.491287691588]

    # Display footprint of the satellite
    display_satellite_footprint(satellite_positions, alpha = 0.705176738839256, roll = 0, pitch = 0, yaw = 0)
    
    # Showing the above plot
    display_figures = args.display_figures
    if display_figures:
        plt.show()
    # end if

if __name__ == "__main__":

    main()
