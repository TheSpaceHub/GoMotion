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
  getDailyData,
  getEventData,
  getFinalPredictedDate,
} from "./server_data";
import { Fetcher } from "./page";
import { resumeToPipeableStream } from "react-dom/server";

export async function loadTableData(
  fetcher: RefObject<Fetcher | null>,
  setter: Dispatch<SetStateAction<any>>,
  day: string,
) {
  let result;

  if (
    (fetcher.current?.day as any)[day] == undefined ||
    (fetcher.current?.day as any)[day]["tableData"] == undefined
  ) {
    result = await getTableData(day);
    if ((fetcher.current?.day as any)[day] == undefined)
      (fetcher.current?.day as any)[day] = {};
    (fetcher.current?.day as any)[day]["tableData"] = result;
  } else result = (fetcher.current?.day as any)[day]["tableData"];

  setter({ rows: result });
}
export async function loadWeeklyTraffic(
  fetcher: RefObject<Fetcher | null>,
  setter: Dispatch<SetStateAction<any>>,
  barri: string,
) {
  let result;

  if (
    (fetcher.current?.barri as any)[barri] == undefined ||
    (fetcher.current?.barri as any)[barri]["weeklyTraffic"] == undefined
  ) {
    result = await getWeeklyTraffic(barri);
    if ((fetcher.current?.barri as any)[barri] == undefined)
      (fetcher.current?.barri as any)[barri] = {};
    (fetcher.current?.barri as any)[barri]["weeklyTraffic"] = result;
  } else result = (fetcher.current?.barri as any)[barri]["weeklyTraffic"];

  let x = [];
  let y = [];
  for (const rowIndex in result) {
    x.push(result[rowIndex]["dotw"]);
    y.push(result[rowIndex]["avg"]);
  }
  setter({ x: x, y: y });
}

export async function loadMonthlyTraffic(
  fetcher: RefObject<Fetcher | null>,
  setter: Dispatch<SetStateAction<any>>,
  barri: string,
) {
  let result;

  if (
    (fetcher.current?.barri as any)[barri] == undefined ||
    (fetcher.current?.barri as any)[barri]["monthlyTraffic"] == undefined
  ) {
    result = await getMonthlyTraffic(barri);
    if ((fetcher.current?.barri as any)[barri] == undefined)
      (fetcher.current?.barri as any)[barri] = {};
    (fetcher.current?.barri as any)[barri]["monthlyTraffic"] = result;
  } else result = (fetcher.current?.barri as any)[barri]["monthlyTraffic"];

  let x = [];
  let y = [];
  for (const rowIndex in result) {
    x.push(result[rowIndex]["month"]);
    y.push(result[rowIndex]["avg"]);
  }
  setter({ x: x, y: y });
}

export async function loadAverageEventImpact(
  fetcher: RefObject<Fetcher | null>,
  setter: Dispatch<SetStateAction<any>>,
  barri: string,
) {
  let result;

  if (
    (fetcher.current?.barri as any)[barri] == undefined ||
    (fetcher.current?.barri as any)[barri]["averageEventImpact"] == undefined
  ) {
    result = await getAverageEventImpact(barri);
    if ((fetcher.current?.barri as any)[barri] == undefined)
      (fetcher.current?.barri as any)[barri] = {};
    (fetcher.current?.barri as any)[barri]["averageEventImpact"] = result;
  } else result = (fetcher.current?.barri as any)[barri]["averageEventImpact"];

  let y = [];
  let x = [];
  for (const rowIndex in result) {
    y.push(result[rowIndex]["category"]);
    x.push(result[rowIndex]["avg"]);
  }

  setter({ x: x, y: y });
}

export async function loadRainIntensityCorrelation(
  fetcher: RefObject<Fetcher | null>,
  setter: Dispatch<SetStateAction<any>>,
  barri: string,
) {
  let result;

  if (
    (fetcher.current?.barri as any)[barri] == undefined ||
    (fetcher.current?.barri as any)[barri]["rainIntensityCorrelation"] ==
      undefined
  ) {
    result = await getRainIntensityCorrelation(barri);
    if ((fetcher.current?.barri as any)[barri] == undefined)
      (fetcher.current?.barri as any)[barri] = {};
    (fetcher.current?.barri as any)[barri]["rainIntensityCorrelation"] = result;
  } else
    result = (fetcher.current?.barri as any)[barri]["rainIntensityCorrelation"];

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
  fetcher: RefObject<Fetcher | null>,
  setter: Dispatch<SetStateAction<any>>,
  barri: string,
) {
  let result;

  if (
    (fetcher.current?.barri as any)[barri] == undefined ||
    (fetcher.current?.barri as any)[barri]["workdayVsHoliday"] == undefined
  ) {
    result = await getWorkdayVsHoliday(barri);
    if ((fetcher.current?.barri as any)[barri] == undefined)
      (fetcher.current?.barri as any)[barri] = {};
    (fetcher.current?.barri as any)[barri]["workdayVsHoliday"] = result;
  } else result = (fetcher.current?.barri as any)[barri]["workdayVsHoliday"];

  let x = [];
  let y = [];
  for (const rowIndex in result) {
    y.push(result[rowIndex]["intensity"]);
    x.push(result[rowIndex]["is_holiday"]);
  }

  setter({ x: x, y: y });
}

export async function loadIntensityPerArea(
  fetcher: RefObject<Fetcher | null>,
  setter: Dispatch<SetStateAction<any>>,
  barri: string,
) {
  //will get stored in general instead of barri
  let result;
  if ((fetcher.current?.general as any)["intensityPerArea"] == undefined) {
    result = await getIntensityPerArea();
    (fetcher.current?.general as any)["intensityPerArea"] = result;
  } else result = (fetcher.current?.general as any)["intensityPerArea"];

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
  fetcher: RefObject<Fetcher | null>,
  setter: Dispatch<SetStateAction<any>>,
  barri: string,
  day: string,
) {
  let result;
  if (
    (fetcher.current?.day as any)[day] == undefined ||
    (fetcher.current?.day as any)[day]["mapData"] == undefined
  ) {
    result = await getMapData(day);
    if ((fetcher.current?.day as any)[day] == undefined)
      (fetcher.current?.day as any)[day] = {};
    (fetcher.current?.day as any)[day]["mapData"] = result;
  } else result = (fetcher.current?.day as any)[day]["mapData"];

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
  fetcher: RefObject<Fetcher | null>,
  setter: Dispatch<SetStateAction<any>>,
) {
  let result;
  if ((fetcher.current?.general as any).weekly == undefined) {
    result = await getWeeklyIntensityDiff();
    (fetcher.current?.general as any).weekly = result;
  } else result = (fetcher.current?.general as any).weekly;

  let x = [];
  let y = [];
  for (const rowIndex in result) {
    x.push(result[rowIndex]["dotw"]);
    y.push(result[rowIndex]["avg"]);
  }
  setter({ x: x, y: y });
}

export async function loadMonthlyIntensityDiff(
  fetcher: RefObject<Fetcher | null>,
  setter: Dispatch<SetStateAction<any>>,
) {
  let result;
  if ((fetcher.current?.general as any).monthly == undefined) {
    result = await getMonthlyIntensityDiff();
    (fetcher.current?.general as any).monthly = result;
  } else result = (fetcher.current?.general as any).monthly;

  let x = [];
  let y = [];
  for (const rowIndex in result) {
    x.push(result[rowIndex]["month"]);
    y.push(result[rowIndex]["avg"]);
  }
  setter({ x: x, y: y });
}

export async function loadModelImportances(
  fetcher: RefObject<Fetcher | null>,
  setter: Dispatch<SetStateAction<any>>,
) {
  let result;
  if ((fetcher.current?.model as any).importances == undefined) {
    result = await getModelImportances();
    (fetcher.current?.model as any).importances = result;
  } else result = (fetcher.current?.model as any).importances;

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
  fetcher: RefObject<Fetcher | null>,
  setter: Dispatch<SetStateAction<any>>,
) {
  let result;
  if ((fetcher.current?.model as any).stats == undefined) {
    result = await getModelStats();
    (fetcher.current?.model as any).stats = result;
  } else result = (fetcher.current?.model as any).stats;

  let x = [];
  let y = [];
  for (const rowIndex in result) {
    x.push(result[rowIndex]["key"]);
    y.push(result[rowIndex]["value"]);
  }
  setter({ labels: x, values: y });
}

export async function loadDailyData(
  fetcher: RefObject<Fetcher | null>,
  setter: Dispatch<SetStateAction<any>>,
  day: string,
) {
  let result;

  if (
    (fetcher.current?.day as any)[day] == undefined ||
    (fetcher.current?.day as any)[day]["dailyData"] == undefined
  ) {
    result = await getDailyData(day);
    if ((fetcher.current?.day as any)[day] == undefined)
      (fetcher.current?.day as any)[day] = {};
    (fetcher.current?.day as any)[day]["dailyData"] = result;
  } else {
    result = (fetcher.current?.day as any)[day]["dailyData"];
  }

  setter({
    precipitation: result[0]["precipitation_sum"],
    is_holiday: result[0]["is_holiday"],
    temperature_max: result[0]["temperature_2m_max"],
    temperature_min: result[0]["temperature_2m_min"],
    total_traffic: result[0]["tt"],
  });
}

export async function loadEventData(
  fetcher: RefObject<Fetcher | null>,
  setter: Dispatch<SetStateAction<any>>,
  day: string,
) {
  let result;

  if (
    (fetcher.current?.day as any)[day] == undefined ||
    (fetcher.current?.day as any)[day]["eventData"] == undefined
  ) {
    result = await getEventData(day);
    if ((fetcher.current?.day as any)[day] == undefined)
      (fetcher.current?.day as any)[day] = {};
    (fetcher.current?.day as any)[day]["eventData"] = result;
  } else {
    result = (fetcher.current?.day as any)[day]["eventData"];
  }

  let descriptions = [];
  let categories = [];
  let impacts = [];
  let barris = [];
  for (const rowIndex in result) {
    descriptions.push(result[rowIndex]["description"]);
    categories.push(result[rowIndex]["categories"]);
    impacts.push(result[rowIndex]["impacts"]);
    barris.push(result[rowIndex]["barris"]);
  }
  setter({
    descriptions: descriptions,
    categories: categories,
    impacts: impacts,
    barris: barris,
  });
}

export async function loadFinalPredictedDate(
  fetcher: RefObject<Fetcher | null>,
  setter: Dispatch<SetStateAction<any>>,
) {
  const result = await getFinalPredictedDate();
  const finalDate = result[0].value;
  setter(finalDate);
}
