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
