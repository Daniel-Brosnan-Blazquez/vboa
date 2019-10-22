var reports = [
    {% for report in reports %}
    {
        "id": "{{ report.report_uuid }}",
        "name": "{{ report.name }}",
        "report_group": "{{ report.reportGroup.name }}",
        "generation_mode": "{{ report.generation_mode }}",
        {% if report.validity_start == None %}
        "validity_start": "{{ report.triggering_time }}",
        {% else %}
        "validity_start": "{{ report.validity_start }}",
        {% endif %}
        {% if report.validity_stop == None %}
        "validity_stop": "{{ report.triggering_time }}",
        {% else %}
        "validity_stop": "{{ report.validity_stop }}",
        {% endif %}
        {% if report.triggering_time == None %}
        "triggering_time": "{{ report.triggering_time }}",
        {% else %}
        "triggering_time": "{{ report.triggering_time }}",
        {% endif %}
        {% if report.generation_start == None %}
        "generation_start": "{{ report.triggering_time }}",
        {% else %}
        "generation_start": "{{ report.generation_start }}",
        {% endif %}
        {% if report.generation_stop == None %}
        "generation_stop": "{{ report.triggering_time }}",
        {% else %}
        "generation_stop": "{{ report.generation_stop }}",
        {% endif %}
        {% if report.metadata_ingestion_duration == None %}
        "metadata_ingestion_duration": "0:00:00",
        {% else %}        
        "metadata_ingestion_duration": "{{ report.metadata_ingestion_duration }}",
        {% endif %}
        "generated": "{{ report.generated }}",
        "compressed": "{{ report.compressed }}",
        "generator": "{{ report.generator }}",
        "version": "{{ report.generator_version }}",
        "generation_error": "{{ report.generation_error }}"
    },
    {% endfor %}
]
