
var events = [
    {% for event in events %}
    {% set memory_usage = event.eventDoubles|selectattr("name", "equalto", "memory_usage_percentage")|first|attr("value") %}
    {% set memory_buffers_percentage = event.eventDoubles|selectattr("name", "equalto", "memory_buffers_percentage")|first|attr("value") %}
    {% set memory_cached_percentage = event.eventDoubles|selectattr("name", "equalto", "memory_cached_percentage")|first|attr("value") %}

    {% set swap_usage = event.eventDoubles|selectattr("name", "equalto", "swap_usage_percentage")|first|attr("value") %}
    {
        "id": "{{ event.event_uuid }}-memory-usage",
        "group": "memory_usage",
        "x": "{{ event.start.isoformat() }}",
        "y": "{{ memory_usage }}",
        "tooltip": "<table border='1'>" +
            "<tr><td>Group</td><td>Memory usage</td>" +
            "<tr><td>Notification time</td><td>{{ event.start.isoformat() }}</td>" +
            "<tr><td>Value</td><td>{{ memory_usage|round(3) }}</td>" +
            '<tr><td>Details</td><td><a href="/eboa_nav/query-event-links/{{ event.event_uuid }}">{{ event.event_uuid }}"></a></td>' +
            "</tr></table>"
    },
    {
        "id": "{{ event.event_uuid }}-memory-buffers",
        "group": "memory_buffers",
        "x": "{{ event.start.isoformat() }}",
        "y": "{{ memory_buffers_percentage }}",
        "tooltip": "<table border='1'>" +
            "<tr><td>Group</td><td>Memory buffers</td>" +
            "<tr><td>Notification time</td><td>{{ event.start.isoformat() }}</td>" +
            "<tr><td>Value</td><td>{{ memory_buffers_percentage|round(3) }}</td>" +
            '<tr><td>Details</td><td><a href="/eboa_nav/query-event-links/{{ event.event_uuid }}">{{ event.event_uuid }}"></a></td>' +
            "</tr></table>"
    },
    {
        "id": "{{ event.event_uuid }}-memory-cached",
        "group": "memory_cached",
        "x": "{{ event.start.isoformat() }}",
        "y": "{{ memory_cached_percentage }}",
        "tooltip": "<table border='1'>" +
            "<tr><td>Group</td><td>Memory cached</td>" +
            "<tr><td>Notification time</td><td>{{ event.start.isoformat() }}</td>" +
            "<tr><td>Value</td><td>{{ memory_cached_percentage|round(3) }}</td>" +
            '<tr><td>Details</td><td><a href="/eboa_nav/query-event-links/{{ event.event_uuid }}">{{ event.event_uuid }}"></a></td>' +
            "</tr></table>"
    },
    {
        "id": "{{ event.event_uuid }}-swap-usage",
        "group": "swap_usage",
        "x": "{{ event.start.isoformat() }}",
        "y": "{{ swap_usage }}",
        "tooltip": "<table border='1'>" +
            "<tr><td>Group</td><td>Swap usage</td>" +
            "<tr><td>Notification time</td><td>{{ event.start.isoformat() }}</td>" +
            "<tr><td>Value</td><td>{{ swap_usage|round(3) }}</td>" +
            '<tr><td>Details</td><td><a href="/eboa_nav/query-event-links/{{ event.event_uuid }}">{{ event.event_uuid }}"></a></td>' +
            "</tr></table>"
    },
    {% endfor %}
]
