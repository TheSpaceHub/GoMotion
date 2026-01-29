"use client";
import dynamic from "next/dynamic";

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

  var xtitle: string = "";
  var ytitle: string = "";
  var plotTitle: string = "";

  if (data == undefined)
    return <div className="plot">Plot for {type} could not be loaded.</div>;

  //make a copy (plotData) in order to keep the original data untouched
  var plotData: Record<string, any> = { ...data };
  //keep this for certain plots which need more traces to look gorgeous
  var additionalTraces: Array<any> = [];

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

    case "weekly intensity diff":
      xtitle = "";
      ytitle = "INTENSITY DIFF (%)";
      plotTitle = "WEEKLY INTENSITY DIFF";
      plotData["type"] = "scatter";
      plotData["x"] = t["dotw"];
      plotData["mode"]="markers";
      plotData["marker"] = {
        color: "#830101ff",
        size:12
      };
      break;

      case "monthly intensity diff":
      xtitle = "";
      ytitle = "INTENSITY DIFF (%)";
      plotTitle = "MONTHLY INTENSITY DIFF";
      plotData["type"] = "scatter";
      plotData["x"] = t["months"];
      plotData["mode"]="markers";
      plotData["marker"] = {
        color: "#a9b500ff",
        size:12
      };
      break;
    default:
      break;
  }

  return (
    <div className="plot">
      <Plot
        data={[plotData, ...additionalTraces]}
        layout={{
          autosize: true,
          showlegend: false,
          margin: { l: 20, r: 20, t: 20, b: 20 },
          xaxis: {
            automargin: true,
            title: { text: xtitle },
            gridcolor: "#cccccc",
          },
          yaxis: {
            automargin: true,
            title: { text: ytitle },
            gridcolor: "#cccccc",
          },
          paper_bgcolor: "#ffffff00",
          plot_bgcolor: "#ffffff00",
          font: {
            family: "system-ui",
            weight: "normal",
            color: window.matchMedia("(prefers-color-scheme: dark)").matches
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
    </div>
  );
}
