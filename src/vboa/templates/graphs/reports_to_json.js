var reports = [
    {% for report in reports %}
    {
        "id": "{{ report.report_uuid }}",
        "name": "{{ report.name }}",
        "report_group": "{{ report.reportGroup.name }}",
        "generation_mode": "{{ report.generation_mode }}",
        "validity_start": "{{ report.validity_start }}",
        "validity_stop": "{{ report.validity_stop }}",
        "triggering_time": "{{ report.triggering_time }}",
        "generation_start": "{{ report.generation_start }}",
        "generation_stop": "{{ report.generation_stop }}",
        "metadata_ingestion_duration": "{{ report.metadata_ingestion_duration }}",
        "generated": "{{ report.generated }}",
        "compressed": "{{ report.compressed }}",
        "generator": "{{ report.generator }}",
        "version": "{{ report.generator_version }}",
        "generation_error": "{{ report.generation_error }}"
    },
    {% endfor %}
]
