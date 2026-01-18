"use client";
import { useState, useEffect, SetStateAction, Dispatch } from "react";
import PlotComponent from "./plot";
import {
  loadWeeklyTraffic,
  loadMonthlyTraffic,
  loadAverageEventImpact,
  loadRainIntensityCorrelation,
  loadWorkdayVsHoliday,
  loadIntensityPerArea,
} from "./load_data";
import { translations } from "./translations";

export default function App() {
  //keep day, barri and language in state
  const [day, setDay] = useState(3);
  const [barri, setBarri] = useState("el Raval");
  const [language, setLanguage] = useState("en");

  //keep loading for placeholders
  const [loading, setLoading] = useState(true);

  //keep all actual data
  const [mapData, setMapData] = useState();
  const [weeklyTraffic, setWeeklyTraffic] = useState(new Map<string, any>());
  const [monthlyTraffic, setMonthlyTraffic] = useState(new Map<string, any>());
  const [avgImpact, setAvgImpact] = useState();
  const [rainIntensityCorrelation, setRainIntensityCorrelation] = useState();
  const [workdayVsHoliday, setWorkdayVsHoliday] = useState();
  const [intensityPerArea, setIntensityPerArea] = useState();
  const [modelStats, setModelStats] = useState();
  const [weeklyIntensityDiff, setWeeklyIntensityDiff] = useState();
  const [monthlyIntensityDiff, setMonthlyIntensityDiff] = useState();

  //keep current language's translation
  const t = translations[language];

  //this will be run every time day is modified
  useEffect(() => {
    async function fetchData() {
      setLoading(true);
      try {
        //we call all SQL queries
        await Promise.all([
          loadWeeklyTraffic(setWeeklyTraffic, barri),
          loadMonthlyTraffic(setMonthlyTraffic, barri),
          loadAverageEventImpact(setAvgImpact, barri),
          loadRainIntensityCorrelation(setRainIntensityCorrelation, barri),
          loadWorkdayVsHoliday(setWorkdayVsHoliday, barri),
        ]);
      } catch (error) {
        console.error("Failed to fetch data:", error);
      }
      setLoading(false);
    }

    fetchData();
  }, [day]);

  //this will be run every time barri is modified
  useEffect(() => {
    async function fetchData() {
      setLoading(true);
      try {
        //we call all SQL queries
        await Promise.all([loadIntensityPerArea(setIntensityPerArea, barri)]);
      } catch (error) {
        console.error("Failed to fetch data:", error);
      }
      setLoading(false);
    }

    fetchData();
  }, [barri]);

  return (
    <>
      <nav>
        <img src="GoMotionShortLogo.png" alt="GoMotion Icon" />
        <p>Future dropdown</p>
      </nav>

      <main>
        <div className="title">
          <img src="GoMotionLogo.png" alt="GoMotion Logo" />
        </div>
        <p className="subtitle">Mobility in Barcelona</p>
        <h3>We are setting things up...</h3>

        <div className="plots">
          <PlotComponent t={t} isLoading={loading} type="map" data={mapData} />
        </div>

        <h2>
          {t["detAnal"]}: {barri.toUpperCase()}
        </h2>

        <div className="plots">
          <PlotComponent
            t={t}
            isLoading={loading}
            type="weekly traffic"
            data={weeklyTraffic}
          />
          <PlotComponent
            t={t}
            isLoading={loading}
            type="monthly traffic"
            data={monthlyTraffic}
          />
          <PlotComponent
            t={t}
            isLoading={loading}
            type="average event impact"
            data={avgImpact}
          />
          <PlotComponent
            t={t}
            isLoading={loading}
            type="rain/intensity correlation"
            data={rainIntensityCorrelation}
          />
          <PlotComponent
            t={t}
            isLoading={loading}
            type="workday vs holiday"
            data={workdayVsHoliday}
          />
          <PlotComponent
            t={t}
            isLoading={loading}
            type="intensity/area"
            data={intensityPerArea}
          />
        </div>

        <h2>{t["modelStatistics"]}</h2>

        <div className="plots">
          <PlotComponent
            t={t}
            isLoading={loading}
            type="model statistics"
            data={modelStats}
          />
        </div>

        <div className="plots">
          <PlotComponent
            t={t}
            isLoading={loading}
            type="weekly intensity diff"
            data={weeklyIntensityDiff}
          />
          <PlotComponent
            t={t}
            isLoading={loading}
            type="monthly intensity diff"
            data={monthlyIntensityDiff}
          />
        </div>
      </main>
    </>
  );
}
