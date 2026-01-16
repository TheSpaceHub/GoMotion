"use client";
import { SetStateAction, Dispatch } from "react";
import { getWeeklyTraffic } from "./server_data";

export async function loadWeeklyTraffic(
  setter: Dispatch<SetStateAction<any>>,
  barri: string
) {
  const result = await getWeeklyTraffic(barri);

  var x = [];
  var y = [];
  for (const rowIndex in result) {
    x.push(result[rowIndex]["dotw"]);
    y.push(result[rowIndex]["avg"]);
  }
  setter({ x: x, y: y });
}
