# backend_task_01

## Datengrundlage
Mit unserem Aufnahmesystem wurden zwei Befahrungen durchgeführt. Die Befahrungsdaten liegen im GeoJSON-Format vor. Unsere Kunden möchten den Straßenzustand auf Kantenebene auswerten können. Die Befahrungsdaten (GPS-Tracks) müssen daher einem Straßennetz (Knoten-Kanten-Modell) zugeordnet werden. Als Grundlage für das Straßennetz soll OpenStreetMap (www.openstreetmap.org) verwendet werden.
Info: der Download von OSM-Daten ist z.B. über Geofabrik Download Server oder Tools wie QuackOSM möglich.

## Aufgabe 1
Ermittle auf Grundlage der Befahrungsdaten die abgefahrenen Netzbereiche und importiere die Befahrungsdaten und die relevanten Kanten des OSM-Straßennetzes in eine PostgreSQL-DB (PostGIS).
(Eine Tabelle für die Befahrungen sowie eine Tabelle für die Kanten).

## Aufgabe 2
Ordne die Befahrungsdaten dem Straßennetz zu. Erstelle hierzu eine Mapping-Tabelle in der die Zuordnung von Kante zu Befahrungsabschnitt gespeichert ist. Ein Befahrungsabschnitt ist ein Teil einer Befahrung mit aufeinanderfolgenden GPS-Punkten:

| KanteId _bigint_ | BefahrungId _bigint_ | GPSIndexArray _bigint[]_ |
| -------- | ------- | ------- |
| 1  | 1 | [0, 1, 2, 3, 4] |
| 1 | 2 | [8, 9, 10, 11] |
| 2 | 1 | [5, 6, 7, 8, 9] |
| 3 | 1 | [10, 11, 12, 13, 14] |

## Aufgabe 3
Erstelle eine API mit einem Endpunkt der
- eine Befahrungsdatei (GeoJSON) entgegen nimmt,
- diese in die Datenbank importiert,
- die relevanten Kanten aus OpenStreetMap ermittelt und in die Datenbank übernimmt,
- die Zuordnung der Kanten durchführt

## Aufgabe 4
Erstelle eine API mit einem Endpunkt der alle Befahrungsabschnitte als GeoJSON (Linestring) zurückliefert.