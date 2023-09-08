var sources = [
    {% for source_uuid in source_uuids %}
    {% set source = data["sources"][source_uuid] %}
    {
        "id": "{{ source['source_uuid'] }}",
        "name": "{{ source['name'] }}",
        "dim_signature": "{{ source['dim_signature'] }}",
        "processor": "{{ source['processor'] }}",
        "version": "{{ source['processor_version'] }}",
        {% if source['validity_start'] == None %}
        "validity_start": "{{ source['generation_time'] }}",
        {% else %}
        "validity_start": "{{ source['validity_start'] }}",
        {% endif %}
        {% if source['validity_stop'] == None %}
        "validity_stop": "{{ source['generation_time'] }}",
        {% else %}
        "validity_stop": "{{ source['validity_stop'] }}",
        {% endif %}
        {% if source['reported_validity_start'] == None %}
        "reported_validity_start": "{{ source['reported_generation_time'] }}",
        {% else %}
        "reported_validity_start": "{{ source['reported_validity_start'] }}",
        {% endif %}
        {% if source['reported_validity_stop'] == None %}
        "reported_validity_stop": "{{ source['reported_generation_time'] }}",
        {% else %}
        "reported_validity_stop": "{{ source['reported_validity_stop'] }}",
        {% endif %}
        {% if source['reception_time'] == None %}
        "reception_time": "{{ source['generation_time'] }}",
        {% else %}
        "reception_time": "{{ source['reception_time'] }}",
        {% endif %}
        {% if source['ingestion_time'] == None %}
        "ingestion_time": "{{ source['generation_time'] }}",
        {% else %}
        "ingestion_time": "{{ source['ingestion_time'] }}",
        {% endif %}
        {% if source['processing_duration'] == None %}
        "processing_duration": "0:00:00",
        {% else %}        
        "processing_duration": "{{ source['processing_duration'] }}",
        {% endif %}
        {% if source['ingestion_duration'] == None %}
        "ingestion_duration": "0:00:00",
        {% else %}        
        "ingestion_duration": "{{ source['ingestion_duration'] }}",
        {% endif %}
        "generation_time": "{{ source['generation_time'] }}",
        "reported_generation_time": "{{ source['reported_generation_time'] }}",
        "number_of_events": "{{ source['number_of_events'] }}",
        "number_of_annotations": "{{ source['number_of_annotations'] }}",
        "priority": "{{ source['priority'] }}",
        "ingestion_completeness": "{{ source['ingestion_completeness'] }}",
        "ingestion_completeness_message": "{{ source['ingestion_completeness_message'] }}",
        "ingestion_error": "{{ source['ingestion_error'] }}"
    },
    {% endfor %}
]
