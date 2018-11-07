var sources = {
    "sources": [
        {% for source in sources %}
        {
            "id": "{{ source.processing_uuid }}",
            "name": "{{ source.name }}",
            "dim_signature": "{{ source.dimSignature.dim_signature }}",
            "processor": "{{ source.dimSignature.dim_exec_name }}",
            "version": "{{ source.dim_exec_version }}",
            "validity_start": "{{ source.validity_start }}",
            "validity_stop": "{{ source.validity_stop }}",
            "ingestion_time": "{{ source.ingestion_time }}",
            "ingestion_duration": "{{ source.ingestion_duration }}",
            "generation_time": "{{ source.generation_time }}",
            "number_of_events": "{{ source.events|list|length }}"
        },
        {% endfor %}
    ]
}
