# Procesamiento de la información obtenida durante el mapatón xalap

Aquí está concentrada (y parcialmente procesada) la información de los camiones que se obtuvo durante el mapatón organizado por @codeandoxalapa y el ayuntamiento.

Dentro de la carpeta `data/` se encuentran los _shapefiles_ originales aunque un poco mejor organizados. Principalmente se trabaja en normalizar la estructura de carpetas.

## Scripts de procesamiento

### Extracción

Lo primero que se hizo fue extraer todos los archivos contenidos en archivadores `zip` distribuidos a lo largo de las carpetas usando el comando `organize.py uncompress`.

### Conversión

El mismo programa es capaz de convertir cualquier archivo shapefile a GEOJson usando `organize.py convert`. Se usó el programa `ogr2ogr` internamente para esta operación. Específicamente la línea de comandos `ogr2ogr -f geoJSON output.geojson input.shp`.

### Procesamiento de las paradas

En los datos crudos cada parada aparece una vez por cada ruta distinta que se mapeó y que paraba ahí, así que la mayoría están multiplicadas. Para esto se crearon dos **tareas** que ayudan a organizarlas. La primera `organize.py extractstops` que se encarga de revisar los más de 120 archivos de paradas y cargarlos a una base de datos en redis, y la segunda `organize.py dumpstops` que corre un algoritmo bastante piojo de clusterización que reduce de 11,000 paradas a solo ~2,500

### Trabajo futuro

Como las rutas están todas chuecas se les hará pasar por un algoritmo de corrección y por una apropiada clasificación para identificarlas.
