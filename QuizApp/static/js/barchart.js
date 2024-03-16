function report(last, max, best=null, question_nr){
    let last_points = {
                label: "Your points",
                backgroundColor: "moccasin",
                data: last
            };
    let max_points = {
                label: "Maximum points",
                backgroundColor: "blue",
                data: max
            };
    let points = [last_points];
    if (best != false) {
        let best_points = {
            label: "Best points",
            backgroundColor: "gold",
            data: best
        };
        points[1] = best_points;
        points[2] = max_points;
    } else {
        points[1] = max_points;
    }
    let xValues = []
    for (let q = 1; q<question_nr; q++) {
        xValues[q-1] = "Q"+q.toString();
    }
    new Chart("questions", {
        type: "bar",
        data: {
            labels: xValues,
            datasets: points
        },
        options: {
            legend: {display: true},
            scales: {
              yAxes: [{
                ticks: {
                  min: 0,
                }
              }]
            },
            min: 0
        }
    });
}