import numpy as np

def monte_carlo_simulation(start_price, days, mu, sigma, iterations):
    log_return = np.log(1 + mu)
    price_list = np.zeros([days, iterations])
    price_list[0] = start_price

    for t in range(1, days):
        shock = np.random.normal(log_return, sigma, iterations)
        price_list[t] = price_list[t - 1] * np.exp(shock)

    mean_end_price = np.mean(price_list[-1])
    sigma_end_price = np.std(price_list[-1])

    return mean_end_price, sigma_end_price
