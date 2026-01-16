"use client";
import { useState, useEffect, SetStateAction, Dispatch } from "react";
import dynamic from "next/dynamic";
import PlotComponent from "./plot";
import {
  loadWeeklyTraffic,
  loadMonthlyTraffic,
  loadAverageEventImpact,
} from "./load_data";
import { translations } from "./translations";

const Plot = dynamic(() => import("react-plotly.js"), {
  ssr: false,
  loading: () => <p>Loading Map...</p>,
});

/*function Heatmap(geojson: string, plotData: { locations: any; zscores: any; hoverText: any })
{
  return (
    <Plot
      style={{ width: "100%", height: "600px" }}
      useResizeHandler={true}
      data={[
        {
          type: "choroplethmapbox", // Equivalent to px.choropleth_map
          geojson: geojson,         // Your 'gdf.geometry'
          locations: plotData.locations,
          z: plotData.zscores,
          
          // Match GeoJSON ID field (check your geojson property name!)
          featureidkey: "properties.barri", 
          
          colorscale: "Plasma",
          zmin: -2.5,
          zmax: 2.5,
          marker: { opacity: 0.75 },
          hoverinfo: "text",
          text: plotData.hoverText,
          colorbar: {
            title: "Intensidad",
            tickvals: [-2.5, 0, 2.5],
            ticktext: ["Baja", "Media", "Alta"],
            len: 0.5,
            thickness: 15,
            x: 0.01,
            xanchor: "left",
            bgcolor: "rgba(255,255,255,0.9)"
          }
        }
      ]}
      layout={{
        mapbox: {
          style: "carto-positron", // Equivalent to map_style="carto-positron"
          center: { lat: 41.395, lon: 2.17 },
          zoom: 11.1
        },
        margin: { r: 0, t: 0, l: 0, b: 0 },
        height: 600,
        // Plotly usually needs a Mapbox token for some styles, 
        // but carto-positron often works without one.
        // mapbox: { accesstoken: "pk.your_token_here" } 
      }}
      config={{ displayModeBar: false }}
    />
  )
}*/

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
        ]);
      } catch (error) {
        console.error("Failed to fetch data:", error);
      }
      setLoading(false);
    }

    fetchData();
  }, [day]);

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
          {t["det_anal"]}: {barri.toUpperCase()}
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
