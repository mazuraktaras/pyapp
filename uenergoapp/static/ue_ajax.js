window.onload = function () {
    //Assign a global for datapoints  in chart
    let dataPoints = [];

    //Initialise chart object
    let chart = new CanvasJS.Chart("chartContainer", {
        animationEnabled: true,
        title: {
            text: "Tags count in document",
            fontFamily: "tahoma",
            fontSize: 30,
        },
        axisX: {
            interval: 1,
            labelAngle: 45,
            labelWrap: true,
            labelFontFamily: "tahoma",
            labelFontSize: 18,

        },
        axisY: {
            labelWrap: true,
            labelFontFamily: "tahoma",
            labelFontSize: 18,

        },
        data: [{
            type: "column",
            showInLegend: false,
            indexLabel: "{y}",
            indexLabelFontFamily: "tahoma",
            indexLabelFontSize: 18,
            indexLabelPlacement: "outside",
            indexLabelOrientation: "horizontal",
            //legendText: "{indexLabel}",
            dataPoints: dataPoints
        }]
    });
    //Render an empty chart
    chart.render();

    //Handler for the button
    $('#ajax-button').click(function () {
        //Empty chart datapoints on each request
        dataPoints.length = 0;
        //Get input URL value and start a task function
        startTask($('#URLinput').val());

    });


    function startTask(url) {

        //Send the POST with desired URL to backend to start
        // a background task and obtain URL where a task status is.
        //URL with task id returned in Location header

        $.ajax({
            type: 'POST',
            url: '/start',
            data: {'url': url},
            success: function (result, status, xhr) {
                status_url = xhr.getResponseHeader('Location');
                //If request with no errors start obtain result
                getTaskResult(status_url);
            },
            //If a backend error, popup alert
            error: function () {
                alert('Unexpected error on backend');
            }
        });
    }


    function getTaskResult(status_url) {

        //Obtain result from background tas as the JSON
        $.getJSON(status_url, function (data) {
            //Check is the background task performed, if yes get JSON data
            if (data.task_state == 'SUCCESS') {

                $.getJSON(data.result_url, function (data) {
                    //Get data and reassign the datapoints array with new values
                    $.each(data, function (key, value) {
                        dataPoints.push({label: value.tag_name, y: value.tag_count});
                    });
                    //Rerender chart
                    chart.render();
                });

            } else {
                //If the background task not ready invoke getting the task status each 1 s
                setTimeout(function () {
                    getTaskResult(status_url);
                }, 1000);
            }
        });

    }
};