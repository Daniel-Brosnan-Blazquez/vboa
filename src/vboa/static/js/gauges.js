import * as query from "./query.js";
import * as selectorFunctions from "./selectors.js";
import * as graph from "./graph.js";

/*
* Functions for the EBOA navigation
*/

/* Function to create the text for the tooltip of the gauge information */
function create_gauge_tooltip_text(gauge){

    return "<table border='1'>" +
        "<tr><td>UUID</td><td>" + gauge["id"] + "</td></tr>" +
        "<tr><td>Gauge name</td><td>" + gauge["name"] + "</td></tr>" +
        "<tr><td>Gauge system</td><td>" + gauge["system"] + "</td></tr>" +
        "<tr><td>Gauge description</td><td>" + gauge["description"] + "</td></tr>" +        
        "<tr><td>DIM signature</td><td>" + gauge["dim_signature_name"] + "</td></tr>" +
        "<tr><td>DIM signature UUID</td><td>" + gauge["dim_signature_uuid"] + "</td></tr>" +
        "</tr></table>"
};

export function create_gauge_network(gauges, dom_id){

    var nodes = []
    var edges = []
    for (const gauge of gauges){

        for (const gauge_link of gauge["gauges_linking"]){
            edges.push({
                "from": gauge_link["gauge_uuid"],
                "to": gauge["id"],
                "arrows": "to",
                "label": gauge_link["link_name"]
            })
        }
        for (const gauge_link of gauge["gauges_linked"]){
            edges.push({
                "from": gauge["id"],
                "to": gauge_link["gauge_uuid"],
                "arrows": "to",
                "label": gauge_link["link_name"]
            })
        }
        nodes.push({
            "id": gauge["id"],
            "color": "lightblue",
            "shape": "elipse",
            "tooltip": create_gauge_tooltip_text(gauge),
            "label": "Gauge name: " + gauge["name"] + "\nGauge system: " + gauge["system"] + "\nGauge UUID: " + gauge["id"] + "\nDIM signature: " + gauge["dim_signature_name"],
            "font": {"align": "left"}
        });
    }

    const options = {
        physics: {
            enabled: true,
            repulsion: {
                nodeDistance: 1000
            },
            solver: "repulsion"
        },
        edges: {
            width: 10,
            color: "green"
        },
        interaction:{hover:true}
    };

    graph.display_network(dom_id, nodes, edges, options);

};

/*
* Query functions
*/

/* Functions for the query interface */
export function fill_gauges(){
    const divs = document.getElementsByClassName("query-gauges");
    var gauge_name_selectors = []
    var gauge_system_selectors = []
    for (const div of divs){
        const gauge_name_div = div.getElementsByClassName("query-gauge-names")[0];
        const gauge_system_div = div.getElementsByClassName("query-gauge-systems")[0];

        /* Gauge name */
        var gauge_name_selector = gauge_name_div.getElementsByTagName("datalist")[0];
        if (gauge_name_selector == null){
           gauge_name_selector = gauge_name_div.getElementsByTagName("select")[0];
        }
        /* If the options were already filled exit */
        if (gauge_name_div.getElementsByTagName("option").length != 0){
            return false
        }
        gauge_name_selectors.push(gauge_name_selector);

        /* Gauge system */
        var gauge_system_selector = gauge_system_div.getElementsByTagName("datalist")[0];
        if (gauge_system_selector == null){
           gauge_system_selector = gauge_system_div.getElementsByTagName("select")[0];
        }
        /* If the options were already filled exit */
        if (gauge_system_div.getElementsByTagName("option").length != 0){
            return false
        }
        gauge_system_selectors.push(gauge_system_selector);
    }
    var selectors = {
        "gauge_name_selectors": gauge_name_selectors,
        "gauge_system_selectors": gauge_system_selectors
    }
    query.request_info("/eboa_nav/query-jsonify-gauges", fill_gauges_into_selectors, selectors);
    return true
}

function fill_gauges_into_selectors(selectors, gauges){

    var gauge_names = new Set(gauges.map(gauge => gauge["name"]))
    var gauge_systems = new Set(gauges.map(gauge => gauge["system"]))
    for (const gauge_name of gauge_names){
        for (const selector of selectors["gauge_name_selectors"]){
            selectorFunctions.add_option(selector, gauge_name);
        }
    }
    for (const gauge_system of gauge_systems){
        for (const selector of selectors["gauge_system_selectors"]){
            selectorFunctions.add_option(selector, gauge_system);
        }
    }
    /* Update chosen for the multiple input selection */
    jQuery(".chosen-select").trigger("chosen:updated");
}

