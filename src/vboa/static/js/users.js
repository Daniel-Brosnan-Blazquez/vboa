import * as query from "./query.js";
import * as selectorFunctions from "./selectors.js";
import * as queryFunctions from "./query.js";
import * as toastr from "toastr/toastr.js";
import * as renderFunctions from "./render.js";

/*
* Functions for the UBOA navigation
*/

/* Function to show the roles related to a user */
export function expand_user_roles(dom_id, user_uuid){
    
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
        query.request_info("/users-management/uboa-nav/query-jsonify-user-roles/" + user_uuid, show_user_roles, parameters);
        tr.addClass('shown');
        tdi.first().removeClass('fa-plus-square');
        tdi.first().removeClass('green');
        tdi.first().addClass('fa-minus-square');
        tdi.first().addClass('red');
    }
};

function insert_in_datatable(row, table){
    row.child(table).show();
}

function show_user_roles(parameters, roles){

    var row = parameters["row"]

    var table = '<table class="table">' +
        '<thead>' +
        '<tr>' +
        '<th>Role</th>' +
        '<th>Description</th>' +
        '</tr>' +
        '</thead>' +
        '<tbody>';

    for (const role of roles){
        table = table + 
            '<tr>' +
            '<td>' + role["name"] + '</td>' +
            '<td>' + role["description"] + '</td>' +
            '</tr>'
    }
    table = table + '</tbody>' +
        '</table>';

    parameters["insert_method"](row, table);
    
}

/*
* User management functions
*/

export function submit_request_for_users_management(form_id){

    var form = document.getElementById(form_id);
    var operation = form.operation

    /* Search table id */
    var tables = form.getElementsByTagName("table");
    var table_id = "";
    for (const table of tables){
        if (table.id != ""){
            table_id = table.id;
            break;
        };
    };

    /* Fill form data */
    var form_data = new FormData(form);
    var table = jQuery("#" + table_id).dataTable();
    table.$(".selected").each(function(){
        form_data.append("users", this.id)
    })

    
    if (!form_data.has("users")){
        toastr.error("No user has been selected to perform the chosen operation.")
    }
    else{
        var loader = document.getElementById("updating-page");
        loader.className = "loader-render"
        if (operation == "deletion_preparation"){
            queryFunctions.request_info_form_data("/users-management/uboa-nav/prepare-deletion-of-users", renderFunctions.render_page, form_data)
            
            toastr.success("Deletion of selected user/s requested")
        }
        else if (operation == "deletion"){
            var deletion_confirmation = confirm("You are about to perform a deletion operation. This will erase the data from the DDBB. Do you want to continue with the operation?")
            if (deletion_confirmation){
                queryFunctions.request_info_form_data("/users-management/uboa-nav/delete-users", notify_deletion, form_data)
                toastr.success("Deletion of selected user/s has been confirmed")
            }else{
                toastr.success("Deletion of selected user/s has been cancelled")
                loader.className = ""
            };
        }
        else{
            toastr.success("The operation requested is not available")
            loader.className = ""
        };
    };
    
}

function notify_deletion(response){

    toastr.success("Deletion operation has been completed")

    // Stop loader
    var loader = document.getElementById("updating-page");
    loader.className = ""
    
}