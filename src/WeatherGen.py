from xml.dom import minidom
import os

def create_element_with_attributes(root, name, value="", unit=""):
    element = root.createElement(name)
    if value or unit:
        element.setAttribute("Value", value)
        element.setAttribute("Unit", unit)
    return element

def create_weather_preset_xml(params):
    root = minidom.Document()

    # Create the root element
    simbase_document = root.createElement('SimBase.Document')
    simbase_document.setAttribute('Type', 'WeatherPreset')
    simbase_document.setAttribute('version', '1,3')
    root.appendChild(simbase_document)

    # Add description
    descr = root.createElement('Descr')
    descr.appendChild(root.createTextNode('AceXML Document'))
    simbase_document.appendChild(descr)

    # Add WeatherPreset.Preset element
    weather_preset = root.createElement('WeatherPreset.Preset')
    simbase_document.appendChild(weather_preset)

    # Add parameters as child elements
    for param in params:
        if param in ['CloudLayer', 'WindLayer', 'GustWave']:
            element = root.createElement(param)
            for sub_param in params[param]:
                sub_element = root.createElement(sub_param)
                sub_element.appendChild(root.createTextNode(params[param][sub_param]))
                element.appendChild(sub_element)
            weather_preset.appendChild(element)
        else:
            element = root.createElement(param)
            element.appendChild(root.createTextNode(params[param]))
            weather_preset.appendChild(element)

    # Add elements with attributes
    weather_preset.appendChild(create_element_with_attributes(root, 'AerosolDensity', '8.000', 'density factor'))
    weather_preset.appendChild(create_element_with_attributes(root, 'Precipitations', '00.000', 'mm/h'))
    weather_preset.appendChild(create_element_with_attributes(root, 'ThunderstormIntensity', '0.0', '(0 - 1)'))

    # Add cloud layers, default values provided
    cloud_layers = [
        {
            'density': ('0.200', '(0 - 1)'),
            'bot': ('00600', 'm'),
            'top': ('00800', 'm'),
            'scatter': ('0.400', '(0 - 1)')
        },
        {
            'density': ('0.500', '(0 - 1)'),
            'bot': ('000700', 'm'),
            'top': ('001300', 'm'),
            'scatter': ('0.000', '(0 - 1)')
        },
        {
            'density': ('0.150', '(0 - 1)'),
            'bot': ('01300', 'm'),
            'top': ('04500', 'm'),
            'scatter': ('1.000', '(0 - 1)')
        }
    ]

    for layer in cloud_layers:
        cloud_layer = root.createElement('CloudLayer')
        cloud_layer.appendChild(create_element_with_attributes(root, 'CloudLayerDensity', *layer['density']))
        cloud_layer.appendChild(create_element_with_attributes(root, 'CloudLayerAltitudeBot', *layer['bot']))
        cloud_layer.appendChild(create_element_with_attributes(root, 'CloudLayerAltitudeTop', *layer['top']))
        cloud_layer.appendChild(create_element_with_attributes(root, 'CloudLayerScattering', *layer['scatter']))
        weather_preset.appendChild(cloud_layer)

    # Add wind layer
    wind_layer = root.createElement('WindLayer')
    wind_layer.appendChild(create_element_with_attributes(root, 'WindLayerAltitude', '1905', 'm'))
    wind_layer.appendChild(create_element_with_attributes(root, 'WindLayerAngle', '290', 'degrees'))
    wind_layer.appendChild(create_element_with_attributes(root, 'WindLayerSpeed', '2', 'knts'))
    weather_preset.appendChild(wind_layer)

    # Convert to pretty XML string
    xml_str = root.toprettyxml(indent="\t", encoding="UTF-8")

    # Save to file
    save_path_file = "Weather.wpr"  # Changed extension from .xml to .wpr
    with open(save_path_file, "wb") as f:  # Open in binary mode to write bytes
        f.write(xml_str)

# Define parameters
params = {
    'Name': 'Preset_Name_Here', # Name of the preset
    'Order': '', # Integer >= 9, optional
    'Image': '', # 332px * 105px JPG, optional
    'LayeredImage': '', # 694px * 248px PNG, optional
    'Icon': '', # 150px * 150px SVG, optional
    'IsAltitudeAMGL': '', # True or False, otherwise based on MSL, optional
    'CloudLayer': {
        'CloudLayerAltitudeBot': '',
        'CloudLayerAltitudeTop': '',
        'CloudLayerDensity': '',
        'CloudLayerScattering': ''
    },
    'WindLayer': {
        'WindLayerAltitude': '',
        'WindLayerAngle': '',
        'WindLayerSpeed': '',
        'GustWave': ''
    },
    'GustWave': {
        'GustWaveDuration': '',
        'GustWaveInterval': '',
        'GustWaveSpeed': '',
        'GustAngle': ''
    },
    'MSLPressure': '', # Sets the MSL pressure in Pa, 50000 <= value <= 130000, optional
    'MSLTemperature': '', # Sets the MSL temperature in K, K = C + 273.15, optional
    'AerosolDensity': '', # The aerosol density, default is 1, optional  
    'Precipitations': '', # The amount of precipitation in mm/h, 1.0 <= value <= 100.0, optional
    'PrecipitationType': '', # RAIN/SNOW/HAIL, optional
    'SnowCover': '', # The amount of snow cover in m, 0.0 <= value <= 4, optional
    'ThunderstormIntensity': '', # The intensity of the thunderstorm, 0.0 <= value <= 1.0, optional
    'ThunderstormCell': '',
    'Hurricane': '',
    'LoadingTip': ''
}

# Create the XML file
create_weather_preset_xml(params)