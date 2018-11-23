
export function date_difference_in_ms(date1, date2){
    return (new Date(date1).getTime() - new Date(date2).getTime());
}

export function date_difference_in_s(date1, date2){
    return date_difference_in_ms(date1, date2) / 1000;
}

export function date_difference_in_m(date1, date2){
    return date_difference_in_ms(date1, date2) / 1000 / 60;
}

export function interval_to_seconds(interval){
    const elements = interval.split(":");
    return (elements[0]) * 60 * 60 + (elements[1]) * 60 + elements[2];
}
