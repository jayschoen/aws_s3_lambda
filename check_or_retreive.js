myObservable = Rx.Observable
	// time a timer... 0 == start immediately, 5000 == every 5 seconds do X
	.timer(0, 5000)
	.switchMap(response => fetch("http://127.0.0.1:5000/status"))
	.flatMap(response => response.text())
	.filter(response => response === 'exit') 
	.take(1)
	.timeout(15000);

myObservable.subscribe(
	// arg1 = emitted, arg2 = error, arg3 = completed (only happens if no error!)
	// emitted data
	response => console.log(response),
	// error
	error => console.log(error),
	// completed
	() => console.log('completed')
); 
