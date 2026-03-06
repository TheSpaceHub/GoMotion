"use client";
import { useState, useEffect } from "react";
import Dropdown from "./dropdown";
import { useDashboardContext } from "./context/DashboardContext";
import {
  loadMapData,
  loadTableData,
  loadDailyData,
  loadEventData,
  loadDailyDataForMonth,
  loadEventDataForMonth,
  loadTableDataForMonth,
  loadMapDataForMonth,
} from "./load_data";
import { translations } from "./translations";
import geoData from "./data/barris.json";
import dynamic from "next/dynamic";
import BarriInfo from "./barriInfo";
import EventDetails from "./eventDetails";

export class Fetcher {
  //storage objects
  barri = {};
  day = {};
  model = {};
  general = {};

  prefetchedMonths = {
    dailyData: {},
    eventData: {},
    mapData: {},
    tableData: {},
  };
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

const Heatmap = dynamic(() => import("./heatmap"), {
  ssr: false,
});

export default function DashboardOverview() {
  const { day, setDay, barri, setBarri, language, fetcher } =
    useDashboardContext();

  const [loading, setLoading] = useState(0);

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

  const t = translations[language];

  // Load data logic specific to the Dashboard Home
  useEffect(() => {
    async function fetchData() {
      setLoading((prev) => prev + 1);
      try {
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

  return (
    <>
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
            <span>{t.eventAnal}</span>
            <span className="events-count-badge">
              {validEvents.length}{" "}
              {validEvents.length == 1 ? t.singleEventFound : t.eventsFound}
            </span>
          </summary>

          <EventDetails validEvents={validEvents} t={t} />
        </details>
      </div>

      <div className="plots">
        <div className="mapContainer">
          <Heatmap
            geoData={geoData}
            zScores={mapData ? mapData["zScores"] : {}}
            barriSetter={setBarri}
            selectedBarri={barri}
          />

          <BarriInfo
            data={tableData}
            day={day}
            setter={setDay}
            fetcher={fetcher}
            t={t}
          />
        </div>
      </div>
    </>
  );
}
