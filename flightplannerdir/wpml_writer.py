import io
import zipfile
from backend.s3_api import upload_flight_data_to_s3
global_speed = 4


def wpml_generator(points, name):
    zip_buffer = io.BytesIO()
    print("line 27")
    index = 0
    photo_count = 1
    initial_placemark = """      <Placemark>
            <Point>
            <coordinates>
                {},{}
            </coordinates>
            </Point>
            <wpml:index>{}</wpml:index>
            <wpml:executeHeight>{}</wpml:executeHeight>
            <wpml:waypointSpeed>{}</wpml:waypointSpeed>
            <wpml:waypointHeadingParam>
            <wpml:waypointHeadingMode>followWayline</wpml:waypointHeadingMode>
            </wpml:waypointHeadingParam>
            <wpml:waypointTurnParam>
            <wpml:waypointTurnMode>toPointAndStopWithDiscontinuityCurvature</wpml:waypointTurnMode>
            <wpml:waypointTurnDampingDist>0</wpml:waypointTurnDampingDist>
            </wpml:waypointTurnParam>
            <wpml:actionGroup>
            <wpml:actionGroupId>{}</wpml:actionGroupId>
            <wpml:actionGroupStartIndex>{}</wpml:actionGroupStartIndex>
            <wpml:actionGroupEndIndex>{}</wpml:actionGroupEndIndex>
            <wpml:actionGroupMode>sequence</wpml:actionGroupMode>
            <wpml:actionTrigger>
                <wpml:actionTriggerType>reachPoint</wpml:actionTriggerType>
            </wpml:actionTrigger>
            <wpml:action>
                <wpml:actionId>0</wpml:actionId>
                <wpml:actionActuatorFunc>gimbalRotate</wpml:actionActuatorFunc>
                <wpml:actionActuatorFuncParam>
                <wpml:gimbalHeadingYawBase>aircraft</wpml:gimbalHeadingYawBase>
                <wpml:gimbalRotateMode>absoluteAngle</wpml:gimbalRotateMode>
                <wpml:gimbalPitchRotateEnable>1</wpml:gimbalPitchRotateEnable>
                <wpml:gimbalPitchRotateAngle>-90</wpml:gimbalPitchRotateAngle>
                <wpml:gimbalRollRotateEnable>0</wpml:gimbalRollRotateEnable>
                <wpml:gimbalRollRotateAngle>0</wpml:gimbalRollRotateAngle>
                <wpml:gimbalYawRotateEnable>0</wpml:gimbalYawRotateEnable>
                <wpml:gimbalYawRotateAngle>0</wpml:gimbalYawRotateAngle>
                <wpml:gimbalRotateTimeEnable>0</wpml:gimbalRotateTimeEnable>
                <wpml:gimbalRotateTime>0</wpml:gimbalRotateTime>
                <wpml:payloadPositionIndex>0</wpml:payloadPositionIndex>
                </wpml:actionActuatorFuncParam>
            </wpml:action>
            <wpml:action>
                <wpml:actionId>1</wpml:actionId>
                <wpml:actionActuatorFunc>takePhoto</wpml:actionActuatorFunc>
                <wpml:actionActuatorFuncParam>
                <wpml:fileSuffix>point{}</wpml:fileSuffix>
                </wpml:actionActuatorFuncParam>
            </wpml:action>
            </wpml:actionGroup>
        </Placemark>
    """

    placemark = """      <Placemark>
            <Point>
            <coordinates>
                {},{}
            </coordinates>
            </Point>
            <wpml:index>{}</wpml:index>
            <wpml:executeHeight>{}</wpml:executeHeight>
            <wpml:waypointSpeed>{}</wpml:waypointSpeed>
            <wpml:waypointHeadingParam>
            <wpml:waypointHeadingMode>followWayline</wpml:waypointHeadingMode>
            </wpml:waypointHeadingParam>
            <wpml:waypointTurnParam>
            <wpml:waypointTurnMode>toPointAndStopWithDiscontinuityCurvature</wpml:waypointTurnMode>
            <wpml:waypointTurnDampingDist>0</wpml:waypointTurnDampingDist>
            </wpml:waypointTurnParam>
            <wpml:actionGroup>
            <wpml:actionGroupId>{}</wpml:actionGroupId>
            <wpml:actionGroupStartIndex>{}</wpml:actionGroupStartIndex>
            <wpml:actionGroupEndIndex>{}</wpml:actionGroupEndIndex>
            <wpml:actionGroupMode>sequence</wpml:actionGroupMode>
            <wpml:actionTrigger>
                <wpml:actionTriggerType>reachPoint</wpml:actionTriggerType>
            </wpml:actionTrigger>
            <wpml:action>
                <wpml:actionId>0</wpml:actionId>
                <wpml:actionActuatorFunc>takePhoto</wpml:actionActuatorFunc>
                <wpml:actionActuatorFuncParam>
                <wpml:fileSuffix>point{}</wpml:fileSuffix>
                </wpml:actionActuatorFuncParam>
            </wpml:action>
            </wpml:actionGroup>
        </Placemark>
    """

    wpml_file_initial = """<?xml version="1.0" encoding="UTF-8"?>
    <kml xmlns="http://www.opengis.net/kml/2.2" xmlns:wpml="http://www.dji.com/wpmz/1.0.2">
    <Document>
        <wpml:missionConfig>
        <wpml:flyToWaylineMode>safely</wpml:flyToWaylineMode>
        <wpml:finishAction>goHome</wpml:finishAction>
        <wpml:exitOnRCLost>executeLostAction</wpml:exitOnRCLost>
        <wpml:executeRCLostAction>goBack</wpml:executeRCLostAction>
        <wpml:globalTransitionalSpeed>{}</wpml:globalTransitionalSpeed>
        <wpml:droneInfo>
            <wpml:droneEnumValue>68</wpml:droneEnumValue>
            <wpml:droneSubEnumValue>0</wpml:droneSubEnumValue>
        </wpml:droneInfo>
        </wpml:missionConfig>
        <Folder>
        <wpml:templateId>0</wpml:templateId>
        <wpml:executeHeightMode>relativeToStartPoint</wpml:executeHeightMode>
        <wpml:waylineId>0</wpml:waylineId>
        <wpml:distance>0</wpml:distance>
        <wpml:duration>0</wpml:duration>
        <wpml:autoFlightSpeed>{}</wpml:autoFlightSpeed>
    """

    wpml_file_ending_lines = """    </Folder>
    </Document>
    </kml>"""

    # Split points into chunks of 200
    chunk_size = 200
    chunks = [points[i:i + chunk_size] for i in range(0, len(points), chunk_size)]
    with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zip_archive:
        for chunk_index, chunk in enumerate(chunks):
            wpml_file = wpml_file_initial.format(global_speed, global_speed)
            for point in chunk:
                longitude, latitude, altitude = point
                if index == 0:
                    wpml_file += initial_placemark.format(
                        round(float(longitude), 6), round(float(latitude), 6), index, altitude, global_speed, index,
                        index, index, photo_count
                    )
                else:
                    wpml_file += placemark.format(
                        round(float(longitude), 6), round(float(latitude), 6), index, altitude, global_speed, index,
                        index, index, photo_count
                    )
                index += 1
            wpml_file += wpml_file_ending_lines
            zip_archive.writestr(f"{name}/{name}_wpml_chunk_{chunk_index + 1}.wpml", wpml_file.encode('utf-8'))
    zip_buffer.seek(0)
    zip_file_name = f"{name}/{name}_wpml_files.zip"
    print("hello", type(zip_buffer))
    urls = upload_flight_data_to_s3(zip_buffer, zip_file_name)
    zip_buffer.close()
    return urls
