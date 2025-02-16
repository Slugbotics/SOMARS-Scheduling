from xml.dom import minidom
import xml.etree.ElementTree as ET

def create_flight_plan(departure, destination, waypoints):
    # Create root element with correct attributes
    root = ET.Element("SimBase.Document")
    root.set("Type", "AceXML")
    root.set("version", "1,0")
    
    # Add description
    ET.SubElement(root, "Descr").text = "AceXML Document"
    
    # Create flight plan element
    flight_plan = ET.SubElement(root, "FlightPlan.FlightPlan")
    
    # Add basic flight information with comments
    title = ET.SubElement(flight_plan, "Title")
    title.text = f"{departure['icao']} to {destination['icao']}"
    title.append(ET.Comment(" Title of the flight plan, generally \"ICAO1 to ICAO2\"."))
    
    fp_type = ET.SubElement(flight_plan, "FPType")
    fp_type.text = "VFR"
    fp_type.append(ET.Comment(" Flight plan type "))
    
    cruising_alt = ET.SubElement(flight_plan, "CruisingAlt")
    cruising_alt.text = "00000"
    cruising_alt.append(ET.Comment(" Desired cruising altitude."))
    
    dep_id = ET.SubElement(flight_plan, "DepartureID")
    dep_id.text = departure['icao']
    dep_id.append(ET.Comment(" Departure ICAO."))
    
    dep_lla = ET.SubElement(flight_plan, "DepartureLLA")
    dep_lla.text = departure['position']
    dep_lla.append(ET.Comment(" Departure coordinates Lat,Long,Alt."))
    
    dest_id = ET.SubElement(flight_plan, "DestinationID")
    dest_id.text = destination['icao']
    dest_id.append(ET.Comment(" Arrival ICAO."))
    
    dest_lla = ET.SubElement(flight_plan, "DestinationLLA")
    dest_lla.text = destination['position']
    dest_lla.append(ET.Comment(" Arrival coordinates Lt,long,alt."))
    
    descr = ET.SubElement(flight_plan, "Descr")
    descr.text = f"{departure['icao']} to {destination['icao']}"
    descr.append(ET.Comment(" ICAO1 to ICAO2."))
    
    dep_pos = ET.SubElement(flight_plan, "DeparturePosition")
    dep_pos.text = ""
    dep_pos.append(ET.Comment(" Departure Runway Number."))
    
    dep_name = ET.SubElement(flight_plan, "DepartureName")
    dep_name.text = departure['name']
    dep_name.append(ET.Comment(" Departure Airport Name."))
    
    dest_name = ET.SubElement(flight_plan, "DestinationName")
    dest_name.text = destination['name']
    dest_name.append(ET.Comment(" Arribal Airport Name."))
    
    # Add app version
    app_version = ET.SubElement(flight_plan, "AppVersion")
    ET.SubElement(app_version, "AppVersionMajor").text = "11"
    ET.SubElement(app_version, "AppVersionBuild").text = "282174"
    
    # Add waypoints
    for wp in waypoints:
        waypoint = ET.SubElement(flight_plan, "ATCWaypoint")
        waypoint.set("id", wp['id'])
        ET.SubElement(waypoint, "ATCWaypointType").text = wp['type']
        ET.SubElement(waypoint, "WorldPosition").text = wp['position']
        
        if wp['type'] == 'Airport':
            icao = ET.SubElement(waypoint, "ICAO")
            ET.SubElement(icao, "ICAOIdent").text = wp['id']
    
    return root

def save_flight_plan(root, filename):
    # Convert to string and pretty print
    xml_str = minidom.parseString(ET.tostring(root)).toprettyxml(indent="    ")
    
    # Add XML declaration with encoding
    if not xml_str.startswith('<?xml'):
        xml_str = '<?xml version="1.0" encoding="UTF-8"?>\n' + xml_str
    
    # Write to file
    with open(filename, 'w', encoding='utf-8') as f:
        f.write(xml_str)

def main():
    # Define airports
    departure = {
        'icao': 'KVNY',
        'name': 'Van Nuys',
        'position': 'N34° 12\' 36.57",W118° 29\' 24.03",+000775.50'
    }
    
    destination = {
        'icao': 'KBUR',
        'name': 'Bob Hope',
        'position': 'N34° 12\' 2.24",W118° 21\' 30.61",+000722.50'
    }
    
    # Define waypoints, defaults provided.
    waypoints = [
        {
            'id': 'KVNY',
            'type': 'Airport',
            'position': departure['position']
        },
        {
            'id': 'CUST0',
            'type': 'User',
            'position': 'N34° 13\' 16.8",W118° 28\' 46",+001000.00'
        },
        {
            'id': 'CUST1',
            'type': 'User',
            'position': 'N34° 13\' 10",W118° 24\' 14",+001000.00'
        },
        {
            'id': 'KBUR',
            'type': 'Airport',
            'position': destination['position']
        }
    ]
    
    # Create and save flight plan
    root = create_flight_plan(departure, destination, waypoints)
    save_flight_plan(root, 'flightplan.pln')

if __name__ == "__main__":
    main()