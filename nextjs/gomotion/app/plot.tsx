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
  switch (type) {
    case "weekly traffic":
      xtitle = "";
      ytitle = "AVG. INTENSITY";
      data["type"] = "bar";
      data["x"] = t["dotw"];
      break;
    default:
      break;
  }
  if (data == undefined)
    return <div className="plot">Plot for {type} could not be loaded.</div>;
  return (
    <div className="plot">
      <Plot
        data={[data]}
        layout={{
          autosize: true,
          margin: { l: 20, r: 20, t: 20, b: 20 },
          xaxis: { automargin: true, title: { text: xtitle } },
          yaxis: { automargin: true, title: { text: ytitle } },
        }}
        useResizeHandler={true}
        style={{ width: "100%", height: "100%", margin: "0", padding: "0" }}
        config={{ displayModeBar: false }}
      />
    </div>
  );
}
