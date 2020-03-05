window.onload = function () {

    let dataPoints = [];
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
    chart.render();


    $('#ajax-button').click(function () {
        dataPoints.length = 0;
        //var newDP = [{label: "div1", y: 200}, {label: "div2", y: 100}, {label: "div3", y: 300}];
        //dataPoints.push({label: "div3", y: 300});
        //dataPoints.push({label: "div2", y: 200});
        //chart.render();
        //dataPoints.length = 0;
        console.log('DATAPOINTS', dataPoints);
        //dataPoints.push({label: "div", y: 200})
        //event.preventDefault();
        startTask($('#URLinput').val());
        //chart.render();

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


    function getTaskResult(status_url) {

        $.getJSON(status_url, function (data) {
            //console.log('DATAPOINTS', dataPoints)
            if (data.task_state = 'SUCCESS') {
                //console.log('Task state ===>', data.task_state);
                //console.log('Task state ===>', data.result_url);

                $.getJSON(data.result_url, function (data) {
                    $.each(data, function (key, value) {
                        dataPoints.push({label: value.tag_name, y: value.tag_count});
                        //console.log('Its key', key, 'Its value', value.tag_name);
                        console.log('Datapoints before each', dataPoints);
                        //chart.render();
                    });
                    //console.log('Datapoints after each', dataPoints);
                    chart.render();
                });
                //console.log('Datapoints after If', dataPoints);

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
};