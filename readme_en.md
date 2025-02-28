# backend_task_01

## Data
Two data recordings were carried out with our recording system. The recorded data (GPS track) is available in GeoJSON format. Our customers want to be able to evaluate the road condition of their roads at edge level. The recorded data (GPS tracks) must therefore be mapped to a road network (node-edge model). OpenStreetMap data (www.openstreetmap.org) is to be used as the basis for the road network.
Info: OSM data can be downloaded e.g. via Geofabrik Download Server or tools such as QuackOSM.

## Task 1
Determine the road network edges traveled on the basis of the recorded data and import the recorded data and the relevant edges of the OSM road network into a PostgreSQL database (PostGIS).
(One table for the recorded data and one table for the road network edges).

## Task 2
Map the recorded data to the road network. To do this, create a mapping table in which the mapping of an edge to a section of a GPS track is saved. A section is a part of a GPS track with consecutive GPS points:

| EdgeId _bigint_ | RecordingId _bigint_ | GPSIndexArray _bigint[]_ |
| -------- | ------- | ------- |
| 1  | 1 | [0, 1, 2, 3, 4] |
| 1 | 2 | [8, 9, 10, 11] |
| 2 | 1 | [5, 6, 7, 8, 9] |
| 3 | 1 | [10, 11, 12, 13, 14] |

## Task 3
Create an API with an endpoint that
- accepts a GeoJSON file with recorded data
- imports it into the database
- determines the relevant edges from OpenStreetMap and transfers them to the database,
- maps the edges

## Task 4
Create an endpoint which returns all GPS track sections as GeoJSON Features (LineString).