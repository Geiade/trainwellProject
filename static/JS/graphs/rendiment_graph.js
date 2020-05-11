$(document).ready(function () {
    const d7 = new Date();
    d7.setDate(d7.getDate() - 7);
    document.getElementById('date_init_rendiment').valueAsDate = d7;
    document.getElementById('date_end_rendiment').valueAsDate = new Date();
    getData_rendiment_graph_promise();
});


function getData_rendiment_graph_promise() {
    let dateInitSelected = document.getElementById('date_init_rendiment').value;
    let dateEndSelected = document.getElementById('date_end_rendiment').value;

    let url = "/manager/graphs/api/rendiment?";
    if (dateInitSelected !== "" && dateEndSelected !== "") {
        url = url + "init_data=" + dateInitSelected + "&end_data=" + dateEndSelected;
    }

    let xhr = new XMLHttpRequest();
    xhr.onreadystatechange = function () {
        if (xhr.readyState === 4 && xhr.status === 200) {
            console.log(xhr.responseText)
            draw_chart_rendiment()
        } else if (xhr.readyState === 4) {
            console.log("error")
        } else {
            // Error or loading
        }
    };
    xhr.open("GET", url, true);
    xhr.send(null);

}

function draw_chart_rendiment() {
    const ctx_rendiment = document.getElementById('canvas_rendiment_graph').getContext('2d');
    const myChart = new Chart(ctx_rendiment, {
        type: 'bar',
        data: {
            labels: ['Red', 'Blue', 'Yellow', 'Green', 'Purple', 'Orange'],
            datasets: [{
                label: '# of Votes',
                data: [12, 19, 3, 5, 2, 3],
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
                        beginAtZero: true
                    }
                }]
            }
        }
    });
}


