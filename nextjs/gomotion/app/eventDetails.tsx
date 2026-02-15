"use client";
import { scaleLinear } from "d3-scale";
import SimpleBar from "simplebar-react";
import "simplebar-react/dist/simplebar.min.css";
import { useState, useEffect } from "react";
import { loadFinalPredictedDate } from "./load_data";

// Helper to determine badge class
const getImpactClass = (val: number) => {
  if (val > 0.7) return "impact-badge impact-high";
  if (val > 0.4) return "impact-badge impact-med";
  return "impact-badge impact-low";
};

function Row(event: any, t: any, i: number) {
  return (
    <tr key={i}>
      <td>{event.category}</td>
      <td>{event.barri}</td>
      <td>
        <span className={getImpactClass(Number(event.impact))}>
          {Number(event.impact).toFixed(2)}
        </span>
      </td>
      <td style={{ whiteSpace: "normal", minWidth: "200px" }}>
        {event.description}
      </td>
    </tr>
  );
}

export default function EventDetails({ validEvents, t }: any) {
  if (validEvents.length == 0)
    return <div className="no-events-msg">{t.noEvents}</div>;

  let rows: Array<any> = [];

  for (let i = 0; i < validEvents.length; i++) {
    rows.push(Row(validEvents[i], t, i));
  }

  return (
    <div className="events-table-wrapper">
      <SimpleBar style={{ maxHeight: "100%" }}>
        <table>
          <thead>
            <tr>
              <th className="text-left">{t.category}</th>
              <th className="text-left">{t.barri}</th>
              <th className="text-left">{t.impact}</th>
              <th className="text-left">{t.description}</th>
            </tr>
          </thead>
          <tbody>{...rows}</tbody>
        </table>
      </SimpleBar>
    </div>
  );
}
