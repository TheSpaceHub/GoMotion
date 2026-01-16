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

  //display logic for all plots
  switch (type) {
    case "weekly traffic":
      xtitle = "";
      ytitle = "AVG. INTENSITY";
      plotTitle = "WEEKLY TRAFFIC";

      data["type"] = "bar";
      data["x"] = t["dotw"];
      data["marker"] = {
        color: "#6275bc",
      };
      break;

    case "monthly traffic":
      xtitle = "";
      ytitle = "AVG. INTENSITY";
      plotTitle = "MONTHLY TRAFFIC";

      data["type"] = "scatter";
      data["x"] = t["months"];
      data["marker"] = {
        color: "#bc6262",
      };
      data["fill"] = "tozeroy";
      data["fillcolor"] = "#bc626288";
      break;

    case "average event impact":
      xtitle = "";
      ytitle = "";
      plotTitle = "AVG. EVENT IMPACT";

      data["type"] = "bar";
      data["orientation"] = "h";
      data["marker"] = {
        color: "#8462bc",
      };
      break;

    default:
      break;
  }
  return (
    <div className="plot">
      <Plot
        data={[data]}
        layout={{
          autosize: true,
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
          font: { family: "system-ui", weight: "normal" },
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
