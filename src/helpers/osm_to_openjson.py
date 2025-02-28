import json

def overpass_to_geojson(overpass_json):
    geojson = {
        "type": "FeatureCollection",
        "features": []
    }

    elements = overpass_json.get("elements", [])
    
    for elem in elements:
        if elem["type"] == "node":
            feature = {
                "type": "Feature",
                "geometry": {
                    "type": "Point",
                    "coordinates": [elem["lon"], elem["lat"]]
                },
                "properties": elem.get("tags", {})
            }
            geojson["features"].append(feature)
        elif elem["type"] == "way":
            coords = [[node["lon"], node["lat"]] for node in elem.get("geometry", []) if "lat" in node and "lon" in node]
            if coords:
                feature = {
                    "type": "Feature",
                    "geometry": {
                        "type": "LineString",
                        "coordinates": coords
                    },
                    "properties": elem.get("tags", {})
                }
                geojson["features"].append(feature)

    return geojson

# Load Overpass JSON and convert to GeoJSON
with open("OSM-Straßennetzes_Befahrung2.json", "r", encoding="utf-8") as f:
    overpass_json = json.load(f)

geojson_data = overpass_to_geojson(overpass_json)

# Save as GeoJSON
with open("converted.geojson", "w", encoding="utf-8") as f:
    json.dump(geojson_data, f, indent=2)

print("Converted GeoJSON saved as 'converted.geojson'. You can open it in geojson.io.")
