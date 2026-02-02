"use client";
import { scaleLinear } from "d3-scale";
import SimpleBar from "simplebar-react";
import "simplebar-react/dist/simplebar.min.css";

const getColor = scaleLinear<string>()
  .domain([-3, 0, 3])
  .range(["#69298F", "#ca4679", "#FFD127"]);

import { useState, useEffect } from "react";
import { loadFinalPredictedDate } from "./load_data";

function classifyPeak(zscore: number) {
  if (zscore >= 1.5) return "Massive peak";
  if (zscore >= 1) return "Peak";
  return "No peak";
}

function Row(data: any) {
  return (
    <tr>
      <td className="text-left">{data["barri"]}</td>
      <td className="text-right">{Math.round(data["intensity"])}</td>
      <td className="text-right">{Math.round(data["mean"])}</td>
      <td className="text-right">{Math.round(data["density"])}</td>
      <td
        className="text-right"
        style={{ backgroundColor: getColor(data["zscore"]) }}
      >
        {Math.round(100 * data["zscore"]) / 100}
      </td>
      <td className="text-left">{classifyPeak(data["zscore"])}</td>
    </tr>
  );
}

export default function BarriInfo({ data, day, setter, fetcher }: any) {


  const [week_ahead, setWeekAhead] = useState("");

  useEffect(() => {
    if (fetcher) {
      loadFinalPredictedDate(fetcher, setWeekAhead);
    }
  }, [fetcher]);

  let rows: Array<any> = [];

  for (let i = 0; i < data["rows"].length; i++) {
    rows.push(Row(data["rows"][i]));
  }

  return (
    <div className="barri-info">
      <div className="date-selector">
        <p>SELECT DATE</p>
        <input
          type="date"
          value={day}
          onChange={(e) => setter(e.target.value)}
          id="dateInput"
          name="dateInput"
          max={week_ahead}
        />
      </div>

      <div className="table-container">
      <SimpleBar style={{maxHeight: "100%"}}>
        <table>
          <thead>
            <tr>
              <th className="text-left">Neighborhood</th>
              <th>Traffic</th>
              <th>Average</th>
              <th>Density</th>
              <th>Deviation</th>
              <th>Peak</th>
            </tr>
          </thead>
          <tbody>{...rows}</tbody>
        </table>
      </SimpleBar></div>
    </div>
  );
}
