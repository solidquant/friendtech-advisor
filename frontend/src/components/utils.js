const getPrice = (supply, amount) => {
    let sum1 = (supply == 0) ? 0 : (supply - 1) * supply * (2 * (supply - 1) + 1) / 6;
    let sum2 = (supply == 0 && amount == 1) ? 0 : (supply - 1 + amount) * (supply + amount) * (2 * (supply - 1 + amount) + 1) / 6;
    let summation = sum2 - sum1;
    return summation * (10 ** 18) / 16000;
};

export default {
    getPrice,
};