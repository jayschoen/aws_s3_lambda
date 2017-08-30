function status_loop() {
    
    let form_data = new FormData(document.getElementById('image_resize_form'));

    let filename; 
    
    submit_obs = Rx.Observable.fromPromise(
        fetch("http://127.0.0.1:5000/", { 
            method: 'POST', 
            body: form_data 
        }))
            // run a fn() on the thing
            .map(response => {
                // check if the response code is between x and z
                if (response.status >= 400 && response.status < 600) {
                    // initialize a new error with the appropriate status text
                    let error = new Error(response.statusText);
                    // add a property to the error... set it's value to the response object
                    error.response = response
                    throw error;
                }
                // make sure to do this so the chain can continue down to the next observable
                else {
                    return response;
                }
            }) 
            // flatMap() expects a promise... turns it into an observable
            // then we can get the response text every time the original observable (in this case, a promise)
            // emits new data
            .flatMap(response => { console.log(response); return response.text() })
            // do() lets us do something to the emitted data
            .do(response => { console.log(response); filename = response; })
    
    checkstatus_obs = Rx.Observable
        // time a timer... 0 == start immediately, 5000 == every 5 seconds do X
        .timer(0, 5000)
        // turn the response object into another observable and fetch() every time data is emitted
        .switchMap(response => fetch("http://127.0.0.1:5000/status?filename=" + filename))
        // turn the response object into another observable and extract the response text every time data is emitted
        .flatMap(response => response.json())
        .do(response => { console.log(response.status); display_status(response); })
        .filter(response => response.status === 'file_ready') 
        .take(1)
        .timeout(15000);

    // initiate submit_obs... we don't care about it's return value
    // so pass nothing to flatMap... which passes nothing to checkstatus_obs
    // but initiate checkstatus_obs, then subscribe to it and check it's result
    final_obs = submit_obs.flatMap(() => checkstatus_obs)

    final_obs.subscribe(
        // arg1 = emitted, arg2 = error, arg3 = completed (only happens if no error!)
        // emitted data
        response => { console.log('chicken'); console.log(response); },
        // error
        error => {
            console.log(error); 
            // if the error has a "response" property
            if (error.response) {
                if (error.response.status == 413) {
                    display_status({'status': 'File too large.'});
                }
            }
        },
        // completed
        () => console.log('completed')
    ); 
}

function display_status(response) {
    if (response.status == 'file_ready'){
        document.getElementById('status').innerHTML = '<a href="' + response.url + '">' + '<img src="' + response.url + '">' + '</a>';
    }
    else {
        document.getElementById('status').innerHTML = response.status;
    }
}
