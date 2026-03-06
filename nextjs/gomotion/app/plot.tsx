"use client";
import dynamic from "next/dynamic";
import { scaleLinear } from "d3-scale";

//returns color depending on importance
const getImportanceColor = scaleLinear<string>()
  .domain([0, 0.5, 1])
  .range(["#69298F", "#ca4679", "#FFD127"]); // GoMotion gradient

const getDiffColor = scaleLinear<string>()
  .domain([-0.5, 0, 0.25])
  .range(["#69298F", "#ca4679", "#FFD127"]);

const Plot = dynamic(() => import("react-plotly.js"), {
  ssr: false,
});

interface PlotComponentParameters {
  t: any;
  type: string;
  isLoading: number;
  data: any;
}

export default function PlotComponent({
  t,
  type,
  isLoading,
  data,
}: PlotComponentParameters) {
  let xtitle: string = "";
  let ytitle: string = "";
  let plotTitle: string = "";

  if (data == undefined) {
    if (isLoading > 0) return <div>Loading...</div>;
    return <div>Plot for {type} could not be loaded.</div>;
  }

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
      ytitle = t.avgIntensity;
      plotTitle = t.weeklyTraffic;

      plotData["type"] = "bar";
      plotData["x"] = t["dotw"];
      plotData["marker"] = {
        color: "#69298F", // GoMotion Purple
        opacity: 0.9,
      };
      plotData["hoverinfo"] = "y+name";
      break;

    case "monthly traffic":
      xtitle = "";
      ytitle = t.avgIntensity;
      plotTitle = t.monthlyTraffic;

      plotData["type"] = "scatter";
      plotData["x"] = t["months"];
      plotData["line"] = {
        color: "#FFD127", // GoMotion Yellow
        shape: "spline",
        width: 3,
      };
      plotData["fill"] = "tozeroy";
      plotData["fillcolor"] = "rgba(255, 209, 39, 0.15)"; // Soft yellow opacity
      break;

    case "average event impact":
      xtitle = "";
      ytitle = "";
      plotTitle = t.avgEventImpact;

      plotData["type"] = "bar";
      plotData["orientation"] = "h";
      plotData["marker"] = {
        color: "#FFD127",
        opacity: 0.9,
      };
      break;

    case "rain/intensity correlation":
      xtitle = "";
      ytitle = t.intensity;
      plotTitle = t.intensityPerRain;

      plotData["type"] = "scatter";
      plotData["mode"] = "markers";
      plotData["marker"] = {
        color: "#69298F",
        size: 8,
        opacity: 0.8,
        line: {
          color: "white",
          width: 0.5,
        },
      };
      break;

    case "workday vs holiday":
      xtitle = "";
      ytitle = "";
      plotTitle = t.workVsHoliday;

      plotData["type"] = "box";
      plotData["x"] = plotData["x"].map((val: any) =>
        val == "1" ? t["holiday"].toUpperCase() : t["workday"].toUpperCase(),
      );
      plotData["marker"] = {
        color: "#69298F", // GoMotion Purple
      };
      plotData["boxpoints"] = "outliers";
      break;

    case "intensity/area":
      xtitle = "";
      ytitle = t.avgIntensity;
      plotTitle = t.intensityPerArea;

      plotData["type"] = "scatter";
      plotData["mode"] = "markers";
      plotData["hoverinfo"] = "text";
      plotData["marker"] = {
        color: "#475569", // Use robust grey for rest
        size: 8,
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
            color: "#FFD127", // Highlight in GoMotion yellow
            size: 11,
            opacity: 1,
            line: { color: "#69298F", width: 1.5 },
          },
        });

      break;

    case "model importances":
      xtitle = "";
      ytitle = "";
      plotTitle = t.shap;

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
        model_accuracy: t.accurate,
        model_error_over: t.overestimation,
        model_error_under: t.underestimation,
      };

      const pie_palette: string[] = ["#FFD127", "#ca4679", "#69298F"];

      xtitle = "";
      ytitle = "";
      plotTitle = t.modelPrecision;

      let pieLabels = [...plotData["labels"]];

      for (let i = 0; i < pieLabels.length; i++) {
        pieLabels[i] = map_stats_text[pieLabels[i]];
      }

      plotData["labels"] = pieLabels;
      plotData["type"] = "pie";
      plotData["marker"] = {
        colors: pie_palette,
        line: { color: "transparent", width: 2 },
      };
      plotData["hoverinfo"] = "label+percent";
      plotData["hole"] = 0.4; // Make it a donut chart
      show_legend = true;

      break;

    case "weekly intensity diff":
      xtitle = "";
      ytitle = t.intensityDiff;
      plotTitle = t.weeklyIntensityDiff;
      plotData["type"] = "scatter";
      plotData["x"] = t["dotw"];
      plotData["line"] = {
        color: "#FFD127", // GoMotion yellow
        shape: "spline",
        width: 3,
      };
      plotData["fill"] = "tozeroy";
      plotData["fillcolor"] = "rgba(255, 209, 39, 0.15)";
      plotData["mode"] = "lines+markers";
      //do color
      let weeklyMarkerColors = [];
      for (let i = 0; i < plotData["y"].length; i++) {
        weeklyMarkerColors.push(getDiffColor(plotData["y"][i] / 100));
      }
      plotData["marker"] = {
        color: weeklyMarkerColors,
        size: 10,
        line: { color: "white", width: 1.5 },
      };
      break;

    case "monthly intensity diff":
      xtitle = "";
      ytitle = t.intensityDiff;
      plotTitle = t.monthlyIntensityDiff;
      plotData["type"] = "scatter";
      plotData["line"] = {
        color: "#FFD127", // GoMotion yellow
        shape: "spline",
        width: 3,
      };
      plotData["fill"] = "tozeroy";
      plotData["fillcolor"] = "rgba(255, 209, 39, 0.15)";
      plotData["x"] = t["months"];
      plotData["mode"] = "lines+markers";
      //do color
      let monthlyMarkerColors = [];
      for (let i = 0; i < plotData["y"].length; i++) {
        monthlyMarkerColors.push(getDiffColor(plotData["y"][i] / 100));
      }
      plotData["marker"] = {
        color: monthlyMarkerColors,
        size: 8,
        line: { color: "white", width: 1 },
      };
      break;
    default:
      break;
  }

  const isDark = window.matchMedia("(prefers-color-scheme: dark)").matches;

  return (
    <Plot
      data={[plotData, ...additionalTraces]}
      layout={{
        autosize: true,
        showlegend: show_legend,
        margin: { l: 40, r: 20, t: 40, b: 30 },
        xaxis: {
          automargin: true,
          title: {
            text: xtitle,
            font: { size: 12, color: isDark ? "#94a3b8" : "#64748b" },
          },
          gridcolor: isDark ? "#334155" : "#e2e8f0",
          gridwidth: 1,
          griddash: "dot",
          showgrid: show_grid,
          zerolinecolor: isDark ? "#475569" : "#cbd5e1",
          tickfont: { color: isDark ? "#94a3b8" : "#64748b" },
        },
        yaxis: {
          automargin: true,
          title: {
            text: ytitle,
            font: { size: 12, color: isDark ? "#94a3b8" : "#64748b" },
          },
          gridcolor: isDark ? "#334155" : "#e2e8f0",
          gridwidth: 1,
          griddash: "dot",
          showgrid: show_grid,
          zerolinecolor: isDark ? "#475569" : "#cbd5e1",
          tickfont: { color: isDark ? "#94a3b8" : "#64748b" },
          ...additionalYLayout,
        },
        paper_bgcolor: "transparent",
        plot_bgcolor: "transparent",
        font: {
          family: "'Inter', 'Lexend', system-ui, sans-serif",
          weight: "normal",
          color: isDark ? "#f8fafc" : "#0f172a",
        },
        title: {
          text: plotTitle,
          font: {
            size: 16,
            weight: 600,
            color: isDark ? "#f8fafc" : "#0f172a",
          },
          x: 0.5,
          xanchor: "center",
          y: 0.95,
          yanchor: "top",
        },
        hoverlabel: {
          bgcolor: isDark ? "#1e293b" : "#ffffff",
          bordercolor: isDark ? "#334155" : "#e2e8f0",
          font: {
            family: "'Inter', sans-serif",
            color: isDark ? "#f8fafc" : "#0f172a",
          },
        },
      }}
      useResizeHandler={true}
      style={{ width: "100%", height: "100%", margin: "0", padding: "0" }}
      config={{ displayModeBar: false, responsive: true }}
    />
  );
}
