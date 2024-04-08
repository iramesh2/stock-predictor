// Global variable to store the fetched stock data
var globalStockData;
var stockChart;

$(document).ready(function() {
    $('#get-data').on('click', function() {
        var stockCode = $('#stock_code').val();
        var daysPast = $('#days_past').val();
        
        if (stockCode && daysPast) {
            $.ajax({
                type: 'POST',
                url: '/get_stock_data',
                data: {
                    stock_code: stockCode,
                    days_past: daysPast
                },
                success: function(data) {
                    globalStockData = data;
                    drawChart(data);
                    $('#predict').show();
                },
                error: function(error) {
                    console.error("Error fetching stock data: ", error);
                }
            });
        }
    });

    $('#predict').on('click', function() {
        var daysPast = $('#days_past').val();

        if (globalStockData && daysPast) {
            $.ajax({
                type: 'POST',
                url: '/predict',
                data: {
                    data: JSON.stringify(globalStockData),
                    days_past: daysPast
                },
                success: function(response) {
                    var prediction = response.prediction;
                    updateChartWithPrediction(prediction);
                },
                error: function(error) {
                    console.error("Error predicting stock price: ", error);
                }
            });
        }
    });
});

function drawChart(stockData) {
    var ctx = document.getElementById('stock-chart').getContext('2d');
    var labels = stockData.map(function(item) { return item.Date; });
    var data = stockData.map(function(item) { return item.Close; });
    
    if (stockChart) {
        stockChart.destroy();
    }

    stockChart = new Chart(ctx, {
        type: 'line',
        data: {
            labels: labels,
            datasets: [{
                label: 'Close Price',
                data: data,
                fill: false,
                borderColor: 'blue',
                borderWidth: 2
            }]
        },
        options: {
            responsive: true,
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

function updateChartWithPrediction(prediction) {
    stockChart.data.labels.push('Prediction');
    stockChart.data.datasets.forEach((dataset) => {
        dataset.data.push(prediction);
    });
    stockChart.update();
}
