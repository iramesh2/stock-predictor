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

        if (stockCode && daysPast) {
            $.ajax({
                type: 'POST',
                url: '/get_stock_data',
                data: {
                    stock_code: stockCode,
                    days_past: daysPast
                },
                success: function(response) {
                    globalStockData = response.history;
                    createOrUpdateChart(globalStockData);
                    updateDashboard(response.dashboard); // Update dashboard with new data
                    $('#predict').show();
                },
                error: function(error) {
                    console.error("Error fetching stock data: ", error);
                }
            });
        }
    });

    $('#predict').on('click', function() {
        var predictionModel = $('#prediction_model').val();

        if (globalStockData && predictionModel) {
            $.ajax({
                type: 'POST',
                url: '/predict',
                contentType: "application/json",
                dataType: "json",
                data: JSON.stringify({
                    data: globalStockData,
                    prediction_model: predictionModel
                }),
                success: function(response) {
                    var prediction = response.prediction;
                    globalStockData.push({
                        Date: `+1 day`, // Placeholder, you need actual date logic here
                        Close: prediction
                    });
                    createOrUpdateChart(globalStockData);
                    $('#prediction-result').text('Predicted closing price for the next day: ' + prediction.toFixed(2));
                    $('#prediction-result').show();
                    updateDashboard(response.dashboard); // If dashboard should include prediction results
                },
                error: function(xhr, status, error) {
                    console.error("Error predicting stock price: ", xhr.responseText);
                }
            });
        }
    });

    $('#undo-predict').on('click', function() {
        if (globalStockData.length > 0) {
            globalStockData.pop();
            createOrUpdateChart(globalStockData);
            $('#undo-predict').hide(); // Hide the undo button after undoing prediction
        }
    });
});

function createOrUpdateChart(stockData) {
    var ctx = document.getElementById('stock-chart').getContext('2d');
    var labels = stockData.map(function(item) { return item.Date; });
    var data = stockData.map(function(item) { return item.Close; });

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

function updateDashboard(dashboardData) {
    $('#current-price').text(dashboardData.currentPrice || 'N/A');
    $('#volume').text(dashboardData.volume || 'N/A');
    $('#market-cap').text(dashboardData.marketCap || 'N/A');
    // Show the dashboard section
    $('#stock-dashboard').show();
}
