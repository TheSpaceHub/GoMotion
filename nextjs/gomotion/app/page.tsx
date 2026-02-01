"use client";
import { useState, useEffect } from "react";
import PlotComponent from "./plot";
import Dropdown from "./dropdown";
import {
  loadMapData,
  loadWeeklyTraffic,
  loadMonthlyTraffic,
  loadAverageEventImpact,
  loadRainIntensityCorrelation,
  loadWorkdayVsHoliday,
  loadIntensityPerArea,
  loadWeeklyIntensityDiff,
  loadMonthlyIntensityDiff,
  loadModelImportances,
} from "./load_data";
import { translations } from "./translations";
import geoData from "./data/barris.json";
import dynamic from "next/dynamic";
import BarriInfo from "./barriInfo";

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
  const now = new Date();

  //keep day, barri and language in state
  const [day, setDay] = useState(formatDate(now));
  const [barri, setBarri] = useState("el Raval");
  const [language, setLanguage] = useState("en");

  //keep loading for placeholders
  const [loading, setLoading] = useState(true);

  //keep all actual data
  const [mapData, setMapData] = useState();
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
    loadWeeklyIntensityDiff(setWeeklyIntensityDiff);
    loadMonthlyIntensityDiff(setMonthlyIntensityDiff);
    loadModelImportances(setModelImportances);
  }, []);

  //this will be run every time day is modified
  useEffect(() => {
    async function fetchData() {
      setLoading(true);
      try {
        //we call all SQL queries
        await Promise.all([]);
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
        await Promise.all([
          loadIntensityPerArea(setIntensityPerArea, barri),
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
  }, [barri]);

  //this will be run every time either barri or day is modified
  useEffect(() => {
    async function fetchData() {
      setLoading(true);
      try {
        //we call all SQL queries
        await Promise.all([loadMapData(setMapData, barri, day)]);
      } catch (error) {
        console.error("Failed to fetch data:", error);
      }
      setLoading(false);
    }

    fetchData();
  }, [barri, day]);

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

        <div className="plots">
          <div className="mapContainer">
            <Heatmap
              geoData={geoData}
              zScores={mapData ? mapData["zScores"] : {}}
              barriSetter={setBarri}
            />
            <BarriInfo />
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
