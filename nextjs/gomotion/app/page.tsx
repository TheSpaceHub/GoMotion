"use client";
import { useState, useEffect, useRef } from "react";
import PlotComponent from "./plot";
import Dropdown from "./dropdown";
import {
  loadMapData,
  loadTableData,
  loadWeeklyTraffic,
  loadMonthlyTraffic,
  loadAverageEventImpact,
  loadRainIntensityCorrelation,
  loadWorkdayVsHoliday,
  loadIntensityPerArea,
  loadWeeklyIntensityDiff,
  loadMonthlyIntensityDiff,
  loadModelImportances,
  loadModelStats,
  loadDailyData,
  loadEventData,
  loadFinalPredictedDate,
  loadDailyDataForMonth,
  loadEventDataForMonth,
  loadTableDataForMonth,
  loadMapDataForMonth,
} from "./load_data";
import { translations } from "./translations";
import geoData from "./data/barris.json";
import dynamic from "next/dynamic";
import BarriInfo from "./barriInfo";

export class Fetcher {
  //storage objects
  barri = {};
  day = {};
  model = {};
  general = {};

  prefetchedMonths = {"dailyData": {}, "eventData": {}, "mapData": {}, "tableData": {}};
  constructor() {
    /*data in the fetcher will be classified by
    - barri
      - general data for each barri
    - day
      - barri
        - barri/day data
      - daily data
    - model
      - all model data
    - general barri data
    */
  }
}

const formatDate = (date: Date) => {
  const year = date.getFullYear();
  //i guess months are 0-indexed
  const month = String(date.getMonth() + 1).padStart(2, "0");
  const day = String(date.getDate()).padStart(2, "0");

  return `${year}-${month}-${day}`;
};

const Heatmap = dynamic(() => import("./heatmap"), {
  ssr: false,
});

export default function App() {
  //define fetcher for user
  const fetcher = useRef<Fetcher | null>(null);
  if (fetcher.current === null) {
    fetcher.current = new Fetcher();
  }

  //keep day, barri and language in state
  const [day, setDay] = useState(formatDate(new Date()));
  const [barri, setBarri] = useState("el Raval");
  const [language, setLanguage] = useState("en");

  //keep loading for placeholders
  const [loading, setLoading] = useState(0);

  //keep all actual data
  const [mapData, setMapData] = useState();
  const [tableData, setTableData] = useState({ rows: [] });
  const [dailyData, setDailyData] = useState({
    precipitation: null,
    is_holiday: null,
    temperature_max: null,
    total_traffic: null,
    temperature_min: null,
  });
  const [eventData, setEventData] = useState({
    barris: null,
    impacts: null,
    categories: null,
    description: null,
  });
  const [weeklyTraffic, setWeeklyTraffic] = useState();
  const [monthlyTraffic, setMonthlyTraffic] = useState();
  const [avgImpact, setAvgImpact] = useState();
  const [rainIntensityCorrelation, setRainIntensityCorrelation] = useState();
  const [workdayVsHoliday, setWorkdayVsHoliday] = useState();
  const [intensityPerArea, setIntensityPerArea] = useState();
  const [modelImportances, setModelImportances] = useState();
  const [modelStats, setModelStats] = useState();
  const [weeklyIntensityDiff, setWeeklyIntensityDiff] = useState();
  const [monthlyIntensityDiff, setMonthlyIntensityDiff] = useState();

  //keep current language's translation
  const t = translations[language];

  //we load static data
  useEffect(() => {
    loadWeeklyIntensityDiff(fetcher, setWeeklyIntensityDiff);
    loadMonthlyIntensityDiff(fetcher, setMonthlyIntensityDiff);
    loadModelImportances(fetcher, setModelImportances);
    loadModelStats(fetcher, setModelStats);
  }, []);

  //this will be run every time day is modified
  useEffect(() => {
    async function fetchData() {
      setLoading((prev) => prev + 1);
      try {
        //we call all SQL queries
        await Promise.all([
          loadTableData(fetcher, setTableData, day),
          loadDailyData(fetcher, setDailyData, day),
          loadEventData(fetcher, setEventData, day),
        ]);

        loadTableDataForMonth(fetcher, day);
        loadDailyDataForMonth(fetcher, day);
        loadEventDataForMonth(fetcher, day);
      } catch (error) {
        console.error("Failed to fetch data:", error);
      }
      setLoading((prev) => prev - 1);
    }

    fetchData();
  }, [day]);

  //this will be run every time barri is modified
  useEffect(() => {
    async function fetchData() {
      setLoading((prev) => prev + 1);
      try {
        //we call all SQL queries
        await Promise.all([
          loadWeeklyTraffic(fetcher, setWeeklyTraffic, barri),
          loadMonthlyTraffic(fetcher, setMonthlyTraffic, barri),
          loadAverageEventImpact(fetcher, setAvgImpact, barri),
          loadRainIntensityCorrelation(
            fetcher,
            setRainIntensityCorrelation,
            barri,
          ),
          loadWorkdayVsHoliday(fetcher, setWorkdayVsHoliday, barri),
          loadIntensityPerArea(fetcher, setIntensityPerArea, barri),
        ]);
      } catch (error) {
        console.error("Failed to fetch data:", error);
      }
      setLoading((prev) => prev - 1);
    }

    fetchData();
  }, [barri]);

  //this will be run every time either barri or day is modified
  useEffect(() => {
    async function fetchData() {
      setLoading((prev) => prev + 1);
      try {
        //we call all SQL queries
        await Promise.all([loadMapData(fetcher, setMapData, barri, day)]);

        loadMapDataForMonth(fetcher, day);
      } catch (error) {
        console.error("Failed to fetch data:", error);
      }
      setLoading((prev) => prev - 1);
    }

    fetchData();
  }, [barri, day]);

  const rawImpacts = (eventData as any).impacts || [];
  const validEvents = rawImpacts
    .map((impact: any, i: number) => ({
      impact: impact,
      category: (eventData as any).categories?.[i] || "-",
      barri: (eventData as any).barris?.[i] || "-",
      description: (eventData as any).description?.[i] || "-",
    }))
    .filter((e: any) => e.impact !== null);

  // Helper to determine badge class
  const getImpactClass = (val: number) => {
    if (val > 0.7) return "impact-badge impact-high";
    if (val > 0.4) return "impact-badge impact-med";
    return "impact-badge impact-low";
  };

  return (
    <>
      <nav>
        <img src="GoMotionShortLogo.png" alt="GoMotion Icon" />
        <Dropdown
          options={["en", "es"]}
          optoval={{ en: "English", es: "Spanish" }}
          value={language}
          onChange={setLanguage}
        />
      </nav>

      <main>
        <div className="title">
          <img src="GoMotionLogo.png" alt="GoMotion Logo" />
        </div>
        <p className="subtitle">Mobility in Barcelona</p>

        <h2>{t.dailyAnal}</h2>

        <div className="dailyMetrics">
          <div className="Metric">
            <h3 className="dailyTitle">{t.dailySummary["totalTraffic"]}</h3>
            <h1 className="dailyMetric">
              {(dailyData as any)["total_traffic"] != null
                ? Math.round((dailyData as any)["total_traffic"])
                : "..."}
            </h1>
          </div>

          <div className="Metric">
            <h3 className="dailyTitle">{t.dailySummary["eventCount"]}</h3>
            <h1 className="dailyMetric">
              {(eventData as any).impacts?.length ?? "..."}
            </h1>
          </div>

          <div className="Metric">
            <h3 className="dailyTitle">{t.dailySummary["holiday"]}</h3>

            <h1 className="dailyMetric">
              {dailyData.is_holiday != null
                ? dailyData["is_holiday"] == "1"
                  ? t["true"]
                  : t["false"]
                : "..."}
            </h1>
          </div>

          <div className="Metric">
            <h3 className="dailyTitle">{t.dailySummary["temp"]}</h3>
            <h1 className="dailyMetric">
              {dailyData.temperature_min != null
                ? dailyData["temperature_min"] +
                  "ºC/" +
                  dailyData["temperature_max"] +
                  "ºC"
                : "..."}
            </h1>
          </div>

          <div className="Metric">
            <h3 className="dailyTitle">{t.dailySummary["precipitation"]}</h3>

            <h1 className="dailyMetric">
              {dailyData["precipitation"] != null
                ? dailyData["precipitation"] + "mm"
                : "..."}
            </h1>
          </div>
        </div>

        <div className="events-container">
          <details className="events-details" open={validEvents.length > 0}>
            <summary>
              <span>Events Analysis</span>
              <span className="events-count-badge">
                {validEvents.length} Events Found
              </span>
            </summary>

            <div className="events-table-wrapper">
              {validEvents.length > 0 ? (
                <table>
                  <thead>
                    <tr>
                      <th className="text-left">Category</th>
                      <th className="text-left">Barri</th>
                      <th className="text-left">Impact</th>
                      <th className="text-left">Description</th>
                    </tr>
                  </thead>
                  <tbody>
                    {validEvents.map((event: any, i: number) => (
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
                    ))}
                  </tbody>
                </table>
              ) : (
                <div className="no-events-msg">
                  No significant events recorded for this date.
                </div>
              )}
            </div>
          </details>
        </div>

        <div className="plots">
          <div className="mapContainer">
            <Heatmap
              geoData={geoData}
              zScores={mapData ? mapData["zScores"] : {}}
              barriSetter={setBarri}
            />

            <BarriInfo
              data={tableData}
              day={day}
              setter={setDay}
              fetcher={fetcher}
            />
          </div>
        </div>

        <h2>
          {t["detAnal"]}: {barri.toUpperCase()}
        </h2>

        <div className="plots">
          <div className="plot">
            <PlotComponent
              t={t}
              isLoading={loading}
              type="weekly traffic"
              data={weeklyTraffic}
            />
          </div>

          <div className="plot">
            <PlotComponent
              t={t}
              isLoading={loading}
              type="monthly traffic"
              data={monthlyTraffic}
            />
          </div>

          <div className="plot">
            <PlotComponent
              t={t}
              isLoading={loading}
              type="average event impact"
              data={avgImpact}
            />
          </div>

          <div className="plot">
            <PlotComponent
              t={t}
              isLoading={loading}
              type="rain/intensity correlation"
              data={rainIntensityCorrelation}
            />
          </div>

          <div className="plot">
            <PlotComponent
              t={t}
              isLoading={loading}
              type="workday vs holiday"
              data={workdayVsHoliday}
            />
          </div>

          <div className="plot">
            <PlotComponent
              t={t}
              isLoading={loading}
              type="intensity/area"
              data={intensityPerArea}
            />
          </div>
        </div>

        <h2>{t["modelStatistics"]}</h2>

        <div className="modelPlots">
          <div className="modelImportances">
            <PlotComponent
              t={t}
              isLoading={loading}
              type="model importances"
              data={modelImportances}
            />
          </div>

          <div className="modelStats">
            <PlotComponent
              t={t}
              isLoading={loading}
              type="model stats"
              data={modelStats}
            />
          </div>
        </div>

        <h2>{t["globalStats"]}</h2>

        <div className="plots">
          <div className="plot">
            <PlotComponent
              t={t}
              isLoading={loading}
              type="weekly intensity diff"
              data={weeklyIntensityDiff}
            />
          </div>
          <div className="plot">
            <PlotComponent
              t={t}
              isLoading={loading}
              type="monthly intensity diff"
              data={monthlyIntensityDiff}
            />
          </div>
        </div>
      </main>
    </>
  );
}
