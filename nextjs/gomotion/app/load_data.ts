"use client";
import { SetStateAction, Dispatch } from "react";
import {
  getMapData,
  getWeeklyTraffic,
  getMonthlyTraffic,
  getAverageEventImpact,
  getRainIntensityCorrelation,
  getWorkdayVsHoliday,
  getIntensityPerArea,
  getWeeklyIntensityDiff,
  getMonthlyIntensityDiff,
  getModelImportances,
} from "./server_data";

export async function loadWeeklyTraffic(
  setter: Dispatch<SetStateAction<any>>,
  barri: string,
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
  barri: string,
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
  barri: string,
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
  barri: string,
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
  barri: string,
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
  barri: string,
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

  setter({ x: x, y: y, text: hover, selectedBarri: barri });
}

export async function loadMapData(
  setter: Dispatch<SetStateAction<any>>,
  barri: string,
  day: string,
) {
  const result = await getMapData(day);

  var zScores: Record<string, number> = {};
  for (const rowIndex in result) {
    zScores[result[rowIndex]["barri"]] = result[rowIndex]["zscore"];
  }

  setter({
    zScores: zScores,
    selectedBarri: barri,
  });
}

export async function loadWeeklyIntensityDiff(
  setter: Dispatch<SetStateAction<any>>,
) {
  const result = await getWeeklyIntensityDiff();

  var x = [];
  var y = [];
  for (const rowIndex in result) {
    x.push(result[rowIndex]["dotw"]);
    y.push(result[rowIndex]["avg"]);
  }
  setter({ x: x, y: y });
}

export async function loadMonthlyIntensityDiff(
  setter: Dispatch<SetStateAction<any>>,
) {
  const result = await getMonthlyIntensityDiff();

  var x = [];
  var y = [];
  for (const rowIndex in result) {
    x.push(result[rowIndex]["month"]);
    y.push(result[rowIndex]["avg"]);
  }
  setter({ x: x, y: y });
}

export async function loadModelImportances(
  setter: Dispatch<SetStateAction<any>>,
) {
  const result = await getModelImportances();

  var x = [];
  var y = [];
  var eventImportance: number = 0;
  for (const rowIndex in result) {
    if ("enc" === result[rowIndex]["features"].substring(0, 3)) {
      eventImportance += result[rowIndex]["importances"];
    } else {
      x.push(result[rowIndex]["importances"]);
      y.push(result[rowIndex]["features"]);
    }
  }

  x.push(eventImportance);
  y.push("events");

  x = x.reverse();
  y = y.reverse();

  setter({ x: x, y: y });
}
