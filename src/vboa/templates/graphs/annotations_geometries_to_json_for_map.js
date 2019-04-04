var annotations_geometries = {
    "annotations_geometries": [
        {% for annotation_geometry in annotations_geometries %}
        {
            "id": "{{ annotation_geometry['annotation'].annotation_uuid }}",
            "annotation_cnf":{
                "name": "{{ annotation_geometry['annotation'].annotationCnf.name }}",
                "system": "{{ annotation_geometry['annotation'].annotationCnf.system }}",
                "description": "{{ annotation_geometry['annotation'].annotationCnf.description }}"
            },
            "explicit_reference": "{{ annotation_geometry['annotation'].explicitRef }}",
            "ingestion_time": "{{ annotation_geometry['annotation'].ingestion_time }}",
            "source": "{{ annotation_geometry['annotation'].source.name }}",
            "geometries": [
                {% for geometry in annotation_geometry["geometries"] %}
                {
                    "value": "{{ geometry['value'] }}",
                    "name": "{{ geometry['name'] }}"
                }
                {% endfor %}
            ]
        },
        {% endfor %}
    ]
}
