import * as query from "./query.js";
import * as selectorFunctions from "./selectors.js";
import * as graph from "./graph.js";

/* Functions for the query interface */
export function fill_ers(){
    const divs = document.getElementsByClassName("query-ers");
    var selectors = []
    for (const div of divs){
        var selector = div.getElementsByTagName("datalist")[0];
        if (selector == null){
           selector = div.getElementsByTagName("select")[0];
        }
        /* If the options were already filled exit */
        if (selector.getElementsByTagName("option").length != 0){
            return false
        }
        selectors.push(selector);
    }
    query.request_info("/eboa_nav/query-jsonify-ers", fill_ers_into_selectors, selectors);
    return true
}

function fill_ers_into_selectors(selectors, ers){

    const er_names = new Set(ers.map(er => er["explicit_ref"]))

    for (const er_name of er_names){
        for (const selector of selectors){
            selectorFunctions.add_option(selector, er_name);
        }
    }
    /* Update chosen for the multiple input selection */
    jQuery(".chosen-select").trigger("chosen:updated");
}

export function fill_er_groups(){
    const divs = document.getElementsByClassName("query-er-groups");
    var selectors = []
    for (const div of divs){
        var selector = div.getElementsByTagName("datalist")[0];
        if (selector == null){
           selector = div.getElementsByTagName("select")[0];
        }
        /* If the options were already filled exit */
        if (selector.getElementsByTagName("option").length != 0){
            return false
        }
        selectors.push(selector);
    }
    query.request_info("/eboa_nav/query-jsonify-er-groups", fill_er_groups_into_selectors, selectors);
    return true
}

function fill_er_groups_into_selectors(selectors, er_groups){

    const er_group_names = new Set(er_groups.map(er_group => er_group["name"]))

    for (const er_group_name of er_group_names){
        for (const selector of selectors){
            selectorFunctions.add_option(selector, er_group_name);
        }
    }
    /* Update chosen for the multiple input selection */
    jQuery(".chosen-select").trigger("chosen:updated");
}

/* Function to create the text for the tooltip of the event information */
function create_er_tooltip_text(er){

    return "<table border='1'>" +
        "<tr><td>UUID</td><td>" + er['id'] + "</td></tr>" +
        "<tr><td>Explicit reference</td><td>" + er['explicit_reference'] + "</td></tr>" +
        "<tr><td>Ingestion time</td><td>" + er['ingestion_time'] + "</td></tr>" +
        "<tr><td>Events</td><td><a href='/eboa_nav/query-events-by-er/" + er["explicit_reference"] + "'><i class='fa fa-link'></i></a></td></tr>" +
        "<tr><td>Annotations</td><td><a href='/eboa_nav/query-annotations-by-er/" + er["explicit_reference"] + "'><i class='fa fa-link'></i></a></td></tr>" +
        "<tr><td>Links</td><td><a href='/eboa_nav/query-er-links/" + er["id"] + "'><i class='fa fa-link'></i></a></td></tr>" +
        "</table>"
};

/* Function to create a network graph for the EBOA navigation view */
export function create_er_network(linked_ers, dom_id){
    var unique_er_uuids = new Set(linked_ers.map(er => er["id"]));
    var prime_er_id = linked_ers.filter(er => er["label"] == "prime_ers").map(er => er["id"])[0];

    var nodes = []
    var edges = []
    for (const id of unique_er_uuids){
        var associated_ers = linked_ers.filter(er => er["id"] == id)

        for (const er of associated_ers){
            var shape = "box";
            var background_color = "lightblue";
            if (er["label"] == "prime_explicit_refs"){
                shape = "elipse";
                background_color = "lightgreen";
            }
            else if (er["label"] == "explicit_refs_linking"){
                edges.push({
                    "from": er["id"],
                    "to": prime_er_id,
                    "arrows": "to",
                    "label": er["link_name"]
                })
            }
            else{
                edges.push({
                    "from": prime_er_id,
                    "to": er["id"],
                    "arrows": "to",
                    "label": er["link_name"]
                })
            }
        }
        nodes.push({
            "id": associated_ers[0]["id"],
            "color": background_color,
            "shape": shape,
            "tooltip": create_er_tooltip_text(associated_ers[0]),
            "label": "Explicit reference: " + associated_ers[0]['explicit_reference'],
            "font": {"align": "left"}
        });
    }
    graph.display_network(dom_id, nodes, edges);

};
