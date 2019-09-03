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
