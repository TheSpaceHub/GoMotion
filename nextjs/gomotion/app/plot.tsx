"use client";
import dynamic from "next/dynamic";
import { scaleLinear } from "d3-scale";

//returns color depending on importance
const getImportanceColor = scaleLinear<string>()
  .domain([0, 0.5, 1])
  .range(["#69298F", "#ca4679", "#FFD127"]);

const getDiffColor = scaleLinear<string>()
  .domain([-0.5, 0, 0.25])
  .range(["#69298F", "#ca4679", "#FFD127"]);

const Plot = dynamic(() => import("react-plotly.js"), {
  ssr: false,
});

interface PlotComponentParameters {
  t: any;
  type: string;
  isLoading: boolean;
  data: any;
}

export default function PlotComponent({
  t,
  type,
  isLoading,
  data,
}: PlotComponentParameters) {
  if (isLoading) return <div className="plot">Loading...</div>;

  let xtitle: string = "";
  let ytitle: string = "";
  let plotTitle: string = "";

  if (data == undefined)
    return <div className="plot">Plot for {type} could not be loaded.</div>;

  //make a copy (plotData) in order to keep the original data untouched
  let plotData: Record<string, any> = { ...data };
  //keep this for certain plots which need more traces to look gorgeous
  let additionalTraces: Array<any> = [];

  let additionalYLayout = {};

  //more layout customization
  let show_legend: boolean = false;
  let show_grid: boolean = true;

  //display logic for all plots
  switch (type) {
    case "weekly traffic":
      xtitle = "";
      ytitle = "AVG. INTENSITY";
      plotTitle = "WEEKLY TRAFFIC";

      plotData["type"] = "bar";
      plotData["x"] = t["dotw"];
      plotData["marker"] = {
        color: "#6275bc",
      };
      break;

    case "monthly traffic":
      xtitle = "";
      ytitle = "AVG. INTENSITY";
      plotTitle = "MONTHLY TRAFFIC";

      plotData["type"] = "scatter";
      plotData["x"] = t["months"];
      plotData["marker"] = {
        color: "#bc6262",
      };
      plotData["fill"] = "tozeroy";
      plotData["fillcolor"] = "#bc626288";
      break;

    case "average event impact":
      xtitle = "";
      ytitle = "";
      plotTitle = "AVG. EVENT IMPACT";

      plotData["type"] = "bar";
      plotData["orientation"] = "h";
      plotData["marker"] = {
        color: "#8462bc",
      };
      break;

    case "rain/intensity correlation":
      xtitle = "";
      ytitle = "INTENSITY";
      plotTitle = "INTENSITY PER PRECIPITATION";

      plotData["type"] = "scatter";
      plotData["mode"] = "markers";
      //plotData["hoverinfo"] = "text";
      plotData["marker"] = {
        color: "#8dbbc6",
        opacity: 0.5,
      };
      break;

    case "workday vs holiday":
      xtitle = "";
      ytitle = "";
      plotTitle = "WORKDAY VS HOLIDAY";

      plotData["type"] = "box";
      plotData["x"] = plotData["x"].map((val: any) =>
        val == "1" ? t["holiday"].toUpperCase() : t["workday"].toUpperCase(),
      );
      plotData["marker"] = {
        color: "#a562bc",
      };
      break;

    case "intensity/area":
      xtitle = "";
      ytitle = "AVG. INTENSITY";
      plotTitle = "INTENSITY PER AREA";

      plotData["type"] = "scatter";
      plotData["mode"] = "markers";
      plotData["hoverinfo"] = "text";
      plotData["marker"] = {
        color: "#58585e",
        opacity: 0.5,
      };

      const selectedBarri: string = plotData["selectedBarri"];
      delete plotData["selectedBarri"];
      const selectedBarriIndex = plotData["text"].indexOf(selectedBarri);

      //highlight current barri
      if (selectedBarriIndex != -1)
        additionalTraces.push({
          x: [plotData["x"][selectedBarriIndex]],
          y: [plotData["y"][selectedBarriIndex]],
          type: "scatter",
          mode: "markers",
          hoverinfo: "skip",
          marker: {
            color: "#ff0000",
            opacity: 1,
          },
        });

      break;

    case "model importances":
      xtitle = "";
      ytitle = "";
      plotTitle = "SHAP FEATURE IMPORTANCES";

      show_grid = false;

      let bar_colors = [];

      for (let i = 0; i < plotData["x"].length; i++) {
        bar_colors.push(getImportanceColor(plotData["x"][i]));
      }

      plotData["type"] = "bar";
      plotData["orientation"] = "h";
      plotData["marker"] = {
        color: bar_colors,
      };
      //add a little bit of separation
      additionalYLayout = { ticksuffix: "   " };
      break;

    case "model stats":
      const map_stats_text: Record<string, string> = {
        model_accuracy: "Accurate",
        model_error_over: "Overestimation",
        model_error_under: "Underestimation",
      };

      const pie_palette: string[] = ["#FFD127", "#ffa800", "#69298F"];

      xtitle = "";
      ytitle = "";
      plotTitle = "MODEL PRECISION";

      let pieLabels = [...plotData["labels"]];

      for (let i = 0; i < pieLabels.length; i++) {
        pieLabels[i] = map_stats_text[pieLabels[i]];
      }

      plotData["labels"] = pieLabels;
      plotData["type"] = "pie";
      plotData["marker"] = {
        colors: pie_palette,
      };
      show_legend = true;

      break;

    case "weekly intensity diff":
      xtitle = "";
      ytitle = "INTENSITY DIFF (%)";
      plotTitle = "WEEKLY INTENSITY DIFF";
      plotData["type"] = "scatter";
      plotData["x"] = t["dotw"];
      plotData["mode"] = "markers";
      //do color
      let weeklyMarkerColors = [];
      for (let i = 0; i < plotData["y"].length; i++) {
        weeklyMarkerColors.push(getDiffColor(plotData["y"][i] / 100));
      }
      plotData["marker"] = {
        color: weeklyMarkerColors,
        size: 12,
      };
      break;

    case "monthly intensity diff":
      xtitle = "";
      ytitle = "INTENSITY DIFF (%)";
      plotTitle = "MONTHLY INTENSITY DIFF";
      plotData["type"] = "scatter";
      plotData["x"] = t["months"];
      plotData["mode"] = "markers";
      //do color
      let monthlyMarkerColors = [];
      for (let i = 0; i < plotData["y"].length; i++) {
        monthlyMarkerColors.push(getDiffColor(plotData["y"][i] / 100));
      }
      plotData["marker"] = {
        color: monthlyMarkerColors,
        size: 12,
      };
      break;
    default:
      break;
  }

  return (
    <Plot
      data={[plotData, ...additionalTraces]}
      layout={{
        autosize: true,
        showlegend: show_legend,
        margin: { l: 20, r: 20, t: 20, b: 20 },
        xaxis: {
          automargin: true,
          title: { text: xtitle },
          gridcolor: "#cccccc",
          showgrid: show_grid,
        },
        yaxis: {
          automargin: true,
          title: { text: ytitle },
          gridcolor: "#cccccc",
          showgrid: show_grid,
          ...additionalYLayout,
        },
        paper_bgcolor: "#ffffff00",
        plot_bgcolor: "#ffffff00",
        font: {
          family: "system-ui",
          weight: "normal",
          color: window.matchMedia("(prefers-color-scheme: dark)").matches //dark mode
            ? "#ffffff"
            : "#171717",
        },
        title: {
          text: plotTitle,
          font: { size: 16, family: "system-ui", weight: "bold" },
          x: 0.5,
          xanchor: "center",
          y: 1,
          yanchor: "top",
        },
      }}
      useResizeHandler={true}
      style={{ width: "100%", height: "100%", margin: "0", padding: "0" }}
      config={{ displayModeBar: false }}
    />
  );
}
