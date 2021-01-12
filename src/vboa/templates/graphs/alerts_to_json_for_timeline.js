var alerts = [];
{% if sources_alerts|length > 0 %}
var sources_alerts = [
    {% for alert in sources_alerts %}
    {% set severity_label=alert.alertDefinition.severity|get_severity_label %}
    {
        "id": "{{ alert.source_alert_uuid }}",
        "name": "{{ alert.alertDefinition.name }}",
        "severity": "{{ severity_label }}",
        "description": "{{ alert.alertDefinition.description }}",
        "message": "{{ alert.message }}",
        "validated": "{{ alert.generator }}",
        "ingestion_time": "{{ alert.ingestion_time }}",
        "generator": "{{ alert.generator }}",
        "notified": "{{ alert.notified }}",
        "solved": "{{ alert.solved }}",
        "solved_time": "{{ alert.solved_time }}",
        "notification_time": "{{ alert.notification_time.isoformat() }}",
        "justification": "{{ alert.justification }}",
        "alert_uuid": "{{ alert.alert_uuid }}",
        "source_uuid": "{{ alert.source_uuid }}",
        "group": "{{ alert.alertDefinition.group.name }}",
        "group_uuid": "{{ alert.alertDefinition.group.alert_group_uuid }}",
        "entity": "SOURCES"
    },
    {% endfor %}
]
alerts = alerts.concat(sources_alerts)
{% endif %}
{% if events_alerts|length > 0 %}
var events_alerts = [
    {% for alert in events_alerts %}
    {% set severity_label=alert.alertDefinition.severity|get_severity_label %}
    {
        "id": "{{ alert.event_alert_uuid }}",
        "name": "{{ alert.alertDefinition.name }}",
        "severity": "{{ severity_label }}",
        "description": "{{ alert.alertDefinition.description }}",
        "message": "{{ alert.message }}",
        "validated": "{{ alert.generator }}",
        "ingestion_time": "{{ alert.ingestion_time }}",
        "generator": "{{ alert.generator }}",
        "notified": "{{ alert.notified }}",
        "solved": "{{ alert.solved }}",
        "solved_time": "{{ alert.solved_time }}",
        "notification_time": "{{ alert.notification_time.isoformat() }}",
        "justification": "{{ alert.justification }}",
        "alert_uuid": "{{ alert.alert_uuid }}",
        "event_uuid": "{{ alert.event_uuid }}",
        "group": "{{ alert.alertDefinition.group.name }}",
        "group_uuid": "{{ alert.alertDefinition.group.alert_group_uuid }}",
        "entity": "EVENTS"
    },
    {% endfor %}
]
alerts = alerts.concat(events_alerts)
{% endif %}
{% if annotations_alerts|length > 0 %}
var annotations_alerts = [
    {% for alert in annotations_alerts %}
    {% set severity_label=alert.alertDefinition.severity|get_severity_label %}
    {
        "id": "{{ alert.annotation_alert_uuid }}",
        "name": "{{ alert.alertDefinition.name }}",
        "severity": "{{ severity_label }}",
        "description": "{{ alert.alertDefinition.description }}",
        "message": "{{ alert.message }}",
        "validated": "{{ alert.generator }}",
        "ingestion_time": "{{ alert.ingestion_time }}",
        "generator": "{{ alert.generator }}",
        "notified": "{{ alert.notified }}",
        "solved": "{{ alert.solved }}",
        "solved_time": "{{ alert.solved_time }}",
        "notification_time": "{{ alert.notification_time.isoformat() }}",
        "justification": "{{ alert.justification }}",
        "alert_uuid": "{{ alert.alert_uuid }}",
        "annotation_uuid": "{{ alert.annotation_uuid }}",
        "group": "{{ alert.alertDefinition.group.name }}",
        "group_uuid": "{{ alert.alertDefinition.group.alert_group_uuid }}",
        "entity": "ANNOTATIONS"   
    },
    {% endfor %}
]
alerts = alerts.concat(annotations_alerts)
{% endif %}
{% if reports_alerts|length > 0 %}
var reports_alerts = [
    {% for alert in reports_alerts %}
    {% set severity_label=alert.alertDefinition.severity|get_severity_label %}
    {
        "id": "{{ alert.report_alert_uuid }}",
        "name": "{{ alert.alertDefinition.name }}",
        "severity": "{{ severity_label }}",
        "description": "{{ alert.alertDefinition.description }}",
        "message": "{{ alert.message }}",
        "validated": "{{ alert.generator }}",
        "ingestion_time": "{{ alert.ingestion_time }}",
        "generator": "{{ alert.generator }}",
        "notified": "{{ alert.notified }}",
        "solved": "{{ alert.solved }}",
        "solved_time": "{{ alert.solved_time }}",
        "notification_time": "{{ alert.notification_time.isoformat() }}",
        "justification": "{{ alert.justification }}",
        "alert_uuid": "{{ alert.alert_uuid }}",
        "report_uuid": "{{ alert.report_uuid }}",
        "group": "{{ alert.alertDefinition.group.name }}",
        "group_uuid": "{{ alert.alertDefinition.group.alert_group_uuid }}",
        "entity": "REPORTS"     
    },
    {% endfor %}
]
alerts = alerts.concat(reports_alerts)
{% endif %}
{% if ers_alerts|length > 0 %}
var ers_alerts = [
    {% for alert in ers_alerts %}
    {% set severity_label=alert.alertDefinition.severity|get_severity_label %}
    {
        "id": "{{ alert.explicit_ref_alert_uuid }}",
        "name": "{{ alert.alertDefinition.name }}",
        "severity": "{{ severity_label }}",
        "description": "{{ alert.alertDefinition.description }}",
        "message": "{{ alert.message }}",
        "validated": "{{ alert.generator }}",
        "ingestion_time": "{{ alert.ingestion_time }}",
        "generator": "{{ alert.generator }}",
        "notified": "{{ alert.notified }}",
        "solved": "{{ alert.solved }}",
        "solved_time": "{{ alert.solved_time }}",
        "notification_time": "{{ alert.notification_time.isoformat() }}",
        "justification": "{{ alert.justification }}",
        "alert_uuid": "{{ alert.alert_uuid }}",
        "explicit_ref_uuid": "{{ alert.explicit_ref_uuid }}",
        "group": "{{ alert.alertDefinition.group.name }}",
        "group_uuid": "{{ alert.alertDefinition.group.alert_group_uuid }}",
        "entity": "EXPLICIT REFERENCES"     
    },
    {% endfor %}
]
alerts = alerts.concat(ers_alerts)
{% endif %}