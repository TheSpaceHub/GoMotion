"use client";
import { SetStateAction, Dispatch, RefObject } from "react";
import {
  getTableData,
  getWeeklyTraffic,
  getMonthlyIntensityDiff,
  getMonthlyTraffic,
  getAverageEventImpact,
  getIntensityPerArea,
  getMapData,
  getModelImportances,
  getModelStats,
  getRainIntensityCorrelation,
  getWeeklyIntensityDiff,
  getWorkdayVsHoliday,
  getDailyData
} from "./server_data";
import { Fetcher } from "./page";

export async function loadTableData(
  fetcher: RefObject<Fetcher>,
  setter: Dispatch<SetStateAction<any>>,
  day: string,
) {
  const result = await getTableData(fetcher, day);
  setter({ rows: result });
}
export async function loadWeeklyTraffic(
  fetcher: RefObject<Fetcher>,
  setter: Dispatch<SetStateAction<any>>,
  barri: string,
) {
  const result = await getWeeklyTraffic(fetcher, barri);

  let x = [];
  let y = [];
  for (const rowIndex in result) {
    x.push(result[rowIndex]["dotw"]);
    y.push(result[rowIndex]["avg"]);
  }
  setter({ x: x, y: y });
}

export async function loadMonthlyTraffic(
  fetcher: RefObject<Fetcher>,
  setter: Dispatch<SetStateAction<any>>,
  barri: string,
) {
  const result = await getMonthlyTraffic(fetcher, barri);

  let x = [];
  let y = [];
  for (const rowIndex in result) {
    x.push(result[rowIndex]["month"]);
    y.push(result[rowIndex]["avg"]);
  }
  setter({ x: x, y: y });
}

export async function loadAverageEventImpact(
  fetcher: RefObject<Fetcher>,
  setter: Dispatch<SetStateAction<any>>,
  barri: string,
) {
  const result = await getAverageEventImpact(fetcher, barri);

  let y = [];
  let x = [];
  for (const rowIndex in result) {
    y.push(result[rowIndex]["category"]);
    x.push(result[rowIndex]["avg"]);
  }

  setter({ x: x, y: y });
}

export async function loadRainIntensityCorrelation(
  fetcher: RefObject<Fetcher>,
  setter: Dispatch<SetStateAction<any>>,
  barri: string,
) {
  const result = await getRainIntensityCorrelation(fetcher, barri);

  let x = [];
  let y = [];
  let hover = [];
  for (const rowIndex in result) {
    y.push(result[rowIndex]["intensity"]);
    x.push(result[rowIndex]["rain"]);
    hover.push(result[rowIndex]["day"]);
  }

  setter({ x: x, y: y, text: hover });
}

export async function loadWorkdayVsHoliday(
  fetcher: RefObject<Fetcher>,
  setter: Dispatch<SetStateAction<any>>,
  barri: string,
) {
  const result = await getWorkdayVsHoliday(fetcher, barri);

  let x = [];
  let y = [];
  for (const rowIndex in result) {
    y.push(result[rowIndex]["intensity"]);
    x.push(result[rowIndex]["is_holiday"]);
  }

  setter({ x: x, y: y });
}

export async function loadIntensityPerArea(
  fetcher: RefObject<Fetcher>,
  setter: Dispatch<SetStateAction<any>>,
  barri: string,
) {
  const result = await getIntensityPerArea(fetcher);

  let x = [];
  let y = [];
  let hover = [];
  for (const rowIndex in result) {
    y.push(result[rowIndex]["avg"]);
    x.push(result[rowIndex]["superficie"]);
    hover.push(result[rowIndex]["nom_barri"]);
  }

  setter({ x: x, y: y, text: hover, selectedBarri: barri });
}

export async function loadMapData(
  fetcher: RefObject<Fetcher>,
  setter: Dispatch<SetStateAction<any>>,
  barri: string,
  day: string,
) {
  const result = await getMapData(fetcher, day);

  let zScores: Record<string, number> = {};
  for (const rowIndex in result) {
    zScores[result[rowIndex]["barri"]] = result[rowIndex]["zscore"];
  }

  setter({
    zScores: zScores,
    selectedBarri: barri,
  });
}

export async function loadWeeklyIntensityDiff(
  fetcher: RefObject<Fetcher>,
  setter: Dispatch<SetStateAction<any>>,
) {
  const result = await getWeeklyIntensityDiff(fetcher);

  let x = [];
  let y = [];
  for (const rowIndex in result) {
    x.push(result[rowIndex]["dotw"]);
    y.push(result[rowIndex]["avg"]);
  }
  setter({ x: x, y: y });
}

export async function loadMonthlyIntensityDiff(
  fetcher: RefObject<Fetcher>,
  setter: Dispatch<SetStateAction<any>>,
) {
  const result = await getMonthlyIntensityDiff(fetcher);

  let x = [];
  let y = [];
  for (const rowIndex in result) {
    x.push(result[rowIndex]["month"]);
    y.push(result[rowIndex]["avg"]);
  }
  setter({ x: x, y: y });
}

export async function loadModelImportances(
  fetcher: RefObject<Fetcher>,
  setter: Dispatch<SetStateAction<any>>,
) {
  const result = await getModelImportances(fetcher);

  let x = [];
  let y = [];
  let eventImportance: number = 0;
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

export async function loadModelStats(
  fetcher: RefObject<Fetcher>,
  setter: Dispatch<SetStateAction<any>>,
) {
  const result = await getModelStats(fetcher);

  let x = [];
  let y = [];
  for (const rowIndex in result) {
    x.push(result[rowIndex]["key"]);
    y.push(result[rowIndex]["value"]);
  }
  setter({ labels: x, values: y });
}

export async function loadDailyData(
  fetcher: RefObject<Fetcher>,
  setter: Dispatch<SetStateAction<any>>,
  day: string,
) {
  const result = await getDailyData(fetcher, day);
  console.log("result");
  console.log(result);
  setter({ precipitation: result[0]["precipitation_sum"], is_holiday: result[0]["is_holiday"], 
    temperature_max: result[0]["temperature_2m_max (°C)"], temperature_min: result[0]["temperature_2m_min (°C)"],
  total_traffic: result[0]["tt"]});
}