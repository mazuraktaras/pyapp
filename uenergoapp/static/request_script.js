function getLiveFlightsCount() {

    let request = new XMLHttpRequest();

    request.onload = function () {

        console.log(this.responseText);

        document.getElementById('live_flights_count').innerText = this.responseText;
    };

    request.open('GET', '/terminal', true);
    request.send();

}

getLiveFlightsCount();
setInterval(getLiveFlightsCount, 7000);