import * as toastr from "toastr/toastr.js";

/* Function to request information to the EBOA by URL */
export function request_info(url, callback, parameters){
    var xmlhttp = new XMLHttpRequest();
    if (callback){
        xmlhttp.onreadystatechange = function() {
            if (this.readyState == 4 && this.status == 200) {
                return callback(parameters, JSON.parse(this.responseText));
            }
            else if (this.readyState == 4 && this.status == 403){
                toastr.error("Ups... Sorry it seems you don't have access to the resource: " + url);
                var permission_denied_response = {
                    "return_code": 403
                };

                return callback(parameters, permission_denied_response);
            }
        };
    }
    xmlhttp.open("GET", url, true);
    xmlhttp.send();
}

/* Function to request information to the EBOA by URL with no parameters */
export function request_info_no_args(url, callback, show_loader = false){
    if (show_loader == true){
        var loader = document.getElementById("updating-page");
        loader.className = "loader-render"
    }

    var xmlhttp = new XMLHttpRequest();
    if (callback){
        xmlhttp.onreadystatechange = function() {
            if (this.readyState == 4 && this.status == 200) {
                var returned_value = callback(this.responseText);
                if (show_loader == true){
                    var loader = document.getElementById("updating-page");
                    loader.className = ""
                }
                return returned_value
            }
            else if (this.readyState == 4 && this.status == 403){
                toastr.error("Ups... Sorry it seems you don't have access to the resource: " + url);
                var permission_denied_response = {
                    "return_code": 403
                };

                return callback(parameters, permission_denied_response);

            }
        };
    }
    xmlhttp.open("GET", url, true);
    xmlhttp.send();
}

/* Function to request information to the EBOA by URL, using json for the parameters */
export function request_info_json(url, callback, json, show_loader = false){
    if (show_loader == true){
        var loader = document.getElementById("updating-page");
        loader.className = "loader-render"
    }

    var xmlhttp = new XMLHttpRequest();
    if (callback){
        xmlhttp.onreadystatechange = function() {
            if (this.readyState == 4 && this.status == 200) {
                var returned_value = callback(this.responseText);
                if (show_loader == true){
                    var loader = document.getElementById("updating-page");
                    loader.className = ""
                }
                return returned_value
            }
            else if (this.readyState == 4 && this.status == 403){
                toastr.error("Ups... Sorry it seems you don't have access to the resource: " + url);
                var permission_denied_response = {
                    "return_code": 403
                };

                return callback(parameters, permission_denied_response);
            }
        };
    }
    
    xmlhttp.open("POST", url, true);
    xmlhttp.setRequestHeader('content-type', 'application/json;charset=UTF-8');
    xmlhttp.send(JSON.stringify(json));
}

/* Function to request information to the EBOA by URL, using json for the parameters after asking for confirmation */
export function request_info_json_after_confirmation(url, json, confirmation_message, cancel_message, show_loader = false){

    var confirmed = confirm(confirmation_message);
    if (confirmed){
        request_info_json(url, notify_end_of_request, json, show_loader)
    }else{
        toastr.warning(cancel_message)
    }
}

function notify_end_of_request(response){

    var data = JSON.parse(response)
    var message = data["message"];
    var status = data["status"];

    if (status == 0){
        toastr.success(message)
    }else{
        toastr.error(message)
    }
    return true;
}

/* Function to request information to the EBOA by URL, using FormData object from javascript for the parameters */
export function request_info_form_data(url, callback, form_data){

    var xmlhttp = new XMLHttpRequest();
    if (callback){
        xmlhttp.onreadystatechange = function() {
            if (this.readyState == 4 && this.status == 200) {
                return callback(this.responseText, form_data);
            }
            else if (this.readyState == 4 && this.status == 403){
                toastr.error("Ups... Sorry it seems you don't have access to the resource: " + url);
                var permission_denied_response = {
                    "return_code": 403
                };

                return callback(parameters, permission_denied_response);
            }
        };
    }
    xmlhttp.open("POST", url, true);
    var json = {};
    form_data.forEach(function(value, key){
        if (key in json){
            json[key].push(value);
        }
        else{
            json[key] = [];
            json[key].push(value);
        }
    });
    xmlhttp.setRequestHeader('content-type', 'application/json;charset=UTF-8');
    xmlhttp.send(JSON.stringify(json));
}
