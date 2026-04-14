import publicWidget from "@web/legacy/js/public/public_widget";
import {rpc} from "@web/core/network/rpc";

publicWidget.registry.statistics = publicWidget.Widget.extend({
    selector: ".chart-statistics",
    async start() {
        const datas = await rpc("/web/dataset/call_kw", {
            model: "res.users",
            method: "get_statistics_char",
            args: [],
            kwargs: {},
        });
        const backgroundColor = datas.map((d) => d.color);
        const value = datas.map((d) => d.value);
        const data = {
            labels: [
                "Janv.",
                "Fev.",
                "Mars",
                "Avril",
                "Mai",
                "Juin",
                "Juil.",
                "Août",
                "Sept.",
                "Oct.",
                "Nov.",
                "Dec.",
            ],
            datasets: [
                {
                    label: "Chiffre d'affaires mensuel (k€ TTC)",
                    hoverBackgroundColor: "#efeb1d",
                    backgroundColor: backgroundColor,
                    data: value,
                },
            ],
        };
        const options = {
            tooltips: {
                callbacks: {
                    label: (tooltipItem) => Math.round(tooltipItem.yLabel * 100) / 100,
                },
            },
            legend: {display: false},
            maintainAspectRatio: false,
            scales: {
                yAxes: [
                    {
                        stacked: true,
                        gridLines: {display: true, color: "rgba(255,99,132,0.2)"},
                    },
                ],
                xAxes: [{gridLines: {display: false}}],
            },
        };
        // Chart.js 2.5 loaded via CDN ir.asset
        Chart.Bar("chart", {options, data}); // eslint-disable-line no-undef
    },
});
