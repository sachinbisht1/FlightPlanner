import simplekml
import io
# Prepare a zip archive
# FastAPI imports
from backend import s3_api
from backend.s3_api import upload_flight_data_to_s3


def convert_to_long_lat_format(coords: list) -> list:
    return [(each_point[1], each_point[0]) for each_point in coords]


def generate_kml_file(name, points, height=0, top_view=True, point_label_count=1):
    file_name = f"{name}/{name}.kml"
    # points = remove_duplicate_points(points=points)
    points = convert_to_long_lat_format(coords=points)
    kml = simplekml.Kml()
    for each_point in points:
        if top_view:
            kml.newpoint(name=f"point-{point_label_count}", coords=[each_point + (height,)])  # lon, lat, optional
        else:
            kml.newpoint(name=f"point-{point_label_count}", coords=[each_point])  # lon, lat
        point_label_count += 1
    kml_string = kml.kml()
    kml_buffer = io.BytesIO(kml_string.encode('utf-8'))
    s3_url = upload_flight_data_to_s3(kml_buffer, file_name)
    if s3_url:
        preassigned_url = get_kml_file(file_name)
    return preassigned_url


def remove_duplicate_points(points):
    point_covered = []
    unique_points = []
    for each_point in points:
        if each_point not in point_covered:
            point_covered.append(each_point)
            unique_points.append(each_point)
    return unique_points


def get_kml_file(name):
    try:
        url = s3_api.get_flight_data_from_s3(name)
        return url
    except Exception as error:
        print(error)
        return "failed to fetch"
