"use client";
import { SetStateAction, Dispatch } from "react";
import { getWeeklyTraffic, getMonthlyTraffic, getAverageEventImpact } from "./server_data";

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

export async function loadMonthlyTraffic(
  setter: Dispatch<SetStateAction<any>>,
  barri: string
) {
  const result = await getMonthlyTraffic(barri);

  var x = [];
  var y = [];
  for (const rowIndex in result) {
    x.push(result[rowIndex]["month"]);
    y.push(result[rowIndex]["avg"]);
  }
  setter({ x: x, y: y });
}

export async function loadAverageEventImpact(
  setter: Dispatch<SetStateAction<any>>,
  barri: string
) {
  const result = await getAverageEventImpact(barri);
  console.log(result)

  var x = [];
  var y = [];
  for (const rowIndex in result) {
    y.push(result[rowIndex]["category"]);
    x.push(result[rowIndex]["avg"]);
  }
  console.log(x);
  
  console.log(y);
  
  setter({ x: x, y: y });
}
