/**
 * Created by matuuar on 28/12/15.
 */

graphResumenCostosBar = function (serie1) {
    var chart = nv.models.discreteBarChart()
        .options({
            margin: {left: 150, bottom: 220},
            showXAxis: true,
            showYAxis: true,
            transitionDuration: 250,
            noData: "No hay datos de costos para el periodo seleccionado.",
        });

    chart.xAxis
        .axisLabel("CC")
        .rotateLabels(-45)
        .tickFormat(function (d) {
            return d
        });
    var commasFormatter = d3.format(",");
    chart.yAxis
        .axisLabel('')
        .tickFormat(function (d) {
            return "$" + commasFormatter(d);
        });

    d3.select("#resumen>svg")
        .datum([
            {
                values: serie1,
                key: "Resumen de costos",
                color: "#2ca02c"
            }])
        .transition().duration(1200)
        .call(chart);


    nv.utils.windowResize(function () {
        chart.update();
    });
    return chart;
};

graphResumenCostosPie = function (serie1) {

    var chart = nv.models.pieChart()
        .options({
            showXAxis: true,
            showYAxis: true,
            transitionDuration: 250,
            noData: "No hay datos de costos para el periodo seleccionado.",
            labelType: "percent",
            donut: true,
            donutRatio: 0.3
        });

    d3.select("#resumen-pie>svg")
        .datum(serie1)
        .transition().duration(1200)
        .call(chart);
    nv.utils.windowResize(function () {
        chart.update();
    });
    return chart;
};

graphCostosVentasBar = function(serie1, serie2, serie3) {
    var chart = nv.models.multiBarChart().options({
        transitionDuration: 250,
        noData: "No hay datos para el periodo seleccionado.",
        margin: {left: 150, bottom: 220},
        showXAxis: true,
        showYAxis: true,
        groupSpacing: 0.1,
        showControls: true
    });

    chart.xAxis
        .axisLabel("CC")
        .rotateLabels(-45)
        .tickFormat(function (d) {
            return d
        });
    var commasFormatter = d3.format(",");
    chart.yAxis
        .axisLabel('')
        .tickFormat(function (d) {
            return "$" + commasFormatter(d);
        });

    d3.select('#resumen-costos-ventas>svg')
        .datum([
            {
                values: serie1,
                key: "Costos",
                color: "#ff4f0e"
            },
            {
                values: serie2,
                key: "Ventas",
                color: "#2ca02c"

            },
            {
                values: serie3,
                key: "Certif. Internas",
                color: "#31708F"

            },
        ])
            .transition()
            .duration(1200)
            .call(chart);

    nv.utils.windowResize(chart.update);
    return chart;
};
