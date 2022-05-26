
/**
 * @description Function to verify the content of a tle
 * @param {string} tle_string: TLE of the satellite with the following format:
 * SATELLITE-INDICATOR
 * 1 NNNNNC NNNNNAAA NNNNN.NNNNNNNN +.NNNNNNNN +NNNNN-N +NNNNN-N N NNNNN
 * 2 NNNNN NNN.NNNN NNN.NNNN NNNNNNN NNN.NNNN NNN.NNNN NN.NNNNNNNNNNNNNN
 
 * @returns {dictionary} {"verifies": Bool, "first_line": String, "second_line": String}
 */
function verify_tle(tle_string){

    let tle_lines = {
        "verifies": false,
        "satellite_line": "",
        "first_line": "",
        "second_line": ""
    }
    
    /* Verify TLE has three lines */
    if (tle_string.match(/.*\n.*\n.*/) == null){
        return tle_lines;
    }

    /* Obtain satellite line of TLE */
    tle_lines["satellite_line"] = tle_string.split("\n")[0];

    /* Obtain first line of TLE */
    tle_lines["first_line"] = tle_string.split("\n")[1];

    /* Verify first line */
    if (tle_lines["first_line"].match(/1 ...... ........ .............. .......... ......-. ......-. . ...../) == null){
        return tle_lines;
    }

    tle_lines["second_line"] = tle_string.split("\n")[2];

    /* Verify second line */
    if (tle_lines["second_line"].match(/2 ..... ........ ........ ....... ........ ........ ................./) == null){
        return tle_lines;
    }

    tle_lines["verifies"] = true;
    
    return tle_lines;

}

/* Function to get the fields contained in a TLE */
export function get_tle_fields(tle_string){

    /* Obtain TLE lines */
    const tle_lines = verify_tle(tle_string);
        
    let tle_fields = {"verifies": false};

    if (tle_lines["verifies"]){

        /* Set verification */
        tle_fields["verifies"] = true
        
        const satellite_line = tle_lines["satellite_line"];
        const first_line = tle_lines["first_line"];
        const second_line = tle_lines["second_line"];

        /* Get satellite name */
        tle_fields["satellite"] = satellite_line;

        /* Get epoch */
        const round = (n, to) => n - n % to;
        const now = new Date();
        const millennium = round(now.getUTCFullYear(), 100);
        const year = millennium + parseFloat(first_line.substring(18, 20));
        const days = parseFloat(first_line.substring(20, 32));
        const year_date = new Date(String(year), 0, 1);
        const epoch_date = new Date(year_date.getTime() + days * 24 * 60 * 60 * 1000);
        tle_fields["epoch"] = epoch_date.toISOString();

        /* Get inclination */
        tle_fields["inclination"] = second_line.substring(8, 16);

        /* Get right ascension of the ascending node */
        tle_fields["raan"] = second_line.substring(17, 25);

        /* Get eccentricity */
        tle_fields["eccentricity"] = "0." + second_line.substring(26, 33);

        /* Get perigee */
        tle_fields["perigee"] = second_line.substring(34, 42);

        /* Get mean anomaly */
        tle_fields["mean_anomaly"] = second_line.substring(43, 51);

        /* Get mean motion */
        tle_fields["mean_motion"] = second_line.substring(52, 63);

        /* Orbit duration */
        tle_fields["orbit_duration"] = (24*60) / tle_fields["mean_motion"];
        
        /* Get orbit */
        tle_fields["orbit"] = second_line.substring(63, 68);

        /* Obtain semimajor from mean motion
           References:
           https://space.stackexchange.com/questions/18289/how-to-get-semi-major-axis-from-tle
           https://smallsats.org/2012/12/06/two-line-element-set-tle/
        */
        /* Standard gravitational parameter for the earth */
        const mu = 398600.0;
        tle_fields["semimajor"] = vboa.math.pow((mu/vboa.math.pow((tle_fields["mean_motion"]*2*vboa.math.pi/(86400)), 2)), (1/3));

    }
    
    return tle_fields;
    
}
