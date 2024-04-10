// Global variable to store the fetched stock data and the stock chart instance
var globalStockData;
var stockChart;

$(document).ready(function() {
    Chart.defaults.font.family = 'Segoe UI, Tahoma, Geneva, Verdana, sans-serif';
    Chart.defaults.font.size = 14;
    Chart.defaults.font.color = '#0a558c';
    $('#get-data').on('click', function() {
        var stockCode = $('#stock_code').val();
        var daysPast = $('#days_past').val();
        var predictionModel = $('#prediction_model').val(); // Ensure this is included in your form
        
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
                    createOrUpdateChart(data);
                    $('#predict').show(); // Make the predict button visible after data is fetched
                },
                error: function(error) {
                    console.error("Error fetching stock data: ", error);
                }
            });
        }
    });

    $('#predict').on('click', function() {
        var daysPast = $('#days_past').val();
        var predictionModel = $('#prediction_model').val();
        
        if (globalStockData && daysPast && predictionModel) {
            $.ajax({
                type: 'POST',
                url: '/predict',
                contentType: "application/json",
                dataType: "json",
                data: JSON.stringify({
                    data: globalStockData,
                    days_past: daysPast,
                    prediction_model: predictionModel
                }),
                success: function(response) {
                    var prediction = response.prediction;
                    createOrUpdateChart(globalStockData, prediction);
                    
                    // Now, also display the numerical prediction.
                    $('#prediction-result').text('Predicted closing price for the next day: ' + prediction.toFixed(2));
                    $('#prediction-result').show();
                },
                error: function(xhr, status, error) {
                    console.error("Error predicting stock price: ", xhr.responseText);
                }
            });
        }
    });
    
});

// Function to create or update the chart
function createOrUpdateChart(stockData, prediction) {
    var ctx = document.getElementById('stock-chart').getContext('2d');
    var labels = stockData.map(function(item) { return item.Date; });
    var data = stockData.map(function(item) { return item.Close; });

    // If a prediction is provided, add it to the data
    if (prediction !== undefined) {
        labels.push('Prediction');
        data.push(prediction);
    }

    if (stockChart) {
        stockChart.data.labels = labels;
        stockChart.data.datasets[0].data = data;
        stockChart.update();
    } else {
        stockChart = new Chart(ctx, {
            type: 'line',
            data: {
                labels: labels,
                datasets: [{
                    label: 'Stock Price',
                    data: data,
                    fill: false,
                    borderColor: 'rgb(75, 192, 192)',
                    tension: 0.1
                }]
            },
            options: {
                responsive: true,
                scales: {
                    y: {
                        beginAtZero: false
                    }
                }
            }
        });
    }
}
