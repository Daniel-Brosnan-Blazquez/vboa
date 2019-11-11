/* Function to request information to the EBOA by URL */
export function request_info(url, callback, parameters){
    var xmlhttp = new XMLHttpRequest();
    if (callback){
        xmlhttp.onreadystatechange = function() {
            if (this.readyState == 4 && this.status == 200) {
                return callback(parameters, JSON.parse(this.responseText));
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
        };
    }
    
    xmlhttp.open("POST", url, true);
    xmlhttp.setRequestHeader('content-type', 'application/json;charset=UTF-8');
    xmlhttp.send(JSON.stringify(json));
}

/* Function to request information to the EBOA by URL, using FormData object from javascript for the parameters */
export function request_info_form_data(url, callback, form_data){

    var xmlhttp = new XMLHttpRequest();
    if (callback){
        xmlhttp.onreadystatechange = function() {
            if (this.readyState == 4 && this.status == 200) {
                return callback(this.responseText, form_data);
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
