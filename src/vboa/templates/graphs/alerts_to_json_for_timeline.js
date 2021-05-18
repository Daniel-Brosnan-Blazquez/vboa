var alerts = [];
{% if source_alerts|length > 0 %}
var source_alerts = [
    {% for alert in source_alerts %}
    {% if alert.solved == "True" %}
    {% set solved_class="bold-red" %}
    {% else %}
    {% set solved_class="bold-orange" %}
    {% endif %}
    {% if alert.notified == "True" %}
    {% set notified_class="bold-red" %}
    {% else %}
    {% set notified_class="bold-orange" %}
    {% endif %}
    {% if alert.validated == "True" %}
    {% set validated_class="bold-red" %}
    {% else %}
    {% set validated_class="bold-orange" %}
    {% endif %}
    {% if alert.solved_time == None %}
    {% set solved_time = alert.solved_time %}
    {% else %}
    {% set solved_time = alert.solved_time.isoformat() %}
    {% endif %}
    {% set severity_label=alert.alertDefinition.severity|get_severity_label %}
    {
        "id": "{{ alert.source_alert_uuid }}",
        "name": "{{ alert.alertDefinition.name }}",
        "severity": "{{ severity_label }}",
        "description": "{{ alert.alertDefinition.description }}",
        "message": "{{ alert.message }}",
        "validated": "<span class='" + "{{ validated_class }}" + "'>" + "{{ alert.validated }}" + "</span>",
        "ingestion_time": "{{ alert.ingestion_time.isoformat() }}",
        "generator": "{{ alert.generator }}",
        "notified": "<span class='" + "{{ notified_class }}" + "'>" + "{{ alert.notified }}" + "</span>" ,
        "solved": "<span class='" + "{{ solved_class }}" + "'>" + "{{ alert.solved }}" + "</span>",
        "solved_time": "{{ solved_time }}",
        "notification_time": "{{ alert.notification_time.isoformat() }}",
        "justification": "{{ alert.justification }}",
        "alert_uuid": "<a href='/eboa_nav/query-alert/" + "{{ alert.source_alert_uuid }}" + "'>" + "{{ alert.source_alert_uuid }}" + "</a>",
        "entity_uuid": "<a href='/eboa_nav/query-source/" + "{{ alert.source_uuid }}" + "'>" + "{{ alert.source_uuid }}" + "</a>",
        "group_alert": "{{ alert.alertDefinition.group.name }}",
        "entity": "Source",
        "group": "SOURCES;{{ alert.alertDefinition.group.name }}",
        "timeline": "{{ alert.alertDefinition.name }}",
        "start": "{{ alert.notification_time.isoformat() }}",
        "stop": "{{ alert.notification_time.isoformat() }}",
    },
    {% endfor %}
]
alerts = alerts.concat(source_alerts)
{% endif %}
{% if event_alerts|length > 0 %}
var event_alerts = [
    {% for alert in event_alerts %}
    {% if alert.solved == "True" %}
    {% set solved_class="bold-red" %}
    {% else %}
    {% set solved_class="bold-orange" %}
    {% endif %}
    {% if alert.notified == "True" %}
    {% set notified_class="bold-red" %}
    {% else %}
    {% set notified_class="bold-orange" %}
    {% endif %}
    {% if alert.validated == "True" %}
    {% set validated_class="bold-red" %}
    {% else %}
    {% set validated_class="bold-orange" %}
    {% endif %}
    {% if alert.solved_time == None %}
    {% set solved_time = alert.solved_time %}
    {% else %}
    {% set solved_time = alert.solved_time.isoformat() %}
    {% endif %}
    {% set severity_label=alert.alertDefinition.severity|get_severity_label %}
    {
        "id": "{{ alert.event_alert_uuid }}",
        "name": "{{ alert.alertDefinition.name }}",
        "severity": "{{ severity_label }}",
        "description": "{{ alert.alertDefinition.description }}",
        "message": "{{ alert.message }}",
        "validated": "<span class='" + "{{ validated_class }}" + "'>" + "{{ alert.validated }}" + "</span>",
        "ingestion_time": "{{ alert.ingestion_time.isoformat() }}",
        "generator": "{{ alert.generator }}",
        "notified": "<span class='" + "{{ notified_class }}" + "'>" + "{{ alert.notified }}" + "</span>" ,
        "solved": "<span class='" + "{{ solved_class }}" + "'>" + "{{ alert.solved }}" + "</span>",
        "solved_time": "{{ solved_time }}",
        "notification_time": "{{ alert.notification_time.isoformat() }}",
        "justification": "{{ alert.justification }}",
        "alert_uuid": "<a href='/eboa_nav/query-alert/" + "{{ alert.event_alert_uuid }}" + "'>" + "{{ alert.event_alert_uuid }}" + "</a>",
        "entity_uuid": "<a href='/eboa_nav/query-event-links/" + "{{ alert.event_uuid }}" + "'>" + "{{ alert.event_uuid }}" + "</a>",
        "group_alert": "{{ alert.alertDefinition.group.name }}",
        "entity": "Event",
        "group": "EVENTS;{{ alert.alertDefinition.group.name }}",
        "timeline": "{{ alert.alertDefinition.name }}",
        "start": "{{ alert.notification_time.isoformat() }}",
        "stop": "{{ alert.notification_time.isoformat() }}",
    },
    {% endfor %}
]
alerts = alerts.concat(event_alerts)
{% endif %}
{% if annotation_alerts|length > 0 %}
var annotation_alerts = [
    {% for alert in annotation_alerts %}
    {% if alert.solved == "True" %}
    {% set solved_class="bold-red" %}
    {% else %}
    {% set solved_class="bold-orange" %}
    {% endif %}
    {% if alert.notified == "True" %}
    {% set notified_class="bold-red" %}
    {% else %}
    {% set notified_class="bold-orange" %}
    {% endif %}
    {% if alert.validated == "True" %}
    {% set validated_class="bold-red" %}
    {% else %}
    {% set validated_class="bold-orange" %}
    {% endif %}
    {% if alert.solved_time == None %}
    {% set solved_time = alert.solved_time %}
    {% else %}
    {% set solved_time = alert.solved_time.isoformat() %}
    {% endif %}
    {% set severity_label=alert.alertDefinition.severity|get_severity_label %}
    {
        "id": "{{ alert.annotation_alert_uuid }}",
        "name": "{{ alert.alertDefinition.name }}",
        "severity": "{{ severity_label }}",
        "description": "{{ alert.alertDefinition.description }}",
        "message": "{{ alert.message }}",
        "validated": "<span class='" + "{{ validated_class }}" + "'>" + "{{ alert.validated }}" + "</span>",
        "ingestion_time": "{{ alert.ingestion_time.isoformat() }}",
        "generator": "{{ alert.generator }}",
        "notified": "<span class='" + "{{ notified_class }}" + "'>" + "{{ alert.notified }}" + "</span>" ,
        "solved": "<span class='" + "{{ solved_class }}" + "'>" + "{{ alert.solved }}" + "</span>",
        "solved_time": "{{ solved_time }}",
        "notification_time": "{{ alert.notification_time.isoformat() }}",
        "justification": "{{ alert.justification }}",
        "alert_uuid": "<a href='/eboa_nav/query-alert/" + "{{ alert.annotation_alert_uuid }}" + "'>" + "{{ alert.annotation_alert_uuid }}" + "</a>",
        "entity_uuid": "<a href='/eboa_nav/query-annotation/" + "{{ alert.annotation_uuid }}" + "'>" + "{{ alert.annotation_uuid }}" + "</a>",
        "group_alert": "{{ alert.alertDefinition.group.name }}",
        "entity": "Annotation",
        "group": "ANNOTATIONS;{{ alert.alertDefinition.group.name }}",
        "timeline": "{{ alert.alertDefinition.name }}",
        "start": "{{ alert.notification_time.isoformat() }}",
        "stop": "{{ alert.notification_time.isoformat() }}", 
    },
    {% endfor %}
]
alerts = alerts.concat(annotation_alerts)
{% endif %}
{% if report_alerts|length > 0 %}
var report_alerts = [
    {% for alert in report_alerts %}
    {% if alert.solved == "True" %}
    {% set solved_class="bold-red" %}
    {% else %}
    {% set solved_class="bold-orange" %}
    {% endif %}
    {% if alert.notified == "True" %}
    {% set notified_class="bold-red" %}
    {% else %}
    {% set notified_class="bold-orange" %}
    {% endif %}
    {% if alert.validated == "True" %}
    {% set validated_class="bold-red" %}
    {% else %}
    {% set validated_class="bold-orange" %}
    {% endif %}
    {% if alert.solved_time == None %}
    {% set solved_time = alert.solved_time %}
    {% else %}
    {% set solved_time = alert.solved_time.isoformat() %}
    {% endif %}
    {% set severity_label=alert.alertDefinition.severity|get_severity_label %}
    {
        "id": "{{ alert.report_alert_uuid }}",
        "name": "{{ alert.alertDefinition.name }}",
        "severity": "{{ severity_label }}",
        "description": "{{ alert.alertDefinition.description }}",
        "message": "{{ alert.message }}",
        "validated": "<span class='" + "{{ validated_class }}" + "'>" + "{{ alert.validated }}" + "</span>",
        "ingestion_time": "{{ alert.ingestion_time.isoformat() }}",
        "generator": "{{ alert.generator }}",
        "notified": "<span class='" + "{{ notified_class }}" + "'>" + "{{ alert.notified }}" + "</span>" ,
        "solved": "<span class='" + "{{ solved_class }}" + "'>" + "{{ alert.solved }}" + "</span>",
        "solved_time": "{{ solved_time }}",
        "notification_time": "{{ alert.notification_time.isoformat() }}",
        "justification": "{{ alert.justification }}",
        "alert_uuid": "<a href='/rboa_nav/query-alert/" + "{{ alert.report_alert_uuid }}" + "'>" + "{{ alert.report_alert_uuid }}" + "</a>",
        "entity_uuid": "<a href='/rboa_nav/query-report/" + "{{ alert.report_uuid }}" + "'>" + "{{ alert.report_uuid }}" + "</a>",
        "group_alert": "{{ alert.alertDefinition.group.name }}",
        "entity": "Report",
        "group": "REPORTS;{{ alert.alertDefinition.group.name }}",
        "timeline": "{{ alert.alertDefinition.name }}",
        "start": "{{ alert.notification_time.isoformat() }}",
        "stop": "{{ alert.notification_time.isoformat() }}",    
    },
    {% endfor %}
]
alerts = alerts.concat(report_alerts)
{% endif %}
{% if er_alerts|length > 0 %}
var er_alerts = [
    {% for alert in er_alerts %}
    {% if alert.solved == "True" %}
    {% set solved_class="bold-red" %}
    {% else %}
    {% set solved_class="bold-orange" %}
    {% endif %}
    {% if alert.notified == "True" %}
    {% set notified_class="bold-red" %}
    {% else %}
    {% set notified_class="bold-orange" %}
    {% endif %}
    {% if alert.validated == "True" %}
    {% set validated_class="bold-red" %}
    {% else %}
    {% set validated_class="bold-orange" %}
    {% endif %}
    {% if alert.solved_time == None %}
    {% set solved_time = alert.solved_time %}
    {% else %}
    {% set solved_time = alert.solved_time.isoformat() %}
    {% endif %}
    {% set severity_label=alert.alertDefinition.severity|get_severity_label %}
    {
        "id": "{{ alert.explicit_ref_alert_uuid }}",
        "name": "{{ alert.alertDefinition.name }}",
        "severity": "{{ severity_label }}",
        "description": "{{ alert.alertDefinition.description }}",
        "message": "{{ alert.message }}",
        "validated": "<span class='" + "{{ validated_class }}" + "'>" + "{{ alert.validated }}" + "</span>",
        "ingestion_time": "{{ alert.ingestion_time.isoformat() }}",
        "generator": "{{ alert.generator }}",
        "notified": "<span class='" + "{{ notified_class }}" + "'>" + "{{ alert.notified }}" + "</span>" ,
        "solved": "<span class='" + "{{ solved_class }}" + "'>" + "{{ alert.solved }}" + "</span>",
        "solved_time": "{{ solved_time }}",
        "notification_time": "{{ alert.notification_time.isoformat() }}",
        "justification": "{{ alert.justification }}",
        "alert_uuid": "<a href='/eboa_nav/query-alert/" + "{{ alert.explicit_ref_alert_uuid }}" + "'>" + "{{ alert.explicit_ref_alert_uuid }}" + "</a>",
        "entity_uuid": "<a href='/eboa_nav/query-er/" + "{{ alert.explicit_ref_uuid }}" + "'>" + "{{ alert.explicit_ref_uuid }}" + "</a>",
        "group_alert": "{{ alert.alertDefinition.group.name }}",
        "entity": "Explicit reference",
        "group": "EXPLICIT_REFERENCES;{{ alert.alertDefinition.group.name }}",
        "timeline": "{{ alert.alertDefinition.name }}",
        "start": "{{ alert.notification_time.isoformat() }}",
        "stop": "{{ alert.notification_time.isoformat() }}",    
    },
    {% endfor %}
]
alerts = alerts.concat(er_alerts)
{% endif %}