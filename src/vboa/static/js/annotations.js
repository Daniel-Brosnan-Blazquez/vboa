import * as query from "./query.js";
import * as graph from "./graph.js";

/*
* Functions for the EBOA navigation
*/

/* Function to create the text for the tooltip of the annotation information */
function create_annotation_tooltip_text(annotation){

    return "<table border='1'>" +
        "<tr><td>UUID</td><td>" + annotation['id'] + "</td></tr>" +
        "<tr><td>Explicit reference</td><td><a href='/eboa_nav/query-er/" + annotation["explicit_ref_uuid"] + "'>" + annotation['explicit_reference'] + "</a></td><tr>" +
        "<tr><td>Annotation name</td><td>" + annotation['annotation_cnf']['name'] + "</td></tr>" +
        "<tr><td>Annotation system</td><td>" + annotation['annotation_cnf']['system'] + "</td></tr>" +
        "<tr><td>Source</td><td><a href='/eboa_nav/query-source/" + annotation["source_uuid"] + "'>" + annotation['source'] + "</a></td></tr>" +
        "<tr><td>Ingestion time</td><td>" + annotation['ingestion_time'] + "</td></tr>" +
        "<tr id='expand-tooltip-values-annotation-" + annotation["id"] + "'><td>Values</td><td><i class='fa fa-plus-square green' onclick='" + 'vboa.expand_annotation_values_in_tooltip("expand-tooltip-values-annotation-' + annotation["id"] + '", "' + annotation["id"] + '")' + "' data-toggle='tooltip' title='Click to show the related values'></i></td></tr>" +
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
        var parameters = {
            "row": row,
            "insert_method": insert_in_datatable
        }
        query.request_info("/eboa_nav/query-jsonify-annotation-values/" + annotation_uuid, show_annotation_values, parameters);
        tr.addClass('shown');
        tdi.first().removeClass('fa-plus-square');
        tdi.first().removeClass('green');
        tdi.first().addClass('fa-minus-square');
        tdi.first().addClass('red');
    }
};

/* Function to show the values related to an annotation in a tooltip */
export function expand_values_in_tooltip(dom_id, annotation_uuid){

    var tr = document.getElementById(dom_id);
    // Structure is /div/div/table/tbody/tr
    var container_div = tr.parentNode.parentNode.parentNode.parentNode;
    var tdi = tr.getElementsByTagName("i")[0];

    var expanded_div = container_div.querySelector("#expanded_values")
    if (tr.classList.contains("expanded")) {
        // This tr is already open - close it
        expanded_div.style.display = 'none';
        tr.classList.remove('expanded');
        tdi.classList.remove('fa-minus-square');
        tdi.classList.remove('red');
        tdi.classList.add('fa-plus-square');
        tdi.classList.add('green');
    }
    else if (expanded_div == undefined){
        // Create the expanded tr
        const expanded_div = document.createElement("div");
        expanded_div.id = "expanded_values"        
        container_div.appendChild(expanded_div);
        var parameters = {
            "row": expanded_div,
            "insert_method": insert_in_html_table
        }
        query.request_info("/eboa_nav/query-jsonify-annotation-values/" + annotation_uuid, show_annotation_values, parameters);
        tr.classList.add('expanded');
        tdi.classList.remove('fa-plus-square');
        tdi.classList.remove('green');
        tdi.classList.add('fa-minus-square');
        tdi.classList.add('red');
    }
    else {
        // Open this tr
        tr.classList.add('expanded');
        tdi.classList.remove('fa-plus-square');
        tdi.classList.remove('green');
        tdi.classList.add('fa-minus-square');
        tdi.classList.add('red');
        expanded_div.style.display = 'block';        
    }
};

function show_annotation_values(parameters, values){

    var row = parameters["row"]
    
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
    
    parameters["insert_method"](row, table);

    return
}

function insert_in_datatable(row, table){
    row.child(table).show();
}

function insert_in_html_table(row, table){
    row.innerHTML = table;
}