"use client";
import { SetStateAction, Dispatch } from "react";
import {
  getWeeklyTraffic,
  getMonthlyTraffic,
  getAverageEventImpact,
  getRainIntensityCorrelation,
  getWorkdayVsHoliday,
  getIntensityPerArea,
} from "./server_data";

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

  var x = [];
  var y = [];
  for (const rowIndex in result) {
    y.push(result[rowIndex]["category"]);
    x.push(result[rowIndex]["avg"]);
  }

  setter({ x: x, y: y });
}

export async function loadRainIntensityCorrelation(
  setter: Dispatch<SetStateAction<any>>,
  barri: string
) {
  const result = await getRainIntensityCorrelation(barri);

  var x = [];
  var y = [];
  var hover = [];
  for (const rowIndex in result) {
    y.push(result[rowIndex]["intensity"]);
    x.push(result[rowIndex]["rain"]);
    hover.push(result[rowIndex]["day"]);
  }

  setter({ x: x, y: y, text: hover });
}

export async function loadWorkdayVsHoliday(
  setter: Dispatch<SetStateAction<any>>,
  barri: string
) {
  const result = await getWorkdayVsHoliday(barri);

  var x = [];
  var y = [];
  for (const rowIndex in result) {
    y.push(result[rowIndex]["intensity"]);
    x.push(result[rowIndex]["is_holiday"]);
  }

  setter({ x: x, y: y });
}

export async function loadIntensityPerArea(
  setter: Dispatch<SetStateAction<any>>,
  barri: string
) {
  const result = await getIntensityPerArea();

  var x = [];
  var y = [];
  var hover = [];
  for (const rowIndex in result) {
    y.push(result[rowIndex]["avg"]);
    x.push(result[rowIndex]["superficie"]);
    hover.push(result[rowIndex]["nom_barri"]);
  }

  setter({ x: x, y: y, text: hover, selectedBarri: barri});
}
