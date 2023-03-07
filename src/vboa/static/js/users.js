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

    // Back to uboa navigation query page
    setTimeout(function() {
        queryFunctions.request_info_no_args("/users-management/uboa-nav/delete-users", renderFunctions.render_page, true);
    }, 2000);
    
}

/*
* Import/export users functions
*/

export function notify_import(message, error){

    if (error === true){
        toastr.error(message)
    }
    else {
        toastr.success(message)
    }
    // Stop loader
    var loader = document.getElementById("updating-page");
    loader.className = ""
    
}

/* Function to prepare file to be uploaded */
export function prepare_browse_file() {
    
    browse_file = {}
    
    /* Check size bigger than 25 MB */
    if (file_input.files[0].size > 26214400){
        var size_confirmation = confirm("The size of the file " + file_input.files[0].name + " is bigger than 25MB. Do you want to continue with the operation?")
        if (size_confirmation){
            browse_file[file_input.files[0]["name"]] = file_input.files[0];
        }else {
            toastr.success("The upload of selected file with size bigger than 25MB has been cancelled")
        };
    }else {
        browse_file[file_input.files[0]["name"]] = file_input.files[0];
    };
    
    if (Object.keys(browse_file).length > 0) {
        show_file_to_import(browse_file) 
    }
};

/* Function to submit the request from selected files in table */
export function submit_request_for_import_users_management(form_id){
    var form = document.getElementById(form_id);
    
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
        /* Just take the files selected */
        var file_name = jQuery("#" + this.id + " #name").text();
        if (file_name in browse_file) {
            form_data.append("files", browse_file[file_name])        
        }
    })
    if (!form_data.has("files")){
        toastr.error("No source has been selected to perform the chosen operation.")
    }
    else{
        var redirection_confirmation = confirm("You are about to be redirect to the UBOA navigation to monitor your imported users. Do you want to continue with the operation?")
        if (redirection_confirmation){
            var relative_url_to_redirect = "/users-management/uboa-nav/query-users-by-group/%"
            toastr.success("Import operation of user/s requested")
            const parameters_query = {
                "form_data": form_data,
                "delay_redirect": 10000
            }
            queryFunctions.request_upload_files_and_redirect("import-users/import-from-file", relative_url_to_redirect, parameters_query)        
        }else{
            toastr.success("The import operation of user/s has been cancelled")
        };
    }
}

/* Function to submit the request from selected files in table */
export function submit_request_for_import_users_manually_management(form_id){
    var form = document.getElementById(form_id);
    
    /* Fill form data */
    var form_data = new FormData(form);
    
    if (form.value == ""){
        toastr.error("The text-area is empty. No users to import")
    }
    else{
        var redirection_confirmation = confirm("You are about to be redirect to the UBOA navigation to monitor your imported users. Do you want to continue with the operation?")
        if (redirection_confirmation){
            var relative_url_to_redirect = "/users-management/uboa-nav/query-users-by-group/%"
            toastr.success("Manually import operation of user/s requested")
            const parameters_query = {
                "form_data": form_data,
                "delay_redirect": 10000
            }
            queryFunctions.request_upload_files_and_redirect("import-users/import-manually", relative_url_to_redirect, parameters_query)        
        }else{
            toastr.success("The manually import operation of user/s has been cancelled")
        };
    }
}