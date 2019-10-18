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

/* Function to request information to the EBOA by URL, using json for the parameters */
export function request_info_json(url, callback, json){

    var xmlhttp = new XMLHttpRequest();
    if (callback){
        xmlhttp.onreadystatechange = function() {
            if (this.readyState == 4 && this.status == 200) {
                return callback(this.responseText);
            }
        };
    }
    
    xmlhttp.open("POST", url, true);
    xmlhttp.setRequestHeader('content-type', 'application/x-www-form-urlencoded;charset=UTF-8');
    xmlhttp.send("json=" + JSON.stringify(json));
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
    xmlhttp.setRequestHeader('content-type', 'application/x-www-form-urlencoded;charset=UTF-8');
    xmlhttp.send("json=" + JSON.stringify(json));
}
