import * as dates from "./dates.js";
import * as graph from "./graph.js";
import * as query from "./query.js";
import * as selectorFunctions from "./selectors.js";
import * as queryFunctions from "./query.js";
import * as toastr from "toastr/toastr.js";

/*
* Functions for the RBOA navigation
*/

/* Function to establish the groups of reports using the report groups */
function create_reports_groups_by_report_group(reports){
    var groups = [];
    var report_groups = new Set(reports.map(report => report["report_group"]))

    for (const report_group of report_groups){
        groups.push({
            id: report_group,
            content: report_group,
            options: {
                drawPoints: {
                    style: "circle"
                }
            }
        })
    }
    return groups;
}

/* Function to create the text for the tooltip of the report information */
function create_report_tooltip_text(report){
    const validity_duration = dates.date_difference_in_m(report["validity_stop"], report["validity_start"])
    const generation_duration = dates.date_difference_in_m(report["generation_stop"], report["generation_start"])
    return "<table border='1'>" +
        "<tr><td>Report UUID</td><td>" + report["id"] + "</td></tr>" +
        "<tr><td>Name</td><td><a href='/rboa_nav/query-report/" + report["id"] + "'>" + report["name"] + "</a></td></tr>" +
        "<tr><td>Generation mode</td><td>" + report["generation_mode"] + "</td></tr>" +
        "<tr><td>Report group</td><td>" + report["report_group"] + "</td></tr>" +
        "<tr><td>Validity start</td><td>" + report["validity_start"] + "</td></tr>" +
        "<tr><td>Validity stop</td><td>" + report["validity_stop"] + "</td></tr>" +
        "<tr><td>Validity duration</td><td>" + validity_duration + "</td></tr>" +
        "<tr><td>Generation start</td><td>" + report["generation_start"] + "</td></tr>" +
        "<tr><td>Generation stop</td><td>" + report["generation_stop"] + "</td></tr>" +
        "<tr><td>Generation duration</td><td>" + generation_duration + "</td></tr>" +
        "<tr><td>Generator</td><td>" + report["generator"] + "</td></tr>" +
        "<tr><td>Version of generator</td><td>" + report["version"] + "</td></tr>" +
        "</tr></table>"
};

export function create_report_validity_timeline(reports, dom_id){
    const groups = create_reports_groups_by_report_group(reports);
    var items = [];
    for (const report of reports){
        items.push({
            id: report["id"],
            group: report["report_group"],
            start: report["validity_start"],
            end: report["validity_stop"],
            tooltip: create_report_tooltip_text(report)
        })
    }
    graph.display_timeline(dom_id, items, groups);

};

export function create_report_generation_duration_xy(reports, dom_id){
    const groups = create_reports_groups_by_report_group(reports);
    var items = [];
    for (const report of reports){
        const generation_duration = dates.date_difference_in_m(report["generation_stop"], report["generation_start"])
        
        items.push({
            id: report["id"],
            group: report["report_group"],
            x: report["triggering_time"],
            y: generation_duration,
            tooltip: create_report_tooltip_text(report)
        })
    }

    const options = {
        legend: true,
        dataAxis: {
            left: {
                title: {
                    text: "Minutes"
                }
            }
        }
    };

    graph.display_x_time(dom_id, items, groups, options);

};

/*
* Query functions
*/

/* Function to show the statuses related to a report */
export function expand_report_statuses(dom_id, report_uuid){
    
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
        query.request_info("/rboa_nav/query-jsonify-report-statuses/" + report_uuid, show_report_statuses, parameters);
        tr.addClass('shown');
        tdi.first().removeClass('fa-plus-square');
        tdi.first().removeClass('green');
        tdi.first().addClass('fa-minus-square');
        tdi.first().addClass('red');
    }
};

function show_report_statuses(parameters, statuses){

    var row = parameters["row"]

    var table = '<table class="table">' +
        '<thead>' +
        '<tr>' +
        '<th>Status</th>' +
        '<th>TIme stamp</th>' +
        '<th>Log</th>' +
        '</tr>' +
        '</thead>' +
        '<tbody>';

    for (const status of statuses){
        table = table + 
            '<tr>' +
            '<td>' + status["status"] + '</td>' +
            '<td>' + status["time_stamp"] + '</td>' +
            '<td>' + status["log"] + '</td>' +
            '</tr>'
    }
    table = table + '</tbody>' +
        '</table>';

    parameters["insert_method"](row, table);
    
}

function insert_in_datatable(row, table){
    row.child(table).show();
}

/* Functions for the query interface */
export function fill_reports(){
    const divs = document.getElementsByClassName("query-reports");
    var report_selectors = []
    var generator_selectors = []
    for (const div of divs){
        const report_divs = div.getElementsByClassName("query-report-names");
        const generator_divs = div.getElementsByClassName("query-report-generators");

        /* Report */
        for (const report_div of report_divs){
            var report_selector = report_div.getElementsByTagName("datalist")[0];
            if (report_selector == null){
                report_selector = report_div.getElementsByTagName("select")[0];
            }
            /* If the options were already filled exit */
            if (report_div.getElementsByTagName("option").length != 0){
                return false
            }
            report_selectors.push(report_selector);
        }

        /* Generator */
        for (const generator_div of generator_divs){
            var generator_selector = generator_div.getElementsByTagName("datalist")[0];
            if (generator_selector == null){
                generator_selector = generator_div.getElementsByTagName("select")[0];
            }
            /* If the options were already filled exit */
            if (generator_div.getElementsByTagName("option").length != 0){
                return false
            }
            generator_selectors.push(generator_selector);
        }
    }
    var selectors = {
        "report_selectors": report_selectors,
        "generator_selectors": generator_selectors
    }
    query.request_info("/rboa_nav/query-jsonify-reports", fill_reports_into_selectors, selectors);
    return true
}

function fill_reports_into_selectors(selectors, reports){

    var report_names = new Set(reports.map(report => report["name"]))
    var generators = new Set(reports.map(report => report["generator"]))
    for (const report of report_names){
        for (const selector of selectors["report_selectors"]){
            selectorFunctions.add_option(selector, report);
        }
    }
    for (const generator of generators){
        for (const selector of selectors["generator_selectors"]){
            selectorFunctions.add_option(selector, generator);
        }
    }
    /* Update chosen for the multiple input selection */
    jQuery(".chosen-select").trigger("chosen:updated");
}

export function fill_statuses(){
    const divs = document.getElementsByClassName("query-report-statuses");
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
    query.request_info("/rboa_nav/get-report-status", fill_statuses_into_selectors, selectors);
    return true
}

function fill_statuses_into_selectors(selectors, statuses){

    for (const status of Object.keys(statuses)){
        for (const selector of selectors){
            selectorFunctions.add_option_tooltip(selector, status, statuses[status]["message"]);
        }
    }
    /* Update chosen for the multiple input selection */
    jQuery(".chosen-select").trigger("chosen:updated");

    /* Activate tooltips */
    jQuery("[data-toggle='tooltip']").tooltip();
}

export function submit_request_for_execution(){

    var form = document.getElementById("execute-reports");
    var form_data = new FormData(form);
    
    var table = jQuery("#generators-table").dataTable();

    table.$(".selected").each(function(){
        form_data.append("generators", this.id)
    })

    queryFunctions.request_info_form_data("/rboa_nav/execute-reports", notify_end_of_generation_of_reports, form_data)

    var message = "Reports for the period " + form_data.get("start") + " - " + form_data.get("stop") +  " are going to be generated using the following generators:"
    for (const generator of form_data.getAll("generators")){
        message += "</br>- <b>" + generator + "</b>"
    }

    toastr.success(message)
    
}

export function notify_end_of_generation_of_reports(response, form_data){

    var message = "Reports for the period " + form_data.get("start") + " - " + form_data.get("stop") +  " were generated using the following generators:"
    for (const generator of form_data.getAll("generators")){
        message += "</br>- <b>" + generator + "</b>"
    }

    toastr.success(message)
    return true;
}
