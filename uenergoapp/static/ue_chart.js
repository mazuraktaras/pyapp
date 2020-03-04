window.onload = function () {

    $('#inputURL').bootstrapValidator({
        feedbackIcons: {
            valid: 'glyphicon glyphicon-ok',
            invalid: 'glyphicon glyphicon-remove',
            validating: 'glyphicon glyphicon-refresh'
        }
    });

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

    //$.getJSON("/tagscount", addData);


    $.getJSON("/tagscount", function (data) {
        $.each(data, function (key, value) {
            dataPoints.push({label: value.tag_name, y: value.tag_count});
            console.log('Its key', key, 'Its value', value.tag_name);
        });
        chart.render();
    });

};

