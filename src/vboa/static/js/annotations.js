import * as query from "./query.js";
import * as graph from "./graph.js";

/*
* Functions for the EBOA navigation
*/

/* Function to create the text for the tooltip of the annotation information */
function create_annotation_tooltip_text(annotation){

    return "<table border='1'>" +
        "<tr><td>UUID</td><td>" + annotation['id'] + "</td></tr>" +
        "<tr><td>Explicit reference</td><td>" + annotation['explicit_reference'] + "</td></tr>" +
        "<tr><td>Annotation name</td><td>" + annotation['annotation_cnf']['name'] + "</td></tr>" +
        "<tr><td>Annotation system</td><td>" + annotation['annotation_cnf']['system'] + "</td></tr>" +
        "<tr><td>Source</td><td>" + annotation['source'] + "</td></tr>" +
        "<tr><td>Ingestion time</td><td>" + annotation['ingestion_time'] + "</td></tr>" +
        "</table>"
};

/* Function to create a network graph for the EBOA navigation view */
export function create_annotation_map(annotations_geometries, dom_id){

    var polygons = [];

    for (const annotation_geometries of annotations_geometries){
        var i = 0;
        for (const geometry of annotation_geometries["geometries"]){
            polygons.push({"polygon": geometry["value"],
                           "id": annotation_geometries["id"] + "_" + i,
                           "tooltip": create_annotation_tooltip_text(annotation_geometries)})
            i = i + 1;
        }
    }
    
    graph.display_map(dom_id, polygons);
};

/*
* Query functions
*/

/* Function to add more value filter selectors when commanded */
export function add_value_query(dom_id){
    
    jQuery.ajax({url: "/static/html/more_value_query_annotations.html",
                cache: false}).done(function (data){
                    jQuery("#" + dom_id).append(data);
                });

};

/* Function to show the values related to an annotation */
export function expand_values(dom_id, annotation_uuid){
    
    var table = jQuery("#" + dom_id).closest("table").DataTable();
    var tr = jQuery("#" + dom_id).closest("tr");
    var tdi = tr.find("i.fa");
    var row = table.row(tr);
    
    if (row.child.isShown()) {
        // This row is already open - close it
        row.child.hide();
        tr.removeClass('shown');
        tdi.first().removeClass('fa-minus-square');
        tdi.first().removeClass('red');
        tdi.first().addClass('fa-plus-square');
        tdi.first().addClass('green');
    }
    else {
        // Open this row
        query.request_info("/eboa_nav/query-jsonify-annotation-values/" + annotation_uuid, show_annotation_values, row);
        tr.addClass('shown');
        tdi.first().removeClass('fa-plus-square');
        tdi.first().removeClass('green');
        tdi.first().addClass('fa-minus-square');
        tdi.first().addClass('red');
    }
};

function show_annotation_values(row, values){

    var table = '<table class="table">' +
        '<thead>' +
        '<tr>' +
        '<th>Type</th>' +
        '<th>Name</th>' +
        '<th>Value</th>' +
        '<th>Position</th>' +
        '<th>Parent level</th>' +
        '<th>Parent position</th>' +
        '</tr>' +
        '</thead>' +
        '<tbody>';

    for (const value of values){
        table = table + 
            '<tr>' +
            '<td>' + value["type"] + '</td>' +
            '<td>' + value["name"] + '</td>' +
            '<td>' + value["value"] + '</td>' +
            '<td>' + value["position"] + '</td>' +
            '<td>' + value["parent_level"] + '</td>' +
            '<td>' + value["parent_position"] + '</td>' +
            '</tr>'
    }
    table = table + '</tbody>' +
        '</table>';
    
    row.child(table).show();

    return
}

