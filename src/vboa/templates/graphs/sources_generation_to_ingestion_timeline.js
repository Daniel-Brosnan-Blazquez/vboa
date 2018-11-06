var groups = [];
var items = [];

var dim_signatures = new Set(sources["sources"].map(source => source["dim_signature"]))

for (const dim_signature of dim_signatures){
    groups.push({
        id: dim_signature,
        content: dim_signature
    })
}

for (const source of sources["sources"]){
    items.push({
        id: source["id"],
        group: source["dim_signature"],
        start: source["generation_time"],
        end: source["ingestion_time"],
        tooltip: "<table border='1'>" +
            "<tr><td>Source UUID</td><td>" + source["id"] + "</td>" +
            "<tr><td>Name</td><td>" + source["name"] + "</td>" +
            "<tr><td>DIM Signature</td><td>" + source["dim_signature"] + "</td>" +
            "<tr><td>Processor</td><td>" + source["processor"] + "</td>" +
            "<tr><td>Version of processor</td><td>" + source["version"] + "</td>" +
            "<tr><td>Validity start</td><td>" + source["validity_start"] + "</td>" +
            "<tr><td>Validity stop</td><td>" + source["validity_stop"] + "</td>" +
            "<tr><td>Generation time</td><td>" + source["generation_time"] + "</td>" +
            "<tr><td>Ingestion time</td><td>" + source["ingestion_time"] + "</td>" +
            "<tr><td>Ingestion duration</td><td>" + source["ingestion_duration"] + "</td>" +
            "</tr></table>"
    })
}
