import geopy
import geopy.distance
import numpy
from collections import namedtuple
from flightplannerdir.wpml_writer import wpml_generator
from flightplannerdir.kml_generator import generate_kml_file
from constants.aws import WPML_PATH, KML_PATH

PointData = namedtuple('PointData',
                       ['length_distance', 'width_distance', 'length1_coords', 'length2_coords', 'width1_coords',
                        'width2_coords'])

PointRequiredData = namedtuple('PointRequiredData',
                               ['points_required', 'new_trigger_distance'])

BoundryPoints = namedtuple('BoundryPoints', ['first_width_points', 'first_length_points',
                                             'second_length_points'])

SpacingBoundryPoints = namedtuple('SpacingBoundryPoints', ['length_coordinates', 'width_required_points',
                                                           'top_view_height'])


def check_first_two_poits_is_width(coords) -> PointData:
    """
    returning length and width coords with their distances.
    length is smaller in distance than width.
    """

    first_distance = None
    second_distance = None
    for i in range(2):
        if not i:
            first_distance = geopy.distance.geodesic((coords[0][1], coords[0][0]), (coords[1][1], coords[1][0])).meters
        else:
            second_distance = geopy.distance.geodesic((coords[1][1], coords[1][0]), (coords[2][1], coords[2][0])).meters

    if first_distance > second_distance:
        # original first point is width
        return PointData(
            length_distance=round(second_distance, 5),
            width_distance=round(first_distance, 5),
            length1_coords=((coords[1][1], coords[1][0]), (coords[2][1], coords[2][0])),
            length2_coords=((coords[3][1], coords[3][0]), (coords[0][1], coords[0][0])),
            width1_coords=((coords[0][1], coords[0][0]), (coords[1][1], coords[1][0])),
            width2_coords=((coords[2][1], coords[2][0]), (coords[3][1], coords[3][0]))
        )
    else:
        return PointData(
            length_distance=round(first_distance, 5),
            width_distance=round(second_distance, 5),
            width1_coords=((coords[1][1], coords[1][0]), (coords[2][1], coords[2][0])),
            width2_coords=((coords[3][1], coords[3][0]), (coords[0][1], coords[0][0])),
            length1_coords=((coords[0][1], coords[0][0]), (coords[1][1], coords[1][0])),
            length2_coords=((coords[2][1], coords[2][0]), (coords[3][1], coords[3][0]))
        )


def get_required_points_count(total_distance, trigger_distance) -> PointRequiredData:
    print("le", total_distance)
    points_required, need_increase_point_count = divmod(total_distance, trigger_distance)

    if need_increase_point_count:
        points_required += 1

    points_required = int(points_required)
    return PointRequiredData(
        points_required=points_required,
        new_trigger_distance=total_distance / points_required
    )


def get_trigger_cords_for_boundry(coords, points_required):
    points = list(zip(numpy.linspace(coords[0][0], coords[1][0], points_required+1),
                      numpy.linspace(coords[0][1], coords[1][1], points_required+1)))
    points = convert_points_to_float(points=points)
    return points


def convert_points_to_float(points):
    final_points = []
    for each_point in points:
        final_points.append([round(float(each_point[0]), 6), round(float(each_point[1]), 6)])
    return final_points


def get_coordinates(boundry_point_1, boundry_point_2):
    coordinates = []
    alternate_fly = False
    for each_point in zip(boundry_point_1, boundry_point_2):
        if not alternate_fly:
            coordinates.extend(list(each_point))
        else:
            coordinates.extend(list(each_point[::-1]))
        alternate_fly = not alternate_fly
    return coordinates


def create_photo_counters_using_length_coords(data: SpacingBoundryPoints):
    final_coordinates = []
    length_coords = data.length_coordinates
    is_point_set_of_width = True
    for index in range(len(length_coords)-1):
        if is_point_set_of_width:
            points = get_trigger_cords_for_boundry(
                coords=[length_coords[index], length_coords[index+1]],
                points_required=data.width_required_points
            )
            for point in points:
                final_coordinates.append((point[0], point[1], data.top_view_height))
        is_point_set_of_width = not is_point_set_of_width

    return final_coordinates


def get_length_width_boundry_cords(coords, trigger_distance, spacing, top_view_height) -> SpacingBoundryPoints:
    point_data = check_first_two_poits_is_width(coords=coords)
    length_points_required = get_required_points_count(total_distance=point_data.length_distance,
                                                       trigger_distance=spacing)
    width_points_required = get_required_points_count(total_distance=point_data.width_distance,
                                                      trigger_distance=trigger_distance)
    print("lo", spacing)
    first_length_points_coords = get_trigger_cords_for_boundry(coords=point_data.length1_coords,
                                                               points_required=length_points_required.points_required)
    second_length_points_coords = get_trigger_cords_for_boundry(coords=point_data.length2_coords,
                                                                points_required=length_points_required.points_required)

    first_width_point_coords = get_trigger_cords_for_boundry(coords=point_data.width1_coords,
                                                             points_required=width_points_required.points_required)
    second_width_point_coords = get_trigger_cords_for_boundry(coords=point_data.width2_coords,
                                                              points_required=width_points_required.points_required)

    boundry_points = BoundryPoints(first_width_points=first_width_point_coords,
                                   first_length_points=first_length_points_coords,
                                   second_length_points=second_length_points_coords)

    length_coordinates = get_coordinates(boundry_point_1=boundry_points.first_length_points,
                                         boundry_point_2=boundry_points.second_length_points[::-1])
    width_coordinates = get_coordinates(first_width_point_coords, second_width_point_coords[::-1])
    length_spacing_boundry_points = SpacingBoundryPoints(length_coordinates=length_coordinates,
                                                         width_required_points=width_points_required.points_required,
                                                         top_view_height=top_view_height)

    width_spacing_boundry_points = SpacingBoundryPoints(length_coordinates=width_coordinates,
                                                        width_required_points=length_points_required.points_required,
                                                        top_view_height=top_view_height)
    final_coordinates = (create_photo_counters_using_length_coords(data=length_spacing_boundry_points) +
                         create_photo_counters_using_length_coords(data=width_spacing_boundry_points))
    return final_coordinates


def calculate_gsd(sensor_width, altitude, focal_length, image_width):
    gsd = (sensor_width * altitude) / (focal_length * image_width) * 100
    print(f"GSD (cm/pixel): {gsd}")
    return gsd


def flight_plan(coordinates, altitude, quality, sensor_width, focal_length, overlap_percentage,
                project_name, Image_width, Image_height):
    coords = []
    for location in coordinates:
        coords.append(tuple(location))
    image_width = Image_width
    image_height = Image_height
    gsd_width = calculate_gsd(sensor_width, altitude, focal_length, image_width)
    # gsd_height = calculate_gsd(sensor_width, altitude, focal_length, image_height)
    spacing = int((image_width * gsd_width * (1 - (overlap_percentage/100))) / 100)
    print("spacing2", spacing)
    trigger_distance = int((image_height * gsd_width * (1 - (overlap_percentage/100))) / 100)
    print("trigger", trigger_distance)
    top_view_height = altitude  # meter

    # Get today's date and time as project ID in 'YYYY-MM-DD-HH-MM-SS' format
    name = project_name

    points = get_length_width_boundry_cords(coords=coords, trigger_distance=trigger_distance,
                                            spacing=spacing, top_view_height=top_view_height)
    result = wpml_generator(points, name)
    result2 = generate_kml_file(name, points, height=top_view_height, top_view=True, point_label_count=1)
    result = {
        WPML_PATH: result,
        KML_PATH: result2
    }
    if result and result2:
        return result
    else:
        return "Failed to generate the file for the filght plan"
