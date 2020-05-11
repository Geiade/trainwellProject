$(document).ready(function () {
    const d7 = new Date();
    d7.setDate(d7.getDate() - 7);
    document.getElementById('date_init_usage').valueAsDate = d7;
    document.getElementById('date_end_usage').valueAsDate = new Date();
    getData_usage_graph();
});


function getData_usage_graph() {
    let dateInitSelected = document.getElementById('date_init_usage').value;
    let dateEndSelected = document.getElementById('date_end_usage').value;

    let init_valuedAsDate = document.getElementById('date_init_usage').valueAsDate;
    let end_valuedAsDate = document.getElementById('date_end_usage').valueAsDate;

    if (init_valuedAsDate < end_valuedAsDate) {
        document.getElementById('canvas_usage_graph').hidden = false;
        document.getElementById('error_usage_graph').innerText = "";
    } else if (init_valuedAsDate > end_valuedAsDate) {
        document.getElementById('canvas_usage_graph').hidden = true;
        document.getElementById('error_usage_graph').innerText = "WRONG DATES";
        return
    } else {
        document.getElementById('canvas_usage_graph').hidden = true;
        document.getElementById('error_usage_graph').innerText = "SAME DATES";
        return
    }

    let url = "/manager/graphs/api/usage?";
    if (dateInitSelected !== "" && dateEndSelected !== "") {
        url = url + "init_data=" + dateInitSelected + "&end_data=" + dateEndSelected;
    }

    let xhr = new XMLHttpRequest();
    xhr.onreadystatechange = function () {
        if (xhr.readyState === 4 && xhr.status === 200) {
            console.log(xhr.responseText)
            draw_chart_usage(xhr.responseText)
        } else if (xhr.readyState === 4) {
            console.log("error")
        } else {
            // Error or loading
        }
    };
    xhr.open("GET", url, true);
    xhr.send(null);

}

function draw_chart_usage(json_data) {
    json_data = JSON.parse(json_data);
    let keys = [];
    let values = [];

    Object.keys(json_data).forEach(function (key) {
        keys.push(key);
        values.push(json_data[key])
    });

    const ctx_usage = document.getElementById('canvas_usage_graph').getContext('2d');

    if (typeof myChartUsage != 'undefined') {
        myChartUsage.destroy();
        myChartUsage = new Chart(ctx_usage, {});
    }


    myChartUsage = new Chart(ctx_usage, {
        type: 'bar',
        data: {
            labels: keys,
            datasets: [{
                label: '%',
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
                        max: 100,
                        beginAtZero: true,
                        stepSize: 25,
                    }
                }]
            }
        }
    });
}


