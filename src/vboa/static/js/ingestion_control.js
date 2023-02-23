import * as queryFunctions from "./query.js";
import * as toastr from "toastr/toastr.js";

/*
* Functions for ingestion control
*/

/* Function to submit the request from selected files in table */
export function submit_request_for_manual_ingestion_management(form_id){
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
        if (file_name in browse_files) {
            form_data.append("files", browse_files[file_name])        
        }
    })
    if (!form_data.has("files")){
        toastr.error("No source has been selected to perform the chosen operation.")
    }
    else{
        var redirection_confirmation = confirm("You are about to be redirect to the ingestion control complete view to monitor your ingestions. The page will be updated automatically every 1 minute. Do you want to continue with the operation?")
        if (redirection_confirmation){
            var relative_url_to_redirect = "/ingestion_control/sliding_ingestion_control_parameters?window_delay=0&window_size=1.0&repeat_cycle=1"
            queryFunctions.request_upload_files_and_redirect("manual-ingestion/ingest-files", relative_url_to_redirect, form_data)        
            toastr.success("Ingestion of selected file/s requested")
        }else{
            toastr.success("The ingestions of selected file/s has been cancelled")
        };
    }
}

/* Function to clean selected file from table */
export function clean_selected_files_manual_ingestion(form_id){
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

    /* Delete files selected */
    var table = jQuery("#" + table_id).dataTable();
    table.$(".selected").each(function(){
        /* Just take the files selected */
        var file_name = jQuery("#" + this.id + " #name").text();
        if (file_name in browse_files) {
            delete browse_files[file_name]  
        }
        else{
            toastr.error("No source has been selected to perform the chosen operation.")
        }
    })
     
    /* Reset value of the input to detect addEventListener'change' */
    file_input.value = null
    
    show_files_to_ingest(browse_files)
}

/* Function to prepare files to be uploaded */
export function prepare_browse_files() {
    for (var i = 0; i < file_input.files.length; i++) {
        /* Check size bigger than 25 MB */
        if (file_input.files[i].size > 26214400){
            var size_confirmation = confirm("The size of the file " + file_input.files[i].name + " is bigger than 25MB. Do you want to continue with the operation?")
            if (size_confirmation){
                browse_files[file_input.files[i]["name"]] = file_input.files[i];
            }else {
                toastr.success("The upload of selected file with size bigger than 25MB has been cancelled")
            };
        }else {
            browse_files[file_input.files[i]["name"]] = file_input.files[i];
        };
    }
    if (!isEmpty(browse_files)) {
        show_files_to_ingest(browse_files) 
    }
};