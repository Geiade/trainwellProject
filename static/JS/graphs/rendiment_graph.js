$(document).ready(function () {
    const d7 = new Date();
    d7.setDate(d7.getDate() - 7);
    document.getElementById('date_init_rendiment').valueAsDate = d7;
    document.getElementById('date_end_rendiment').valueAsDate = new Date();
    getData_rendiment_graph();
});


function getData_rendiment_graph() {
    let dateInitSelected = document.getElementById('date_init_rendiment').value;
    let dateEndSelected = document.getElementById('date_end_rendiment').value;

    let init_valuedAsDate = document.getElementById('date_init_rendiment').valueAsDate;
    let end_valuedAsDate = document.getElementById('date_end_rendiment').valueAsDate;

    if (init_valuedAsDate < end_valuedAsDate) {
        document.getElementById('canvas_rendiment_graph').hidden = false;
        document.getElementById('error_rendiment_graph').innerText = "";
    } else if (init_valuedAsDate > end_valuedAsDate) {
        document.getElementById('canvas_rendiment_graph').hidden = true;
        document.getElementById('error_rendiment_graph').innerText = "WRONG DATES";
        return
    } else {
        document.getElementById('canvas_rendiment_graph').hidden = true;
        document.getElementById('error_rendiment_graph').innerText = "SAME DATES";
        return
    }

    let url = "/manager/graphs/api/rendiment?";
    if (dateInitSelected !== "" && dateEndSelected !== "") {
        url = url + "init_data=" + dateInitSelected + "&end_data=" + dateEndSelected;
    }

    let xhr = new XMLHttpRequest();
    xhr.onreadystatechange = function () {
        if (xhr.readyState === 4 && xhr.status === 200) {
            draw_chart_rendiment(xhr.responseText)
        } else if (xhr.readyState === 4) {
            console.log("error")
        } else {
            // Error or loading
        }
    };
    xhr.open("GET", url, true);
    xhr.send(null);

}

function draw_chart_rendiment(json_data) {
    json_data = JSON.parse(json_data);
    let keys = [];
    let values = [];

    Object.keys(json_data).forEach(function (key) {
        keys.push(key);
        values.push(json_data[key])
    });

    let stepSize = Math.max.apply(Math, values) / 5.0;

    const ctx_rendiment = document.getElementById('canvas_rendiment_graph').getContext('2d');

    if (typeof myChartRendiment != 'undefined') {
        myChartRendiment.destroy();
        myChartRendiment = new Chart(ctx_rendiment, {});
    }

    myChartRendiment = new Chart(ctx_rendiment, {
        type: 'bar',
        data: {
            labels: keys,
            datasets: [{
                label: '€',
                data: values,
                backgroundColor: [
                    'rgba(255, 99, 132, 0.2)',
                    'rgba(54, 162, 235, 0.2)',
                    'rgba(255, 206, 86, 0.2)',
                    'rgba(75, 192, 192, 0.2)',
                    'rgba(153, 102, 255, 0.2)',
                    'rgba(255, 159, 64, 0.2)'
                ],
                borderColor: [
                    'rgba(255, 99, 132, 1)',
                    'rgba(54, 162, 235, 1)',
                    'rgba(255, 206, 86, 1)',
                    'rgba(75, 192, 192, 1)',
                    'rgba(153, 102, 255, 1)',
                    'rgba(255, 159, 64, 1)'
                ],
                borderWidth: 1
            }]
        },
        options: {
            scales: {
                yAxes: [{
                    ticks: {
                        min: 0,
                        suggestedMax: Math.round(stepSize * 1.25 * 5.0),
                        beginAtZero: true,
                        stepSize: Math.round(stepSize),
                    }
                }]
            }
        }
    });
}


