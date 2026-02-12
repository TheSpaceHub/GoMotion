"use client";
import { scaleLinear } from "d3-scale";
import SimpleBar from "simplebar-react";
import "simplebar-react/dist/simplebar.min.css";
import { useState, useEffect } from "react";
import { loadFinalPredictedDate } from "./load_data";

const getColor = scaleLinear<string>()
  .domain([-3, 0, 3])
  .range(["#69298F", "#ca4679", "#FFD127"]);

function classifyPeak(zscore: number, t: any) {
  if (zscore >= 1.5) return t.table.massivePeak;
  if (zscore >= 1) return t.table.peak;
  return t.table.noPeak;
}

function Row(data: any, t: any) {
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
      <td className="text-left">{classifyPeak(data["zscore"], t)}</td>
    </tr>
  );
}

export default function BarriInfo({ data, day, setter, fetcher, t }: any) {
  const [week_ahead, setWeekAhead] = useState("");

  useEffect(() => {
    if (fetcher) {
      loadFinalPredictedDate(fetcher, setWeekAhead);
    }
  }, [fetcher]);

  let rows: Array<any> = [];

  for (let i = 0; i < data["rows"].length; i++) {
    rows.push(Row(data["rows"][i], t));
  }

  return (
    <div className="barri-info">
      <div className="date-selector">
        <p>{t.selectDate}</p>
        <input
          type="date"
          value={day}
          onFocus={(e) => e.target.blur()}
          onChange={(e) => setter(e.target.value)}
          onMouseDown={(e) => e.preventDefault()}
          onClick={(e) => e.currentTarget.showPicker()}
          id="dateInput"
          name="dateInput"
          max={week_ahead}
        />
      </div>

      <div className="table-container">
        <SimpleBar style={{ maxHeight: "100%" }}>
          <table>
            <thead>
              <tr>
                <th className="text-left">{t.barri}</th>
                <th>{t.table.traffic}</th>
                <th>{t.table.average}</th>
                <th>{t.table.density}</th>
                <th>{t.table.deviation}</th>
                <th>{t.table.peak}</th>
              </tr>
            </thead>
            <tbody>{...rows}</tbody>
          </table>
        </SimpleBar>
      </div>
    </div>
  );
}
