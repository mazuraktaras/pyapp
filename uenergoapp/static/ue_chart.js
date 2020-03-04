let dataPoints = [{label: "div", y: 14}];
window.onload = function () {


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


    $('#ajax-button').click(function () {
        //dataPoints = [{label: "div", y: 200}];
        console.log('DATAPOINTS', dataPoints);
        //event.preventDefault();
        //startTask($('#url').val());
        chart.render();

    });

    $('#inputURLform').bootstrapValidator({
        feedbackIcons: {
            valid: 'glyphicon glyphicon-ok',
            invalid: 'glyphicon glyphicon-remove',
            validating: 'glyphicon glyphicon-refresh'
        }
    });


    /*
    function addData(data) {
        for (let i = 0; i < data.length; i++) {
            dataPoints.push({
                label: data[i].tag_name,
                y: data[i].tag_count
            });
        }
        //console.log(dataPoints);
        chart.render();

    }


     */

//$.getJSON("/tagscount", addData);


    function getTaskResult(status_url) {

        $.getJSON(status_url, function (data) {
            console.log('DATAPOINTS', dataPoints)
            if (data.task_state != 'PENDING') {
                console.log('Task state ===>', data.task_state);
                console.log('Task state ===>', data.result_url);

                $.getJSON(data.result_url, function (data) {
                    $.each(data, function (key, value) {
                        dataPoints.push({label: value.tag_name, y: value.tag_count});
                        console.log('Its key', key, 'Its value', value.tag_name);
                        console.log('Datapoints before each', dataPoints);
                    });
                    console.log('Datapoints after each', dataPoints);
                    //chart.render();
                });
                console.log('Datapoints after If', dataPoints);

            } else {

                console.log('Task state ===>', data.task_state)
                console.log('Task state ===>', data.task_id);
                setTimeout(function () {
                    getTaskResult(status_url);
                }, 1000);
                //setTimeout(getTaskResult(status_url), 1000);

            }

        });


    };

    function startTask(url) {


        $.ajax({
            type: 'POST',
            url: '/start',
            data: {'url': url},
            success: function (result, status, xhr) {
                status_url = xhr.getResponseHeader('Location');

                getTaskResult(status_url);


            },
            error: function () {
                alert('Unexpected error');
            }
        });
        console.log('Datapoints after STARTTask', dataPoints);


    };

    //chart.render();


    /*
    $.getJSON("/tagscount", function (data) {
        $.each(data, function (key, value) {
            dataPoints.push({label: value.tag_name, y: value.tag_count});
            console.log('Its key', key, 'Its value', value.tag_name);
        });
        chart.render();
    });

     */

};

