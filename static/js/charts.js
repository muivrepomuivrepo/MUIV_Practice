function prepareSimpleChartData(items) {
    return Object.entries(items || {}).map(function ([label, value]) {
        return { label: label, value: value };
    });
}
