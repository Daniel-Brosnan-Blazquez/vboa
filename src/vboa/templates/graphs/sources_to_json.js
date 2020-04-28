var sources = [
    {% for source in sources %}
    {
        "id": "{{ source.source_uuid }}",
        "name": "{{ source.name }}",
        "dim_signature": "{{ source.dimSignature.dim_signature }}",
        "processor": "{{ source.processor }}",
        "version": "{{ source.processor_version }}",
        {% if source.validity_start == None %}
        "validity_start": "{{ source.generation_time.isoformat() }}",
        {% else %}
        "validity_start": "{{ source.validity_start.isoformat() }}",
        {% endif %}
        {% if source.validity_stop == None %}
        "validity_stop": "{{ source.generation_time.isoformat() }}",
        {% else %}
        "validity_stop": "{{ source.validity_stop.isoformat() }}",
        {% endif %}
        {% if source.ingestion_time == None %}
        "ingestion_time": "{{ source.generation_time.isoformat() }}",
        {% else %}
        "ingestion_time": "{{ source.ingestion_time.isoformat() }}",
        {% endif %}
        {% if source.ingestion_duration == None %}
        "ingestion_duration": "0:00:00",
        {% else %}        
        "ingestion_duration": "{{ source.ingestion_duration }}",
        {% endif %}
        "generation_time": "{{ source.generation_time.isoformat() }}",
        "number_of_events": "{{ source.events|list|length }}",
        "ingestion_error": "{{ source.ingestion_error }}"
    },
    {% endfor %}
]
